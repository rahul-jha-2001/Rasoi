import io
from PIL import Image
import imghdr
import boto3
from botocore.exceptions import NoCredentialsError


class image_handler:
    
    @staticmethod
    def check_size(bytes_data):
        """
        Check the size of bytes data in KB.
        
        Args:
            bytes_data (bytes): The bytes data to check.
            
        Returns:
            float: Size of the data in kilobytes.
        """
        size_in_mb = len(bytes_data) / (1024*1024)
        return size_in_mb
    
    @staticmethod
    def bytes_to_image(bytes_data):
        """
        Convert bytes data to a PIL Image object.
        
        Args:
            bytes_data (bytes): The bytes data to convert.
            
        Returns:
            PIL.Image: The converted image object.
        """
        if not bytes_data:
            raise ValueError("Empty bytes data provided")
        
        try:
            image = Image.open(io.BytesIO(bytes_data))
            return image
        except Exception as e:
            raise ValueError(f"Failed to convert bytes to image: {str(e)}")
    
    @staticmethod
    def check_extension(bytes_data):
        """
        Detect the file extension from image bytes data.
        
        Args:
            bytes_data (bytes): The bytes data to check.
            
        Returns:
            str: The file extension (e.g., '.jpg', '.png').
        """
        if not bytes_data:
            raise ValueError("Empty bytes data provided")
        
        # Method 1: Using imghdr
        image_type = imghdr.what(None, h=bytes_data)
        if image_type:
            return f".{image_type}"
        
        # Method 2: Try with PIL as fallback
        try:
            image = Image.open(io.BytesIO(bytes_data))
            return f".{image.format.lower()}"
        except:
            return None
    
    @staticmethod
    def upload_to_s3(bytes_data, bucket_name, 
                    object_name=None,
                    aws_access_key=None,
                    aws_secret_key=None,
                    region_name=None):
        """
        Upload image bytes to an S3 bucket.
        
        Args:
            bytes_data (bytes): The bytes data to upload.
            bucket_name (str): Name of the S3 bucket.
            object_name (str, optional): S3 object name. If not specified, a name will be generated.
            aws_access_key (str, optional): AWS access key.
            aws_secret_key (str, optional): AWS secret key.
            region_name (str, optional): AWS region name.
            
        Returns:
            bool: True if upload was successful, False otherwise.
            str: Object URL if successful, error message otherwise.
        """
        if not bytes_data:
            return False, "Empty bytes data provided"
        
        # Generate object name if not provided
        extension = image_handler.check_extension(bytes_data)
        if not extension:
            raise ValueError("Unkown image extention")
        if extension not in ['.jpg','.png','.jpeg']:
            raise ValueError(f"{extension} is not allowed")
        object_name = f'{object_name}{extension}'
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name
        ) if (aws_access_key and aws_secret_key) else boto3.client('s3', region_name=region_name)
        
        try:
            # Upload the file
            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=bytes_data,
                ContentType=f"image/{extension[1:]}" if extension else "image/jpeg"
            )
            # Generate the URL
            url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{object_name}"
            return True, url
        except NoCredentialsError as e:
            raise e
        except Exception as e:
            raise e