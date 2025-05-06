
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
                logger.info(f"User not found: {uid}")
                return None
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
            logger.error(f"Error verifying token",e)
            raise e
    
    def get_user_by_UID(self,uid):
        # Get a user by UID
        try:
            user = self.auth.get_user(uid)
            logger.info(f"Successfully fetched user data: {user.uid}")
            return user
        except UserNotFoundError:
            logger.info(f"User not found: {uid}")
            return None
        except Exception as e:
            logger.info(f"Error fetching user data",e)
            return None
        
    
    
    def add_store_claims(self,id_token,store_uuids):
        # Update store claims for a user
        try:
            uid = self.verify_user_token(id_token)
            user = self.auth.get_user(uid)
            if not user:
                logger.info(f"User not found: {uid}")
                return None
            # Check if the user already has store claims
            existing_claims = user.custom_claims or {}
            if "store_uuids" in existing_claims:
                # Merge existing store claims with new ones
                store_uuids = list(set(existing_claims["store_uuids"]) | set(store_uuids))
            
            self.auth.set_custom_user_claims(uid, {"role":"store","store_uuids": store_uuids})
            
            logger.info(f"Successfully updated store claims for user: {uid}")
        
        except Exception as e:
            logger.error(f"Error updating store claims: {str(e)}",e)    
            raise e