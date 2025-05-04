
from .logger import Logger  
from grpc_interceptor.exceptions import GrpcException,Unauthenticated,FailedPrecondition

logger = Logger("GRPC_service")
def check_access(roles:list[str],require_URL_check = True):
    def decorator(func):
        def wrapper(self, request, context):
            metadata = dict(context.invocation_metadata() or [])
            role = metadata.get("role")

            if not role:
                logger.warning("Missing role in metadata")
                raise Unauthenticated("Role missing from metadata")

            if role == "internal":
                # TODO: Add internal service verification here
                return func(self, request, context)

            if role not in roles:
                logger.warning(f"Unauthorized role: {role}")
                raise Unauthenticated(f"Unauthorized role: {role}")

            # Role-specific access checks
            try:
                if role == "store":
                    if not require_URL_check:
                        return func(self, request, context)
                    store_uuid_in_token = metadata["store_uuid"]
                    if not getattr(request, "store_uuid", None):
                        logger.warning("Store UUID missing in request")
                        raise Unauthenticated("Store UUID is missing in the request")
                    if store_uuid_in_token != getattr(request, "store_uuid", None):
                        logger.warning("Store UUID mismatch")
                        raise Unauthenticated("Store UUID does not match token")

                elif role == "user":
                    if not require_URL_check:
                        return func(self, request, context)
                    phone_in_token = metadata["user_phone_no"]
                    if not getattr(request, "user_phone_no", None):
                        logger.warning("User phone number missing in request")
                        raise Unauthenticated("User phone number is missing in the request")
                    if phone_in_token != getattr(request, "user_phone_no", None):
                        logger.warning("User phone mismatch")
                        raise Unauthenticated("User phone does not match token")

            except KeyError as e:
                logger.warning(f"Missing required metadata for role '{role}': {e}")
                raise Unauthenticated(f"Missing metadata: {e}")

            return func(self, request, context)
        return wrapper
    return decorator
