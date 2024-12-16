import secrets
import string
import jwt
import datetime
import dotenv
import os 
dotenv.load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY","Rahul")

def generate_otp(length=6, use_digits=True, use_letters=False):
    """
    Generate a secure OTP with the specified length.
    
    Parameters:
        length (int): Length of the OTP (default: 6).
        use_digits (bool): Whether to include digits in the OTP (default: True).
        use_letters (bool): Whether to include letters in the OTP (default: False).
    
    Returns:
        str: The generated OTP.
    """
    if not (use_digits or use_letters):
        raise ValueError("At least one of 'use_digits' or 'use_letters' must be True.")
    
    characters = ''
    if use_digits:
        characters += string.digits
    if use_letters:
        characters += string.ascii_letters
    
    otp = ''.join(secrets.choice(characters) for _ in range(length))
    return otp



class JWTAuthentication:
    @staticmethod
    def Store_generate_token(user, token_type='access'):
        # Different expiration for access and refresh tokens
        if token_type == 'access':
            expiration = datetime.datetime.now() + datetime.timedelta(minutes=15)
        else:  # refresh token
            expiration = datetime.datetime.now() + datetime.timedelta(days=7)
        
        payload = {
            'StoreUuid': str(user.StoreUuid),
            'email': user.email,
            'token_type': token_type,
            'exp': expiration,
            'iat': datetime.datetime.now()
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def validate_token(token):
        try:
            # Decode and validate the token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return False  # Token has expired
        except jwt.InvalidTokenError:
            return False # Invalid token
    
    @staticmethod
    def Customer_generate_token(UserName,PhoneNumber,token_type = 'access'):
        if token_type == 'access':
            expiration = datetime.datetime.now() + datetime.timedelta(minutes=15)
        else:  # refresh token
            expiration = datetime.datetime.now() + datetime.timedelta(days=7)
        
        payload = {
            'UserName': str(UserName),
            'PhoneNumber':str(PhoneNumber),
            'token_type': token_type,
            'exp': expiration,
            'iat': datetime.datetime.now()
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
