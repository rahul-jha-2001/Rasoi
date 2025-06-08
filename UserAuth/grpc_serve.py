import sys
import os
import functools
import json

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
from Proto.user_auth_pb2 import store,address,user
from User.models import User, Store ,Address, StoreRole,Customer

from utils.logger import Logger
from utils.check_access import check_access
from utils.jwt_manager import JWTManager

from firebase_admin.auth import UserRecord, UserNotFoundError, InvalidIdTokenError
from firebase_admin.auth import ExpiredIdTokenError, RevokedIdTokenError
from firebase_admin.auth import CertificateFetchError



logger = Logger("GRPC_Service")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGO = os.getenv("JWT_ALGO",'HS256')



def handle_error(func): 
    @functools.wraps(func)
    def wrapper(self, request, context):
        try:
            return func(self, request, context)
        
        except User.DoesNotExist:
            logger.warning(f"User does not exist")
            context.abort(grpc.StatusCode.NOT_FOUND, "User Not Found")

        except Customer.DoesNotExist:
            logger.warning(f"customer does not exist")
            context.abort(grpc.StatusCode.NOT_FOUND, "User Not Found")

        except Store.DoesNotExist:
            logger.warning(f"Store with UUID {request.store_uuid} does not exist")
            context.abort(grpc.StatusCode.NOT_FOUND, "Store Not Found")

        except Address.DoesNotExist:
            logger.warning(f"Address with UUID {request.address_uuid} does not exist")
            context.abort(grpc.StatusCode.NOT_FOUND, "Address Not Found")

        except ObjectDoesNotExist:
            logger.warning("Requested object does not exist")
            context.abort(grpc.StatusCode.NOT_FOUND, "Requested Object Not Found")

        except MultipleObjectsReturned:
            logger.warning(f"Multiple objects found for request")
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Multiple matching objects found")

        except ValidationError as e:
            logger.warning(f"Validation Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Validation Error: {str(e)}")

        except IntegrityError as e:
            detail_message = e.args[0] if e.args else "Integrity constraint violation"
            logger.warning(f"Integrity Error: {detail_message}")
            
            context.abort(grpc.StatusCode.ALREADY_EXISTS, f"DETAIL: {detail_message}")

        except DatabaseError as e:
            logger.error(f"Database Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INTERNAL, "Internal Error")

        except PermissionDenied as e:
            logger.warning(f"Permission Denied: {str(e)}",e)
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission Denied")

        except ValueError as e:
            logger.warning(f"Invalid Value: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Invalid Value: {str(e)}")

        except TypeError as e:
            logger.error(f"Type Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Type Error: {str(e)}")

        except TimeoutError as e:
            logger.warning(f"Timeout Error: {str(e)}")
            context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "Request timed out")
            
        except grpc.RpcError as e:
            logger.error(f"RPC Error: {str(e)}")
            # Don't re-abort as this is likely a propagated error
            raise

        except FailedPrecondition as e:
            logger.warning(f"Failed Precondition: {e.details}")
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, f"Failed Precondition: {str(e)}")

        except Unauthenticated as e:
            logger.warning(f"Unauthenticated: {e.details}")
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
        except UserNotFoundError as e:
            logger.warning(f"User Not Found: {str(e)}")
            context.abort(grpc.StatusCode.NOT_FOUND, "User Not Found")
        except InvalidIdTokenError as e:
            logger.warning(f"Invalid Token: {str(e)}")
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid Token")
        except ExpiredIdTokenError as e:
            logger.warning(f"Expired Token: {str(e)}")
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Expired Token")
        except RevokedIdTokenError as e:
            logger.warning(f"Revoked Token: {str(e)}")
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Revoked Token")
        except CertificateFetchError as e:
            logger.warning(f"Certificate Fetch Error: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Certificate Fetch Error")
    
    return wrapper


class UserAuthService(AuthServiceServicer):
    def __init__(self):
        self.firebase_auth_manager = firebase_main.FireBaseAuthManager()
        self.jwt_manager = JWTManager(secret_key=JWT_SECRET_KEY,algorithm=JWT_ALGO)
        logger.info(f"{JWT_ALGO},{JWT_SECRET_KEY}")
    
    def _verify_wire_format(self,GRPC_message,GRPC_message_type,context_info = ""):
        """
        Helper to verify protobuf wire format
        Args:
            GRPC_message: The protobuf message to verify
            GRPC_message_type:The Protobuf message class type
            context_info: Additional context for logging 
        Returns:
            bool:True if Verifications Succeeds

        """
        try:
            serialized = GRPC_message.SerializeToString()
            logger.debug(f"Serialized Message Size: {len(serialized)} bytes")
            logger.debug(f"Message before serializtion: {GRPC_message}")

            test_msg = GRPC_message_type()
            test_msg.ParseFromString(serialized)

            original_fields = GRPC_message.ListFields()
            test_fields = test_msg.ListFields()

            if len(original_fields) != len(test_fields):
                logger.error(f"Field count mismatch - Original: {len(original_fields)}, Deserialized: {len(test_fields)}")
                logger.error(f"Original fields: {[f[0].name for f in original_fields]}")
                logger.error(f"Deserialized fields: {[f[0].name for f in test_fields]}")
            
            return True
        except Exception as e:
            logger.error(f"Wire Format verifications failed for {GRPC_message_type.__name__}{context_info}: {str(e)}")
            logger.error(f"Message Contents: {GRPC_message}")
            try:
                logger.error(f"Serialized hex: {serialized.hex()}")
            except:
                pass
            raise

    def _address_to_proto(self, address_obj):
        try:
            response = user_auth_pb2.address()

            try:
                response.address_uuid = str(address_obj.address_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert address_uuid: {e}")
                response.address_uuid = ""

            try:
                response.address_line_1 = address_obj.address_line_1 or ""
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert address_line_1: {e}")
                response.address_line_1 = ""

            try:
                response.address_line_2 = address_obj.address_line_2 or ""
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert address_line_2: {e}")
                response.address_line_2 = ""

            try:
                response.city = address_obj.city or ""
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert city: {e}")
                response.city = ""

            try:
                response.state = address_obj.state or ""
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert state: {e}")
                response.state = ""

            try:
                response.country = address_obj.country or ""
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert country: {e}")
                response.country = ""

            try:
                response.pincode = address_obj.pincode or ""
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert pincode: {e}")
                response.pincode = ""

            if not self._verify_wire_format(response, user_auth_pb2.address, f"address_uuid={address_obj.address_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Address {address_obj.address_uuid}")

            return response
        except Exception as e:
            logger.error("Error Creating address proto", e)
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, "Internal server error in _address_to_proto")

    def _store_to_proto(self, store_obj:Store):
        try:
            response = user_auth_pb2.store()

            try:
                response.store_uuid = str(store_obj.store_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert store_uuid: {e}")
                response.store_uuid = ""

            try:
                response.store_name = store_obj.name or ""
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert store_name: {e}")
                response.store_name = ""

            try:
                response.gst_number = store_obj.gst_number or ""
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert gst_number: {e}")
                response.gst_number = ""

            try:
                response.is_active = bool(store_obj.is_active)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert is_active: {e}")
                response.is_active = False

            try:
                response.is_open = bool(store_obj.is_open)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert is_open: {e}")
                response.is_open = False

            try:
                if store_obj.created_at:
                    response.created_at.FromDatetime(store_obj.created_at)
            except (AttributeError, ValueError) as e:
                logger.warning(f"Failed to convert created_at: {e}")

            try:
                if store_obj.updated_at:
                    response.updated_at.FromDatetime(store_obj.updated_at)
            except (AttributeError, ValueError) as e:
                logger.warning(f"Failed to convert updated_at: {e}")

            try:
                if store_obj.address:
                    response.address.CopyFrom(self._address_to_proto(store_obj.address))
            except (AttributeError, ValueError) as e:
                logger.warning(f"Failed to convert address: {e}")

            if not self._verify_wire_format(response, user_auth_pb2.store, f"store_uuid={store_obj.store_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Store {store_obj.store_uuid}")

            return response
        except Exception as e:
            logger.error("Error Creating store proto", e)
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, "Internal server error in _store_to_proto")

    def _user_to_proto(self,user_obj:User):
        try: 
            response = user_auth_pb2.user()

            try:
                response.user_uuid = str(user_obj.user_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert user_uuid: {e}")
                response.user_uuid = ""
            try:
                response.firebase_uid = str(user_obj.firebase_uid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert firebase_uid: {e}")
                response.firebase_uid = ""
            try:
                response.email = str(user_obj.email)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert email: {e}")
                response.email = ""
            try:
                response.phone = str(user_obj.phone)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert phone: {e}")
                response.phone = ""

            try:
                if user_obj.created_at:
                    response.created_at.FromDatetime(user_obj.created_at)
            except (AttributeError, ValueError) as e:
                logger.warning(f"Failed to convert created_at: {e}")

            try:
                if user_obj.updated_at:
                    response.updated_at.FromDatetime(user_obj.updated_at)
            except (AttributeError, ValueError) as e:
                logger.warning(f"Failed to convert updated_at: {e}")
            
            self._verify_wire_format(response, user_auth_pb2.user, f"user_uuid={user_obj.user_uuid}")
            
            return response
        
        except Exception as e:
            logger.error("Error Creating user proto", e)
            raise


    @handle_error
    def EmailSignUp(self, request, context):
        logger.info(request)
        firebase_uid = request.firebase_uid
        token = getattr(request.token, "token", request.token)

        logger.info(f"CreateUser called for firebase_uid={firebase_uid}")
        logger.debug(f"Raw token: {token}")

        # 1. Verify the ID token and UID match
        firebase_uid_from_token = self.firebase_auth_manager.verify_user_token(id_token=token)
        logger.debug(f"Token verified; firebase_uid_from_token={firebase_uid_from_token}")
        if firebase_uid != firebase_uid_from_token:
            logger.warning(f"Firebase UID mismatch: request={firebase_uid}, token={firebase_uid_from_token}")
            raise Unauthenticated("Firebase UID mismatch")

        # 2. Create user in DB
        with transaction.atomic():
            firebase_user = self.firebase_auth_manager.get_user_by_UID(firebase_uid)
            if not firebase_user:
                logger.warning(f"User not found in Firebase for firebase_uid={firebase_uid}")
                raise Unauthenticated("User not found in Firebase")
            
            user = User.objects.create(
                firebase_uid=firebase_uid,
                email=firebase_user.email
            )
            logger.info(f"Created User record; user_uuid={user.user_uuid}")

            # 3. Set Firebase custom claims
            claims = {
                "user_uuid": str(user.user_uuid),
                "firebase_uid": str(firebase_uid),
                "type": "store",
                "role": "admin",
                "store_uuids": json.dumps([]),
            }
        # 4. Create session cookie (7 days)
        session_cookie = self.firebase_auth_manager.create_session_cookie(token,60*60*24*7)
        jwt_token = self.jwt_manager.create_jwt(claims=claims,expires_in=1800)

        logger.info("Returning session and JWT")

        return user_auth_pb2.AccessTokenResponse(
            token=jwt_token,
            session_token=session_cookie,
        )

    @handle_error
    def EmailSignIn(self, request, context):
        firebase_uid = request.firebase_uid
        token = getattr(request.token, "token", request.token)

        logger.info(f"Sign-In called for firebase_uid={firebase_uid}")
        logger.debug(f"Raw token: {token}")

        # 1. Verify the ID token and UID match
        firebase_uid_from_token = self.firebase_auth_manager.verify_user_token(id_token=token)
        logger.debug(f"Token verified; firebase_uid_from_token={firebase_uid_from_token}")
        
        if firebase_uid != firebase_uid_from_token:
            logger.warning(f"Firebase UID mismatch: request={firebase_uid}, token={firebase_uid_from_token}")
            raise Unauthenticated("Firebase UID mismatch")
        user = self.firebase_auth_manager.get_user_by_UID(firebase_uid)

        if not user:
            logger.warning(f"No user found for firebase UID: {firebase_uid}")
            raise Unauthenticated("User not found")

        user_db:User = User.objects.prefetch_related('stores').get(firebase_uid=firebase_uid)

        store_uuids = user_db.stores.values_list('store_uuid', flat=True)
        store_uuids = [str(store_uuid) for store_uuid in store_uuids]

        claims = {
            "firebase_uid": firebase_uid,
            "type": "store",
            "role": "admin",
            "user_uuid": str(user_db.user_uuid),
            "store_uuids": json.dumps(store_uuids),  # ✅ fix
        }


        jwt_token = self.jwt_manager.create_jwt(claims=claims,expires_in=1800)
        session_cookie = self.firebase_auth_manager.create_session_cookie(token,60*60*24*7)

        return user_auth_pb2.AccessTokenResponse(session_token=session_cookie,
                                                 token = jwt_token
                                                 )

    @handle_error
    def OtpSignup(self, request, context):
        token = request.token
        name = request.name
        phone_number = request.phone_number

        logger.info("OtpSignup called")


        uid = self.firebase_auth_manager.verify_user_token(token)
        user = self.firebase_auth_manager.get_user_by_UID(uid)

        if not user:
            raise Unauthenticated("User not found in Firebase")

        with transaction.atomic():
            
            customer, created = Customer.objects.update_or_create(
                        firebase_UID=uid,
                        defaults={"phone_number": phone_number, "name": name}
                    )

        claims = {
            "type": "customer",
            "firebase_uid": uid,
            "user_phone_no":phone_number,
            "name":name

        }

        session_cookie = self.firebase_auth_manager.create_session_cookie(token,60*60*24*7)
        jwt_token = self.jwt_manager.create_jwt(claims=claims,expires_in=1800)
        

        # Done — now client should refresh ID token and call VerifyToken
       
        return user_auth_pb2.AccessTokenResponse(
                token=jwt_token,
                session_token=session_cookie,
            )


    @handle_error
    def RefreshUserSession(self, request, context):
        token = request.session_token
        logger.info("RefreshUserSession called")
        uid = self.firebase_auth_manager.verify_user_token(token)
        user = self.firebase_auth_manager.get_user_by_UID(uid)

        if not user:
            logger.warning(f"No user found for firebase UID: {uid}")
            raise Unauthenticated("User not found")

        user_db:User = User.objects.prefetch_related('stores').get(firebase_uid=uid)

        store_uuids = user_db.stores.values_list('store_uuid', flat=True)
        store_uuids = [str(store_uuid) for store_uuid in store_uuids]

        claims = {
            "user_uuid": str(user_db.user_uuid),
            "firebase_uid": str(uid),
            "type": "store",
            "role": "admin",
            "store_uuids": store_uuids,
            }


        jwt_token = self.jwt_manager.create_jwt(claims=claims,expires_in=1800)
        session_cookie = self.firebase_auth_manager.create_session_cookie(token,60*60*24*7)

        return user_auth_pb2.AccessTokenResponse(session_token=session_cookie,
                                                 token = jwt_token
                                                 )


    @handle_error
    def RefreshCustomerSession(self, request, context):
        token = request.session_token
        logger.info("RefreshCustomerSession called")
        
        _= self.firebase_auth_manager.verify_session_cookie(token)
        uid = _.get("user_id")
        user = self.firebase_auth_manager.get_user_by_UID(uid)


        if not user:
            logger.warning(f"No user found for firebase UID: {uid}")
            raise Unauthenticated("User not found")

        try:
            customer = Customer.objects.get(firebase_UID=uid)
        except Customer.DoesNotExist:
            logger.warning(f"customer with UID:{uid} does not exits" )
            raise

        
        claims = {
            "firebase_uid": uid,
            "type": "customer",
            "name": customer.customer_name,
            "user_phone_no": customer.phone_number,
        }

        # 4. Issue new session cookie and short-lived
        session_cookie = self.firebase_auth_manager.create_session_cookie(token, 60 * 60 * 24 * 7)
        jwt_token = self.jwt_manager.create_jwt(claims=claims, expires_in=1800)

        # 5. Return both tokens
        return user_auth_pb2.AccessTokenResponse(
            session_token=session_cookie,
            token=jwt_token
        )

    @handle_error
    def RefreshCustomerJwt(self, request, context):
        token = request.session_token
        if not self.jwt_manager.is_jwt(token):
            raise ValidationError("Not a JWT token")
        logger.info("RefreshCustomerJwt called")

        # 1. Verify session token
        _= self.firebase_auth_manager.verify_session_cookie(token)
        uid = _.get("user_id")
        user = self.firebase_auth_manager.get_user_by_UID(uid)
        if not user:
            raise Unauthenticated("User not found")

        # 2. Get customer from DB
        try:
            customer = Customer.objects.get(firebase_UID=uid)
        except Customer.DoesNotExist:
            logger.warning(f"No customer found for firebase UID: {uid}")
            raise Unauthenticated("Customer not found")

        # 3. Construct JWT claims
        claims = {
            "firebase_uid": uid,
            "type": "customer",
            "name": customer.customer_name,
            "user_phone_no": customer.phone_number,
            # "customer_uuid": str(customer.customer_uuid),
        }

        # 4. Issue short-lived JWT
        jwt_token = self.jwt_manager.create_jwt(claims=claims, expires_in=1800)

        return user_auth_pb2.AccessTokenResponse(token=jwt_token)


    @handle_error
    def RefreshStoreJwt(self, request, context):
        logger.info(request)
        token = request.session_token
        if not self.jwt_manager.is_jwt(token):
            raise ValidationError("Not a JWT token")
        logger.info("RefreshCustomerJwt called")

        logger.info("RefreshStoreJwt called")
        _= self.firebase_auth_manager.verify_session_cookie(token)
        uid = _.get("user_id")
        user = self.firebase_auth_manager.get_user_by_UID(uid)

        if not user:
            logger.warning(f"No user found for firebase UID: {uid}")
            raise Unauthenticated("User not found")

        user_db: User = User.objects.prefetch_related('stores').get(firebase_uid=uid)

        store_uuids = user_db.stores.values_list('store_uuid', flat=True)
        store_uuids = [str(store_uuid) for store_uuid in store_uuids]

        claims = {
            "firebase_uid": uid,
            "type": "store",
            "role": "admin",
            "user_uuid": str(user_db.user_uuid),
            "store_uuids": json.dumps(store_uuids),  # ✅ fix
        }
        jwt_token = self.jwt_manager.create_jwt(claims=claims, expires_in=1800)

        return user_auth_pb2.AccessTokenResponse(token=jwt_token)


    @handle_error
    @check_access(
        expected_types=["store"],
    allowed_roles={"store":["admin","staff"]}
    )
    def CreateStore(self, request, context):
        user_uuid = request.user_uuid
        store_name = request.store_name

        logger.info(f"CreateStore called for user_uuid={user_uuid}, store_name={store_name}")

        try:
            user = User.objects.get(user_uuid=user_uuid)
            logger.info(f"User retrieved successfully for user_uuid={user_uuid}")
        except User.DoesNotExist:
            logger.warning(f"User with user_uuid={user_uuid} does not exist")
            raise 

        with transaction.atomic():
            
            store = Store.objects.create(
                name=store_name,
                user=user,
                gst_number=request.gst_number,
                is_active=request.is_active,
                discription=request.description
            )
            logger.info(f"Created Store record; store_uuid={store.store_uuid}") 
            return user_auth_pb2.StoreResponse(
                user_uuid=str(store.user.user_uuid),
                store=self._store_to_proto(store),
            )

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def UpdateStore(self, request, context):
        store_uuid = request.store_uuid

        with transaction.atomic():
            
            store = Store.objects.get(store_uuid=store_uuid)
        
            if request.HasField('store_name'):
                store.name = request.store_name
            if request.HasField('gst_number'):
                store.gst_number = request.gst_number
            if request.HasField('is_active'):
                store.is_active = request.is_active
            if request.HasField('is_open'):
                store.is_open = request.is_open        

            store.save()

            return user_auth_pb2.StoreResponse(
                user_uuid=str(store.user.user_uuid),
                store = self._store_to_proto(store),)

    
    @handle_error
    @check_access(
    expected_types=["store","customer"],
    allowed_roles={"store":["admin","staff"]})
    def GetStore(self, request, context):
        user_uuid = request.user_uuid
        store_uuid = request.store_uuid

        with transaction.atomic():
            
                store = Store.objects.get(store_uuid=store_uuid)

        return user_auth_pb2.StoreResponse(
                user_uuid=str(store.user.user_uuid),
                store = self._store_to_proto(store),)


    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def GetAllStores(self, request, context):

        user_uuid = request.user_uuid


        limit = int(request.limit) if request.limit != "" else 10
        page = int(request.page) if request.page != "" else 1

        logger.info(f"GetAllStores called for user_uuid={user_uuid}, limit={limit}, page={page}")

        data, next_page, prev_page = Store.objects.get_stores(user_uuid, limit, page)
        logger.info(f"Retrieved {len(data)} stores for user_uuid={user_uuid}")

        return user_auth_pb2.GetAllStoreResponse(
            stores=[self._store_to_proto(store) for store in data],
            next_page=next_page,
            prev_page=prev_page
        )
    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def DeleteStore(self, request, context):
        store_uuid = request.store_uuid

        with transaction.atomic():
            
            store = Store.objects.get(store_uuid=store_uuid)
            store.delete()

        return empty_pb2.Empty()
    
    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
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
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def UpdateAddress(self, request, context):
        logger.info(request)
        address_uuid = request.address_uuid

        with transaction.atomic():
        
            address = Address.objects.get(address_uuid=address_uuid)
            store = Store.objects.get(address=address)

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
                store_uuid=str(store.store_uuid),
                address=self._address_to_proto(address)
            )

    
    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def GetAddress(self, request, context):
        address_uuid = request.address_uuid
        store_uuid = request.store_uuid

        with transaction.atomic():
            
            address = Address.objects.get(address_uuid=address_uuid)
                

        return user_auth_pb2.AddressResponse(
            store_uuid=str(address.store.store_uuid),
            address=self._address_to_proto(address))
    
    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def DeleteAddress(self, request, context):
        address_uuid = request.address_uuid
        store_uuid = request.store_uuid

        with transaction.atomic():
            
            address = Address.objects.get(address_uuid=address_uuid)
            address.delete()

        return empty_pb2.Empty()

    
    
    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def GetUser(self, request, context):
        user_uuid = request.user_uuid

        with transaction.atomic():
            user = User.objects.get(user_uuid=user_uuid)

        return self._user_to_proto(user)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def UpdateUser(self, request, context):
        user_uuid = request.user_uuid

        with transaction.atomic():
            user = User.objects.get(user_uuid=user_uuid)

            if request.HasField("email"):
                user.email = request.email
            if request.HasField("email_verified"):
                user.email_verified = request.email_verified
            if request.HasField("role"):
                user.role = request.role
            if request.preferences:
                user.preferences.update(request.preferences)

            user.save()

        return self._user_to_proto(user)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def DeleteUser(self, request, context):
        user_uuid = request.user_uuid

        with transaction.atomic():
            user = User.objects.get(user_uuid=user_uuid)
            user.delete()

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