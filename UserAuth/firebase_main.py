
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.auth import UserRecord, UserNotFoundError, InvalidIdTokenError
from firebase_admin.auth import ExpiredIdTokenError, RevokedIdTokenError
from firebase_admin.auth import CertificateFetchError

from dotenv import load_dotenv
load_dotenv()
from utils.logger import Logger
logger = Logger(__name__)

class FireBaseAuthManager:
    def __init__(self,cert_file:str = None):
        # Initialize Firebase Admin SDK
        self.cred = credentials.Certificate("rasoi-auth-firebase-adminsdk-fbsvc-2131b3731f.json")
        firebase_admin.initialize_app(self.cred)
        self.auth = auth


    def vetify_token_and_set_claims(self,id_token,claims):
        # Verify a user and set custom claims
        try:
            uid = self._verify_user_token(id_token)
            user = self.auth.get_user(uid)
            if user:
                self.auth.set_custom_user_claims(uid, claims)
                logger.info(f"Successfully verified user and set claims: {uid}")
                return user.id
            else:
                raise UserNotFoundError(f"User not found: {uid}")
        except Exception as e:
            logger.error(f"Error verifying user and setting claims: {e}",e)
            raise e

    def verify_user_token(self,id_token):
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            return uid
        except auth.InvalidIdTokenError:
            raise ValueError("Invalid token")
        except auth.ExpiredIdTokenError:
            raise ValueError("Token expired")
        except auth.RevokedIdTokenError:
            raise ValueError("Token revoked")
        except auth.CertificateFetchError:
            raise ValueError("Certificate error")
        except Exception as e:
            raise e
    
    def get_user_by_UID(self,uid) -> UserRecord:
        # Verify a user and get their data
        # Get a user by UID
        try:
            user = self.auth.get_user(uid)
            logger.info(f"Successfully fetched user data: {user.uid}")
            return user
        except UserNotFoundError as e:
            raise e
        except Exception as e:
            raise e 
    
    def add_store_claims(self,id_token,store_uuids):
        # Update store claims for a user
        try:
            uid = self.verify_user_token(id_token)
            user = self.auth.get_user(uid)
            if not user:
                raise UserNotFoundError(f"User not found: {uid}")
            # Check if the user already has store claims
            existing_claims = user.custom_claims or {}
            if "store_uuids" in existing_claims:
                # Merge existing store claims with new ones
                store_uuids = list(set(existing_claims["store_uuids"]) | set(store_uuids))
            
            self.auth.set_custom_user_claims(uid, {"role":"store","store_uuids": store_uuids})
            
            logger.info(f"Successfully updated store claims for user: {uid}")
        
        except Exception as e:
            raise e
        
    def get_user_claims(self,uid):
        # Get user claims
        try:
            user = self.auth.get_user(uid)
            if not user:
                raise UserNotFoundError(f"User not found: {uid}")
            claims = user.custom_claims
            logger.info(f"Successfully fetched user claims: {claims}")
            return claims
        except Exception as e:
            raise e
    
    def add_custom_claims(self,firebase_uid,claims):
        # Add custom claims to a user
        try:
            user = self.auth.get_user(firebase_uid)
            if not user:
                raise UserNotFoundError(f"User not found: {firebase_uid}")
            # Check if the user already has custom claims
            existing_claims = user.custom_claims or {}
            # Merge existing claims with new ones
            claims = {**existing_claims, **claims}
            
            self.auth.set_custom_user_claims(firebase_uid, claims)
            
            logger.info(f"Successfully updated custom claims for user: {firebase_uid}")
        
        except Exception as e:
            raise e
    

    def create_user(self,email,password) -> UserRecord:
        # Create a new user
        try:
            user = self.auth.create_user(
                email=email,
                password=password
            )
            logger.info(f"Successfully created user: {user.uid}")
            return user
        except Exception as e:
            raise e
    
    def update_user(self,uid,email,password) -> UserRecord:
        # Update user details
        try:
            user = self.auth.update_user(
                uid=uid,
                email=email,
                password=password
            )
            logger.info(f"Successfully updated user: {user.uid}")
            return user
        except UserNotFoundError as e:
            raise e
        except Exception as e:
            raise e
    
    def list_users(self, max_results=1000)  -> list[UserRecord]:
        # List all users
        try:
            page = self.auth.list_users(max_results=max_results)
            users = page.users
            logger.info(f"Successfully listed {len(users)} users")
            return users
        except Exception as e:
            raise e
    def delete_user(self,uid)  -> None:
        # Delete a user by UID
        try:
            self.auth.delete_user(uid)
            logger.info(f"Successfully deleted user: {uid}")
        except UserNotFoundError as e:
            raise e
        except Exception as e:
            raise e
    
    def get_access_token(self,uid) -> str:
        # Get access token for a user
        try:
            user = self.auth.get_user(uid)
            if not user:
                raise UserNotFoundError(f"User not found: {uid}")
            access_token = auth.create_custom_token(uid)
            logger.info(f"Successfully created access token for user: {uid}")
            return access_token
        except Exception as e:
            raise e