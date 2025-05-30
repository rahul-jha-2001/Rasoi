import io
from typing import Optional, Tuple
from PIL import Image
import boto3
from botocore.exceptions import NoCredentialsError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageHandler:
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

    @staticmethod
    def check_size(bytes_data: bytes) -> float:
        """
        Check the size of bytes data in MB.
        """
        if not bytes_data:
            raise ValueError("Empty bytes data provided")
        return len(bytes_data) / (1024 * 1024)

    @staticmethod
    def bytes_to_image(bytes_data: bytes) -> Image.Image:
        """
        Convert bytes data to a PIL Image object.
        """
        if not bytes_data:
            raise ValueError("Empty bytes data provided")
        try:
            return Image.open(io.BytesIO(bytes_data))
        except Exception as e:
            logger.error("Failed to convert bytes to image: %s", str(e))
            raise ValueError(f"Failed to convert bytes to image: {str(e)}")

    @staticmethod
    def check_extension(bytes_data: bytes) -> Optional[str]:
        """
        Detect the file extension from image bytes data.
        """
        if not bytes_data:
            raise ValueError("Empty bytes data provided")
        try:
            image = Image.open(io.BytesIO(bytes_data))
            return f".{image.format.lower()}"
        except Exception as e:
            logger.warning("Failed to detect image extension: %s", str(e))
            return None

    @staticmethod
    def _create_s3_client(aws_access_key: Optional[str], aws_secret_key: Optional[str], region_name: Optional[str]):
        """
        Create an S3 client.
        """
        try:
            if aws_access_key and aws_secret_key:
                return boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=region_name
                )
            return boto3.client('s3', region_name=region_name)
        except Exception as e:
            logger.error("Failed to create S3 client: %s", str(e))
            raise

    @staticmethod
    def upload_to_s3(
        bytes_data: bytes,
        bucket_name: str,
        object_name: Optional[str] = None,
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
        region_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Upload image bytes to an S3 bucket.
        """
        if not bytes_data:
            return False, "Empty bytes data provided"
        if not bucket_name:
            return False, "Bucket name is required"

        # Detect extension
        extension = ImageHandler.check_extension(bytes_data)
        if not extension:
            return False, "Unknown image extension"
        if extension not in ImageHandler.ALLOWED_EXTENSIONS:
            return False, f"{extension} is not allowed"

        # Generate object name if not provided
        object_name = f"{object_name or 'image'}{extension}"

        # Create S3 client
        s3_client = ImageHandler._create_s3_client(aws_access_key, aws_secret_key, region_name)

        try:
            # Upload the file
            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=bytes_data,
                ContentType=f"image/{extension[1:]}"
            )
            # Generate the URL
            url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{object_name}"
            return True, url
        except NoCredentialsError:
            logger.error("AWS credentials not provided or invalid")
            return False, "AWS credentials not provided or invalid"
        except Exception as e:
            logger.error("Failed to upload to S3: %s", str(e))
            return False, f"Failed to upload to S3: {str(e)}"
