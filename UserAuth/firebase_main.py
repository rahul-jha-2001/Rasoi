from datetime import timedelta
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.auth import UserRecord, UserNotFoundError
from firebase_admin.auth import ExpiredIdTokenError, RevokedIdTokenError, InvalidIdTokenError, CertificateFetchError, InvalidSessionCookieError, InvalidSessionCookieError
from firebase_admin.auth import UserNotFoundError, InvalidIdTokenError, ExpiredIdTokenError, RevokedIdTokenError, CertificateFetchError
from dotenv import load_dotenv
from utils.logger import Logger

load_dotenv()
logger = Logger(__name__)

class FireBaseAuthManager:
    def __init__(self, cert_file: str = "rasoi-auth-firebase-adminsdk-fbsvc-2131b3731f.json"):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cert_file)
            firebase_admin.initialize_app(cred)
        self.auth = auth


    def get_user_by_UID(self, uid) -> UserRecord:
        """
        Fetch Firebase user by UID.
        """
        try:
            user = self.auth.get_user(uid)
            logger.info(f"Fetched Firebase user: {uid}")
            return user
        except UserNotFoundError as e:
            logger.warning(f"Firebase user not found: {uid}")
            raise e
        except Exception as e:
            logger.error(f"Error fetching user by UID: {str(e)}", e)
            raise e


    # ========== SESSION COOKIE ==========
    def create_session_cookie(self, id_token: str, expires_in_seconds: int = 60 * 60 * 24 * 5) -> str:
        try:
            expires_in = timedelta(seconds=expires_in_seconds)
            return self.auth.create_session_cookie(id_token, expires_in=expires_in)
        except Exception as e:
            logger.error("Failed to create session cookie", e)
            raise Exception("Failed to create session cookie") from e

    def verify_session_cookie(self, session_cookie: str, check_revoked: bool = True):
        try:
            return self.auth.verify_session_cookie(session_cookie, check_revoked=check_revoked)
        except InvalidSessionCookieError:
            raise ValueError("Invalid or expired session cookie")
        except Exception as e:
            raise e

    # ========== TOKEN HANDLING ==========
    def verify_user_token(self, id_token: str):
        try:
            decoded_token = self.auth.verify_id_token(id_token)
            return decoded_token["uid"]
        except InvalidIdTokenError:
            raise ValueError("Invalid token")
        except CertificateFetchError:
            raise ValueError("Certificate error")
        except Exception as e:
            raise e

    # ========== CLAIM MANAGEMENT ==========
    def set_custom_claims(self, uid: str, claims: dict):
        try:
            self.auth.set_custom_user_claims(uid, claims)
            logger.info(f"Set claims for user: {uid}")
        except Exception as e:
            logger.error(f"Failed to set claims for {uid}", e)
            raise

    def get_user_claims(self, uid: str):
        try:
            user = self.auth.get_user(uid)
            return user.custom_claims or {}
        except Exception as e:
            raise e

    def add_custom_claims(self, uid: str, claims: dict):
        try:
            user = self.auth.get_user(uid)
            existing = user.custom_claims or {}
            combined = {**existing, **claims}
            self.auth.set_custom_user_claims(uid, combined)
            logger.info(f"Updated claims for {uid}")
        except Exception as e:
            raise e

    # ========== USER MANAGEMENT ==========
    def get_user_by_uid(self, uid: str) -> UserRecord:
        try:
            return self.auth.get_user(uid)
        except UserNotFoundError as e:
            raise e
        except Exception as e:
            raise e

    def create_user(self, email: str, password: str) -> UserRecord:
        try:
            return self.auth.create_user(email=email, password=password)
        except Exception as e:
            raise e

    def update_user(self, uid: str, email: str, password: str) -> UserRecord:
        try:
            return self.auth.update_user(uid=uid, email=email, password=password)
        except Exception as e:
            raise e

    def delete_user(self, uid: str):
        try:
            self.auth.delete_user(uid)
        except Exception as e:
            raise e

    def list_users(self, max_results=1000) -> list[UserRecord]:
        try:
            page = self.auth.list_users(max_results=max_results)
            return page.users
        except Exception as e:
            raise e
    def create_custom_token(self, uid: str) -> bytes:
        """
        Generate a custom Firebase token for the given UID.
        Used to force a token refresh after setting custom claims.
        """
        try:
            return self.auth.create_custom_token(uid)
        except Exception as e:
            logger.error(f"Failed to create custom token for UID={uid}", e)
            raise Exception("Failed to create custom token") from e
