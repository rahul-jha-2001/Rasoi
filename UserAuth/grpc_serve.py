import sys
import os
import functools
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

from User.models import User, Store ,Address

from utils.logger import Logger
from utils.check_access import check_access

logger = Logger("GRPC_Service")

# def handle_error(func):
#     def wrapper(self, request, context):
#         try:
#             return func(self, request, context)
#         except User.DoesNotExist:
#             logger.warning(f"Product Not Found: {getattr(request, 'product_uuid', '')}")
#             context.abort(grpc.StatusCode.NOT_FOUND, "Product Not Found")

#         except Store.DoesNotExist:
#             logger.error(f"Category Not Found: {getattr(request, 'category_uuid', '')}")
#             context.abort(grpc.StatusCode.NOT_FOUND, "Category Not Found")

#         except ObjectDoesNotExist:
#             logger.error("Requested object does not exist")
#             context.abort(grpc.StatusCode.NOT_FOUND, "Requested Object Not Found")

#         except MultipleObjectsReturned:
#             logger.error(f"Multiple objects found for request")
#             context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Multiple matching objects found")

#         except ValidationError as e:
#             logger.error(f"Validation Error: {str(e)}")
#             context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Validation Error: {str(e)}")

#         except IntegrityError as e:
#             logger.error(f"Integrity Error: {str(e)}")
#             context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Object Already Exists")

#         except DatabaseError as e:
#             logger.error(f"Database Error: {str(e)}",e)
#             context.abort(grpc.StatusCode.INTERNAL, "Database Error")

#         except PermissionDenied as e:
#             logger.warning(f"Permission Denied: {str(e)}",e)
#             context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission Denied")

#         except ValueError as e:
#             logger.error(f"Invalid Value: {str(e)}")
#             context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Invalid Value: {str(e)}")

#         except TypeError as e:
#             logger.error(f"Type Error: {str(e)}",e)
#             context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Type Error: {str(e)}")

#         except TimeoutError as e:
#             logger.error(f"Timeout Error: {str(e)}")
#             context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "Request timed out")
            
#         except grpc.RpcError as e:
#             logger.error(f"RPC Error: {str(e)}")
#             # Don't re-abort as this is likely a propagated error
#             raise

#         except FailedPrecondition as e:
#             context.abort(e.status_code,e.details)

#         except Unauthenticated as e:
#             context.abort(grpc.StatusCode.PERMISSION_DENIED,f"Unauthenticated: {e.details}")
        
#         except GrpcException as e:
#             context.abort(e.status_code,e.details)    
        
#         except AttributeError as e:
#             logger.error(f"Attribute Error: {str(e)}",e)
#             context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Attribute Error: {str(e)}")
            
#         except transaction.TransactionManagementError as e:
#             logger.error(f"Transaction Error: {str(e)}")
#             context.abort(grpc.StatusCode.ABORTED, f"Transaction Error: {str(e)}")

#         except Exception as e:
#             logger.error(f"Unexpected Error: {str(e)}",e)
#             context.abort(grpc.StatusCode.INTERNAL, "Internal Server Error")
#     return wrapper


def handle_error(func):
    @functools.wraps(func)
    def wrapper(self, request, context):
        logger.info(f"→ Entering {func.__name__} with request={request!r}")
        try:
            result = func(self, request, context)
            logger.info(f"← {func.__name__} succeeded")
            return result

        # 404 errors
        except User.DoesNotExist as e:
            logger.warning(
                "User not found",
                exc_info=True,
                extra={"firebase_uid": getattr(request, "firebase_uid", None)}
            )
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        except Store.DoesNotExist as e:
            logger.warning(
                "Store not found",
                exc_info=True,
                extra={"store_uuid": getattr(request, "store_uuid", None)}
            )
            context.abort(grpc.StatusCode.NOT_FOUND, "Store not found")

        except ObjectDoesNotExist as e:
            logger.error("Requested object does not exist", exc_info=True)
            context.abort(grpc.StatusCode.NOT_FOUND, "Requested object not found")

        # multiple matches
        except MultipleObjectsReturned as e:
            logger.error("Multiple objects found for request", exc_info=True)
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                "Multiple matching objects found"
            )

        # validation problems
        except ValidationError as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"Validation error: {e}"
            )

        # unique-constraint / already exists
        except IntegrityError as e:
            logger.error("Integrity error (object already exists)", exc_info=True)
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "Object already exists"
            )

        # other DB issues
        except DatabaseError as e:
            logger.exception("Database error")
            context.abort(grpc.StatusCode.INTERNAL, "Database error")

        # permission from Django
        except PermissionDenied as e:
            logger.warning(f"Permission denied: {e}", exc_info=True)
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied")

        # built-in Python errors
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid argument: {e}", exc_info=True)
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        # timeout
        except TimeoutError as e:
            logger.error(f"Timeout: {e}", exc_info=True)
            context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "Request timed out")

        # pre-existing gRPC error → rethrow
        except grpc.RpcError:
            logger.debug("Propagating existing RpcError", exc_info=True)
            raise

        # custom gRPC-style exceptions
        except FailedPrecondition as e:
            logger.error(f"Failed precondition: {e}", exc_info=True)
            context.abort(e.status_code, e.details)

        except Unauthenticated as e:
            logger.warning(f"Unauthenticated: {e.details}", exc_info=True)
            context.abort(grpc.StatusCode.UNAUTHENTICATED, f"Unauthenticated: {e.details}")

        except GrpcException as e:
            logger.error(f"gRPC exception: {e}", exc_info=True)
            context.abort(e.status_code, e.details)

        # transaction errors
        except transaction.TransactionManagementError as e:
            logger.error(f"Transaction management error: {e}", exc_info=True)
            context.abort(grpc.StatusCode.ABORTED, f"Transaction error: {e}")

        # catch-all
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")

    return wrapper


class UserAuthService(AuthServiceServicer):
    def __init__(self):
        self.firebase_auth_manager = firebase_main.FireBaseAuthManager
    
    def _address_to_proto(self, address):
        return user_auth_pb2.AddressResponse(
            address_uuid=str(address.address_uuid),
            address_line_1=address.address_line_1,
            address_line_2=address.address_line_2,
            city=address.city,
            state=address.state,
            country=address.country,
            pincode=address.pincode
        )

    def _store_to_proto(self, store):
        return user_auth_pb2.StoreResponse(
            store_uuid=str(store.store_uuid),
            name=store.name,
            gst_number=store.gst_number,
            address=self._address_to_proto(store.address) if store.address else None,
            user_uuid=str(store.user.user_uuid)
        )

    @handle_error
    def CreateUser(self, request, context):
        firebase_uid = request.firebase_uid
        token = request.token.token

        firebase_uid_from_token = self.firebase_auth_manager.verify_user_token(token)

        if firebase_uid != firebase_uid_from_token:
            logger.error(f"Firebase UID mismatch: {firebase_uid} != {firebase_uid_from_token}")
            raise grpc.RpcError(grpc.StatusCode.PERMISSION_DENIED, "Firebase UID mismatch")
        with transaction.atomic():
            user = User.objects.create(
                firebase_uid=firebase_uid,
                email=request.email,
                phone=request.phone
            )

            self.firebase_auth_manager.set_custom_user_claims(firebase_uid, {"user_uuid": str(user.user_uuid)})
            
            return empty_pb2.Empty()

    @handle_error 
    def VerifyToken(self,request,context):
        token =  request.token

        firebase_id = self.firebase_auth_manager.verify_user_token(token)
        user =  self.firebase_auth_manager.get_user_by_UID(firebase_id)

        if user != None:
            return empty_pb2.Empty()
        else:
            logger.error("Invalid token User not Found")
            raise Unauthenticated("User token Could not be verified")

        @handle_error
    def CreateUser(self, request, context):
        firebase_uid = request.firebase_uid
        token = getattr(request.token, "token", request.token)

        logger.info(f"CreateUser called for firebase_uid={firebase_uid}")
        logger.debug(f"Raw token: {token}")

        # Verify the token’s UID matches the requested UID
        firebase_uid_from_token = self.firebase_auth_manager.verify_user_token(token)
        logger.debug(f"Token verified; firebase_uid_from_token={firebase_uid_from_token}")
        if firebase_uid != firebase_uid_from_token:
            logger.warning(
                f"Firebase UID mismatch: request={firebase_uid}, token={firebase_uid_from_token}"
            )
            raise Unauthenticated("Firebase UID mismatch")

        # Create the user in the database
        with transaction.atomic():
            user = User.objects.create(
                firebase_uid=firebase_uid,
                email=request.email,
                phone=request.phone
            )
            logger.info(f"Created User record; user_uuid={user.user_uuid}")

        # Attach the new user_uuid as a custom claim
        self.firebase_auth_manager.set_custom_user_claims(
            firebase_uid,
            {"user_uuid": str(user.user_uuid)}
        )
        logger.info(f"Set custom claims for firebase_uid={firebase_uid}")

        return empty_pb2.Empty()

    @handle_error
    def VerifyToken(self, request, context):
        token = getattr(request.token, "token", request.token)

        logger.info("VerifyToken called")
        logger.debug(f"Raw token: {token}")

        # Verify the token
        firebase_id = self.firebase_auth_manager.verify_user_token(token)
        logger.debug(f"Token verified; firebase_id={firebase_id}")

        # Ensure the user exists
        user = self.firebase_auth_manager.get_user_by_UID(firebase_id)
        if not user:
            logger.warning(f"User not found for firebase_id={firebase_id}")
            raise Unauthenticated("User token could not be verified")

        logger.info(f"VerifyToken succeeded for firebase_id={firebase_id}")
        return empty_pb2.Empty()



    @handle_error
    def CreateStore(self, request, context):
        user_uuid = request.user_uuid
        store_name = request.store_name
        
        with transaction.atomic():
            try:
                user = User.objects.get(user_uuid=user_uuid)
            except User.DoesNotExist:
                logger.error(f"User with UUID {user_uuid} does not exist")
                raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, "User Not Found")

            store = Store.objects.create(
                name=store_name,
                user=user
            )
            
            return user_auth_pb2.StoreResponse(
                user_uuid=str(store.user.user_uuid),
                store = self._store_to_proto(store),)

    @handle_error
    def UpdateStore(self, request, context):
        store_uuid = request.store_uuid
        store_name = request.store_name

        with transaction.atomic():
            try:
                store = Store.objects.get(store_uuid=store_uuid)
            except Store.DoesNotExist:
                logger.error(f"Store with UUID {store_uuid} does not exist")
                raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, "Store Not Found")
            
            if request.HasField('store_name'):
                store.name = request.store_name
            if request.HasField('gst_number'):
                store.gst_number = request.gst_number
            
            store.save()

            return user_auth_pb2.StoreResponse(
                user_uuid=str(store.user.user_uuid),
                store = self._store_to_proto(store),)

    @handle_error
    def GetStore(self, request, context):
        user_uuid = request.user_uuid
        store_uuid = request.store_uuid

        with transaction.atomic():
            try:
                store = Store.objects.get(store_uuid=store_uuid)
            except Store.DoesNotExist:
                logger.error(f"Store with UUID {store_uuid} does not exist")
                raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, "Store Not Found")

        return user_auth_pb2.StoreResponse(
                user_uuid=str(store.user.user_uuid),
                store = self._store_to_proto(store),)


    @handle_error
    def GetAllStores(self, request, context):

        user_uuid = request.user_uuid
        limit = request.limit
        page = request.page

        data, next_page, prev_page = Store.objects.get_stores(user_uuid, limit, page)

        return user_auth_pb2.GetAllStoresResponse(
            stores=[self._store_to_proto(store) for store in data],
            next_page=next_page,
            prev_page=prev_page
        )
    
    @handle_error
    def DeleteStore(self, request, context):
        store_uuid = request.store_uuid

        with transaction.atomic():
            try:
                store = Store.objects.get(store_uuid=store_uuid)
                store.delete()
            except Store.DoesNotExist:
                logger.error(f"Store with UUID {store_uuid} does not exist")
                raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, "Store Not Found")

        return empty_pb2.Empty()
    
    @handle_error
    def CreateAddress(self, request, context):
        store_uuid = request.store_uuid
        address_line_1 = request.address_line_1
        address_line_2 = request.address_line_2
        city = request.city
        state = request.state
        country = request.country
        pincode = request.pincode

        with transaction.atomic():
            store = Store.objects.get(store_uuid=store_uuid)

            
            address = Address.objects.create(
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                country=country,
                pincode=pincode
            )
            store.address = address
            store.save()

            return user_auth_pb2.AddressResponse(
                store_uuid=str(store.store_uuid),
                address = self._address_to_proto(address))
    
    @handle_error
    def UpdateAddress(self, request, context):
        address_uuid = request.address_uuid
        store_uuid = request.store_uuid        


        with transaction.atomic():
            try:
                address = Address.objects.get(address_uuid=address_uuid)
            except Address.DoesNotExist:
                logger.error(f"Address with UUID {address_uuid} does not exist")
                raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, "Address Not Found")

            if request.HasField('address_line_1'):
                address.address_line_1 = request.address_line_1
            if request.HasField('address_line_2'):
                address.address_line_2 = request.address_line_2
            if request.HasField('city'):
                address.city = request.city
            if request.HasField('state'):
                address.state = request.state
            if request.HasField('country'):
                address.country = request.country
            if request.HasField('pincode'):
                address.pincode = request.pincode

            address.save()

            return user_auth_pb2.AddressResponse(
                store_uuid=str(address.store.store_uuid),
                address=self._address_to_proto(address))
    
    @handle_error
    def GetAddress(self, request, context):
        address_uuid = request.address_uuid
        store_uuid = request.store_uuid

        with transaction.atomic():
            try:
                address = Address.objects.get(address_uuid=address_uuid)
            except Address.DoesNotExist:
                logger.error(f"Address with UUID {address_uuid} does not exist")
                raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, "Address Not Found")

        return user_auth_pb2.AddressResponse(
            store_uuid=str(address.store.store_uuid),
            address=self._address_to_proto(address))
    
    @handle_error
    def DeleteAddress(self, request, context):
        address_uuid = request.address_uuid
        store_uuid = request.store_uuid

        with transaction.atomic():
            try:
                address = Address.objects.get(address_uuid=address_uuid)
                address.delete()
            except Address.DoesNotExist:
                logger.error(f"Address with UUID {address_uuid} does not exist")
                raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, "Address Not Found")

        return empty_pb2.Empty()



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add your services to the server
    add_AuthServiceServicer_to_server(UserAuthService(), server)
    
    # Get the port from environment variables
    grpc_port = os.getenv('GRPC_SERVER_PORT', '50052')
    
    # Bind the server to the specified port
    server.add_insecure_port(f'[::]:{grpc_port}')
    server.start()
    
    logger.info(f"gRPC server is running on port {grpc_port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()