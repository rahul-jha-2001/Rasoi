
from .logger import Logger  
from grpc_interceptor.exceptions import GrpcException,Unauthenticated,FailedPrecondition
import functools
import grpc

logger = Logger("GRPC_service")
# def check_access(subject:str,roles:list[str],require_URL_check = True):
#     def decorator(func):
#         def wrapper(self, request, context):
#             metadata = dict(context.invocation_metadata() or [])
#             role = metadata.get("role")

#             if not role:
#                 logger.warning("Missing role in metadata")
#                 raise Unauthenticated("Role missing from metadata")

#             if role == "internal":
#                 # TODO: Add internal service verification here
#                 return func(self, request, context)

#             if role not in roles:
#                 logger.warning(f"Unauthorized role: {role}")
#                 raise Unauthenticated(f"Unauthorized role: {role}")

#             # Role-specific access checks
#             try:
#                 if role == "store":
#                     if not require_URL_check:
#                         return func(self, request, context)
#                     store_uuid_in_token = metadata["store_uuid"]
#                     if not getattr(request, "store_uuid", None):
#                         logger.warning("Store UUID missing in request")
#                         raise Unauthenticated("Store UUID is missing in the request")
#                     if store_uuid_in_token != getattr(request, "store_uuid", None):
#                         logger.warning("Store UUID mismatch")
#                         raise Unauthenticated("Store UUID does not match token")

#                 elif role == "user":
#                     if not require_URL_check:
#                         return func(self, request, context)
#                     phone_in_token = metadata["user_phone_no"]
#                     if not getattr(request, "user_phone_no", None):
#                         logger.warning("User phone number missing in request")
#                         raise Unauthenticated("User phone number is missing in the request")
#                     if phone_in_token != getattr(request, "user_phone_no", None):
#                         logger.warning("User phone mismatch")
#                         raise Unauthenticated("User phone does not match token")

#             except KeyError as e:
#                 logger.warning(f"Missing required metadata for role '{role}': {e}")
#                 raise Unauthenticated(f"Missing metadata: {e}")

#             return func(self, request, context)
#         return wrapper
#     return decorator


def check_access(expected_type: str,
                 allowed_roles: list[str],
                 require_resource_match: bool = True):
    """
    :param expected_type: "store" or "customer"
    :param allowed_roles: e.g. ["admin","staff"] or ["customer"]
    :param require_resource_match: if True, enforce store/customer ID match
    """
    def decorator(handler):
        @functools.wraps(handler)
        def wrapper(self, request, context):
            meta = dict(context.invocation_metadata() or [])
            typ  = meta.get("type")    # e.g. "store","customer","internal"
            role = meta.get("role")

            # 1) internal services bypass all checks
            if typ == "internal":
                return handler(self, request, context)

            # 2) ensure the right actor type
            if typ != expected_type:
                raise Unauthenticated(
                    grpc.StatusCode.PERMISSION_DENIED,
                    f"Expected actor type '{expected_type}', got '{typ}'"
                )

            # 3) ensure the role is allowed
            if role not in allowed_roles:
                raise Unauthenticated(
                    grpc.StatusCode.PERMISSION_DENIED,
                    f"Role '{role}' not in allowed roles {allowed_roles}"
                )

            # 4) optional enforcement of resource‐ID matching
            if require_resource_match:
                if typ == "store":
                    token_stores = meta.get("stores", [])
                    req_uuid     = getattr(request, "store_uuid", None)
                    if not req_uuid or req_uuid not in token_stores:
                        raise Unauthenticated(
                            grpc.StatusCode.PERMISSION_DENIED,
                            "Store UUID mismatch or missing"
                        )

                elif typ == "customer":
                    token_phone = meta.get("phone")
                    req_phone   = getattr(request, "user_phone_no", None)
                    if not req_phone or req_phone != token_phone:
                        raise Unauthenticated(
                            "User phone number mismatch or missing"
                        )

            # all checks passed
            return handler(self, request, context)

        return wrapper
    return decorator
