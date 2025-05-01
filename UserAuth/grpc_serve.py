import sys
import os
sys.path.append(os.getcwd())
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UserAuth.settings')
django.setup()

from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned, PermissionDenied
from grpc_interceptor import exceptions as grpc_exceptions
from grpc_interceptor.exceptions import FailedPrecondition, Unauthenticated, GrpcException
from django.db import DatabaseError
from django.db import IntegrityError
from django.db import transaction

import grpc
from concurrent import futures
import os
from datetime import datetime
from decimal import Decimal as DecimalType
from dotenv import load_dotenv
from google.protobuf import timestamp_pb2,empty_pb2

import firebase_main

from Proto import user_auth_pb2
from Proto import user_auth_pb2_grpc 
from Proto.user_auth_pb2_grpc import AuthServiceServicer, add_AuthServiceServicer_to_server

from User.models import User, Store, address

from utils.logger import Logger
from utils.check_access import check_access

logger = Logger("GRPC_Service")

def handle_error(func):
    def wrapper(self, request, context):
        try:
            return func(self, request, context)
        except User.DoesNotExist:
            logger.warning(f"Product Not Found: {getattr(request, 'product_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, "Product Not Found")

        except Store.DoesNotExist:
            logger.error(f"Category Not Found: {getattr(request, 'category_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, "Category Not Found")

        except ObjectDoesNotExist:
            logger.error("Requested object does not exist")
            context.abort(grpc.StatusCode.NOT_FOUND, "Requested Object Not Found")

        except MultipleObjectsReturned:
            logger.error(f"Multiple objects found for request")
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Multiple matching objects found")

        except ValidationError as e:
            logger.error(f"Validation Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Validation Error: {str(e)}")

        except IntegrityError as e:
            logger.error(f"Integrity Error: {str(e)}")
            context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Object Already Exists")

        except DatabaseError as e:
            logger.error(f"Database Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INTERNAL, "Database Error")

        except PermissionDenied as e:
            logger.warning(f"Permission Denied: {str(e)}",e)
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission Denied")

        except ValueError as e:
            logger.error(f"Invalid Value: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Invalid Value: {str(e)}")

        except TypeError as e:
            logger.error(f"Type Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Type Error: {str(e)}")

        except TimeoutError as e:
            logger.error(f"Timeout Error: {str(e)}")
            context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "Request timed out")
            
        except grpc.RpcError as e:
            logger.error(f"RPC Error: {str(e)}")
            # Don't re-abort as this is likely a propagated error
            raise

        except FailedPrecondition as e:
            context.abort(e.status_code,e.details)

        except Unauthenticated as e:
            context.abort(grpc.StatusCode.PERMISSION_DENIED,f"User Not Allowed To make this Call")
        
        except GrpcException as e:
            context.abort(e.status_code,e.details)    
        
        except AttributeError as e:
            logger.error(f"Attribute Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Attribute Error: {str(e)}")
            
        except transaction.TransactionManagementError as e:
            logger.error(f"Transaction Error: {str(e)}")
            context.abort(grpc.StatusCode.ABORTED, f"Transaction Error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INTERNAL, "Internal Server Error")
    return wrapper

class UserAuthService(AuthServiceServicer):
    def __init__(self):
        self.firebase_auth_manager = firebase_main.FireBaseAuthManager()

    @handle_error
    def CreateUser(self, request, context):
        logger.info(f"Creating new user with firebase_uid: {request.firebase_uid}")
        firebase_uid = request.firebase_uid
        token = request.token

        logger.debug(f"Verifying token for firebase_uid: {firebase_uid}")
        firebase_uid_from_token = self.firebase_auth_manager.verify_user_token(id_token=token)
        user = self.firebase_auth_manager.get_user_by_UID(firebase_uid_from_token)
        if firebase_uid != firebase_uid_from_token:
            logger.error(f"Firebase UID mismatch: {firebase_uid} != {firebase_uid_from_token}")
            raise grpc.RpcError(grpc.StatusCode.PERMISSION_DENIED, "Firebase UID mismatch")

        logger.debug("Starting database transaction for user creation")
        with transaction.atomic():
            try:
                user = User.objects.create(
                    firebase_uid=firebase_uid,
                    email=user.email,
                    phone=user.phone_number if user.phone_number else None,
                )
                logger.info(f"User created successfully with UUID: {user.user_uuid}")

                logger.debug(f"Setting custom claims for firebase_uid: {firebase_uid}")
                self.firebase_auth_manager.set_custom_claims(firebase_uid, {"user_uuid": str(user.user_uuid),"role":"owner"})
                logger.info("Custom claims set successfully")
                return empty_pb2.Empty()

            except IntegrityError as e:
                user = User.objects.get(firebase_uid=firebase_uid)
                logger.warning(f"User already exists with firebase_uid: {firebase_uid}")
                self.firebase_auth_manager.set_custom_claims(firebase_uid, {"user_uuid": str(user.user_uuid)})
                logger.info("Custom claims set successfully for existing user")

                return empty_pb2.Empty()

    @handle_error 
    def VerifyToken(self, request, context):
        logger.info("Processing token verification request")
        token = request.token

        logger.debug("Verifying user token with Firebase")
        firebase_id = self.firebase_auth_manager.verify_user_token(token)
        logger.debug(f"Token verified for firebase_id: {firebase_id}")

        logger.debug(f"Fetching user details for firebase_id: {firebase_id}")
        user = self.firebase_auth_manager.get_user_by_UID(firebase_id)

        if user is not None:
            logger.info(f"Token verification successful for firebase_id: {firebase_id}")
            return empty_pb2.Empty()
        else:
            logger.error(f"Invalid token: User not found for firebase_id: {firebase_id}")
            raise Unauthenticated("User token Could not be verified")

    @handle_error
    def CreateStore(self, request, context):
        user_uuid = request.user_uuid
        store_name = request.store_name
        user =  User.objects.get(user_uuid = user_uuid)

        with transaction.atomic():

            store = Store.objects.create(
                user = user,
                store_name = store_name,
                gst_number =  request.gst_number
            )
            


def serve():
    logger.info("Initializing gRPC server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    logger.debug("Adding services to server")
    add_AuthServiceServicer_to_server(UserAuthService(), server)
    
    grpc_port = os.getenv('GRPC_SERVER_PORT', '50051')
    logger.debug(f"Using port: {grpc_port}")
    
    server.add_insecure_port(f'[::]:{grpc_port}')
    server.start()
    
    logger.info(f"gRPC server is running on port {grpc_port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()