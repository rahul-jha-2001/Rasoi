import sys
import os
sys.path.append(os.getcwd())
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UserAuth.settings')
django.setup()
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction
from django.contrib.auth.hashers import make_password

import grpc
from concurrent import futures
import uuid
import random
import re
import redis
import logging
import os
from datetime import datetime
import traceback
from decimal import Decimal as DecimalType
from dotenv import load_dotenv
from google.protobuf import timestamp_pb2
from utils import generate_otp,JWTAuthentication
import traceback

from proto import UserAuth_pb2,UserAuth_pb2_grpc
from User.models import Store,Customer,CustomerLogin
logger = logging.getLogger(__name__)

load_dotenv()

class UserAuthService(UserAuth_pb2_grpc.UserAuthServiceServicer):

    def _validate_phone_number(self, phone_number):
        """Validate phone number format"""
        pattern = r'^\+?1?\d{9,15}$'
        return re.match(pattern, phone_number) is not None

    def _validate_gst_number(self, gst_number):
        """Validate GST number format"""
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        return re.match(pattern, gst_number) is not None

    def CreateOTP(self, request, context):
    
        try:
            # Log the incoming request
            logger.info(f"OTP Creation Request - Phone Number: {request.PhoneNumber}")

            # Validate phone number
            if not self._validate_phone_number(request.PhoneNumber):
                logger.error(f"Invalid phone number format: {request.PhoneNumber}")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Invalid phone number format')
                return UserAuth_pb2.OTPResponse(Success=False, message='Invalid phone number')

            # Generate a 6-digit OTP
            try:
                otp = generate_otp(4)
                logger.info(f"OTP generated for phone number: {request.PhoneNumber}")
            except Exception as otp_gen_error:
                logger.error(f"Failed to generate OTP: {str(otp_gen_error)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('OTP generation failed')
                return UserAuth_pb2.OTPResponse(Success=False, message='OTP generation error')

            # Store OTP temporarily 
            data = {
                'OTP': otp,
                'PhoneNumber': request.PhoneNumber,
                'UserName': request.UserName,
                'StoreUuid': request.StoreUuid,
                "created_at": datetime.now().timestamp()
            }
            try:
                # Store in Redis
                RedisCilent.hset(data['PhoneNumber'], mapping=data)
                logger.info(f"OTP stored in Redis for phone number: {request.PhoneNumber}")
            except Exception as redis_error:
                logger.error(f"Failed to store OTP in Redis: {str(redis_error)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('Failed to store OTP')
                return UserAuth_pb2.OTPResponse(Success=False, message='OTP storage error')

            # Messaging service (placeholder for future implementation)
            try:
                # Add your messaging service logic here
                # self.send_sms(phone_number, otp)
                """


                            Add The messaging Service here


                """
                logger.info(f"OTP message preparation for phone number: {request.PhoneNumber}")
            except Exception as messaging_error:
                logger.warning(f"Failed to prepare messaging service: {str(messaging_error)}")

            # Convert datetime to Timestamp
            created_at = timestamp_pb2.Timestamp()
            created_at.FromDatetime(datetime.fromtimestamp(data["created_at"]))

            # Return successful response
            logger.info("")
            return UserAuth_pb2.OTPResponse(
                Success=True, 
                message='OTP Generated Successfully',
                CreatedAt=created_at
            )

        except Exception as unexpected_error:
            # Catch any unexpected errors
            logger.error(f"Unexpected error in CreateOTP: {str(unexpected_error)}")
            logger.error(traceback.format_exc())
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Unexpected error during OTP creation')
            return UserAuth_pb2.OTPResponse(Success=False, message='Internal server error')

    def VerifyOTP(self, request, context):
        """Verify the OTP"""
        # Check if OTP reference exists
        if not RedisCilent.exists(request.PhoneNumber):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Invalid OTP reference')
            logger.error("OTP Does not Exist For the PhoneNumber")
            return UserAuth_pb2.AuthResponse(authenticated=False, message='Invalid OTP')

        # Retrieve the stored OTP data
        try:
            stored_data = RedisCilent.hgetall(request.PhoneNumber)
            # logger.info(stored_data)
        except :
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Invalid OTP reference')
            logger.error("OTP Does not Exist For the PhoneNumber")
            return UserAuth_pb2.AuthResponse(authenticated=False, message='Could not Fetch from REDIS')

        
        
        # Check if the OTP matches
        if stored_data.get('OTP') != request.OTP:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Incorrect OTP')
            return UserAuth_pb2.AuthResponse(authenticated=False, message='Incorrect OTP')

        # Optional: Check OTP expiration (recommended)
        created_at = float(stored_data.get('created_at'))
        current_time = datetime.now().timestamp()
        # logger.info(f"Time Difff {current_time - created_at}")


        if (current_time - created_at) > 300:  # 5 minutes expiration
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details('OTP has expired')
            return UserAuth_pb2.AuthResponse(authenticated=False, message='OTP expired')

        # Remove the OTP after successful verification (optional but recommended)
        
        access_token = JWTAuthentication.Customer_generate_token(UserName=request.UserName,PhoneNumber= request.PhoneNumber,token_type='access')
        refresh_token = JWTAuthentication.Customer_generate_token(UserName=request.UserName,PhoneNumber= request.PhoneNumber,token_type='refresh')

        try:
            store = Store.objects.get(StoreUuid = request.StoreUuid)
        
        except Store.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Store not found')
            return UserAuth_pb2.AuthResponse(authenticated=False, message='Store does not exist')
            
        except Exception as e:
            # Catch any unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Internal error: {str(e)}')
            return UserAuth_pb2.AuthResponse(authenticated=False, message=f'Error {str(e)} has occured ')

        try:
            customer,created = Customer.objects.get_or_create(Name = request.UserName,PhoneNo = request.PhoneNumber)
            login = CustomerLogin.objects.create(customer=customer,store = store)
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Internal error: {str(e)}')
            return UserAuth_pb2.AuthResponse(authenticated=False, message=f'Error {str(e)} has occured ')



        RedisCilent.delete(request.PhoneNumber)    
        # Generate and return authentication token
        return UserAuth_pb2.AuthResponse(
            authenticated=True, 
            JWTtoken =UserAuth_pb2.Token(
                access= access_token,
                refresh= refresh_token
            ),
            message='Authentication Successful'
        )

    @transaction.atomic
    def CreateStore(self, request, context):
        """Create a new store"""
        # Validate input
        if not self._validate_phone_number(request.PhoneNumber):
            logger.error(f"Invalid phone number format: {request.PhoneNumber}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Invalid phone number')
            return UserAuth_pb2.CreateStoreResponse(success=False, message='Invalid phone number')

        if not self._validate_gst_number(request.GSTNumber):
            logger.error(f"Invalid GST number format: {request.GSTNumber}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Invalid GST number')
            return UserAuth_pb2.CreateStoreResponse(success=False, message='Invalid GST number')

        try:

            store = Store.objects.create_user(
                email = request.Email,
                PhoneNo = request.PhoneNumber,
                StoreName = request.StoreName,
                StoreAddress = request.StoreAddress,
                GST = request.GSTNumber,
                password = request.Password  
                )
            return UserAuth_pb2.CreateStoreResponse(
                success=True, 
                StoreUuid=str(store.StoreUuid),
                message=str('Store Created Successfully')
            )
        except IntegrityError as e:

            error_msg = 'Store creation failed: Duplicate entry or database constraint violated'
            logger.error(f"{error_msg} Store creation failed: Duplicate entry or database constraint violated {str(e)}")
            
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(error_msg)
            
            return UserAuth_pb2.CreateStoreResponse(
                success=False, 
                message=error_msg
            )
        
        except ValidationError as e:
            # Handle Django validation errors
            error_msg = f'Store creation validation failed: {str(e)}'
            logger.error(error_msg)
            
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(error_msg)
            
            return UserAuth_pb2.CreateStoreResponse(
                success=False, 
                message=error_msg
            )
        
        except Exception as e:
            # Catch-all for unexpected errors
            error_msg = f'Unexpected error during store creation: {str(e)} '
            logger.critical(error_msg, exc_info=True)
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            
            return UserAuth_pb2.CreateStoreResponse(
                success=False, 
                message='An unexpected error occurred'
            )

    def AuthStore(self, request, context):
        """Authenticate a store"""
        if not request.Email or not request.Password:
            logger.error("Password or Email Not present")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Email and password are required')
            return UserAuth_pb2.AuthStoreResponse(Authenticated=False, message='Authentication Failed')

        try:

            store = Store.objects.get(email=request.Email)
            
            if not store.check_password(request.Password):
                logger.error("Incorrect Password")
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('Invalid credentials')
                return UserAuth_pb2.AuthStoreResponse(Authenticated=False, message='Authentication Failed')
            
            # Generate a token (you might want to use a more robust token generation method)
            access = JWTAuthentication.Store_generate_token(store,'access')
            refresh = JWTAuthentication.Store_generate_token(store,'refresh')
            
            # Optional: You could implement token storage or caching here
            logger.info(f"Tokens generated for {request.Email}")
            return UserAuth_pb2.AuthStoreResponse(
                Authenticated=True,
                StoreUuid = str(store.StoreUuid),  # Convert UUID to string
                JWTToken=UserAuth_pb2.Token(
                    access = access,
                    refresh = refresh
                ),
                message='Authentication Successful'
            )
        
        except Store.DoesNotExist:
            # Store not found
            logger.error(f"Store Does Not Exists For Email {request.Email}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Store not found')
            return UserAuth_pb2.AuthStoreResponse(Authenticated=False, message='Authentication Failed')
            
        except Exception as e:
            # Catch any unexpected errors
            logger.error(f"Some Eorro {str(e)} ")

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Internal error: {str(e)}')
            return UserAuth_pb2.AuthStoreResponse(Authenticated=False, message='Authentication Failed')

    @transaction.atomic
    def UpdateStore(self, request, context):
        """Update store information"""
        # Update store details
        try:
            store = Store.objects.get(StoreUuid=request.StoreUuid)
            
            if request.HasField("PhoneNumber"):
                if not self._validate_phone_number(request.PhoneNumber):
                    logger.error(f"Invalid Phone Number {request.PhoneNumber}")
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details('Invalid phone number')
                    return UserAuth_pb2.UpdateStoreResponse(success=False, message='Invalid phone number')
                store.PhoneNo = request.PhoneNumber
            
            if request.HasField("GSTNumber"):
                if not self._validate_gst_number(request.GSTNumber):
                    logger.error(f"GST number Incorrect {request.GSTNumber}")
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details('Invalid GST number')
                    return UserAuth_pb2.UpdateStoreResponse(success=False, message='Invalid GST number')
                store.GST = request.GSTNumber #Need to change GST to GSTNumber

            if request.HasField("StoreName"):
                store.StoreName = request.StoreName
            
            if request.HasField("StoreAddress"):
                store.StoreAddress = request.StoreAddress

            if request.HasField("Email"):
                store.email = request.Email

            store.full_clean()
            store.save()
            
            logger.info(f"Store for Store Uuid:{request.StoreUuid} updated")
            return UserAuth_pb2.UpdateStoreResponse(success=True, message='Store Updated Successfully')

        except Store.DoesNotExist:
            logger.error(f"Store does not Exist for {request.StoreUuid}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Store not found')
            return UserAuth_pb2.UpdateStoreResponse(success=False, message='Store does not exist')
            
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'Validation Error: {str(e)}')
            return UserAuth_pb2.UpdateStoreResponse(success=False, message=str(e))
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Internal error: {str(e)}')
            return UserAuth_pb2.UpdateStoreResponse(success=False, message=str(e))
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    UserAuth_pb2_grpc.add_UserAuthServiceServicer_to_server(UserAuthService(),server)
    
    grpc_port = os.getenv('GRPC_SERVER_PORT', '50051')

    server.add_insecure_port(f"[::]:{grpc_port}")
    server.start()
    logger.info(f"Server Stated at {grpc_port}")
    server.wait_for_termination()

if __name__ == "__main__":
    RedisCilent = redis.Redis(host=os.getenv("REDIS_ADDRESS","localhost"),
                              port=os.getenv("REDIS_PORT",6379),
                              password= os.getenv("REDIS_PASSWORD"),
                              decode_responses=True)
    logging.basicConfig(level= logging.INFO)
    serve()