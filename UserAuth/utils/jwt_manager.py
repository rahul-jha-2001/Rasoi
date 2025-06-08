import jwt
import datetime
import re

class JWTManager:
    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.jwt_regex = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


    def create_jwt(self, claims: dict, expires_in: int = 1800) -> str:
        payload = claims.copy()
        payload["exp"] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in)
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_custom_jwt(self,token: str, secret: str):
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload  # This contains your claims (user_uuid, role, etc.)
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")


    def is_jwt(self,token: str) -> bool:
        return bool(self.jwt_regex.match(token))

