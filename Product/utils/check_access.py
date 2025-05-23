
from .logger import Logger  
from grpc_interceptor.exceptions import GrpcException,Unauthenticated,FailedPrecondition
import functools
import json
import grpc
from grpc import StatusCode
from typing import Sequence, Mapping, Union, Callable, Any

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


def check_access(
    expected_types: Sequence[str],
    allowed_roles: Union[Sequence[str], Mapping[str, Sequence[str]]],
    require_resource_match: bool = True
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    :param expected_types: list of allowed actor types, e.g. ["store", "customer"]
    :param allowed_roles:
        - If a flat list: those roles apply to every type.
        - If a dict: only types present as keys get their roles enforced.
          Types not in the dict (e.g. "customer") skip role enforcement.
    :param require_resource_match: if True, enforce ID/phone matching
    """
    def decorator(handler: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(handler)
        def wrapper(self, request, context) -> Any:
            meta = dict(context.invocation_metadata() or [])
            typ  = meta.get("type")    # e.g. "store","customer","internal"
            role = meta.get("role")

            logger.debug(f"Invocation metadata: {meta}")
            logger.info(f"Actor type: {typ}, Role: {role}")

            # 1) internal actors bypass everything
            if typ == "internal":
                logger.info("Internal actor detected, bypassing checks")
                return handler(self, request, context)

            # 2) ensure actor type is allowed
            if typ not in expected_types:
                logger.warning(f"Unauthorized actor type: {typ}. Expected: {expected_types}")
                raise Unauthenticated(
                    StatusCode.PERMISSION_DENIED,
                    f"Expected actor type in {expected_types}, got '{typ}'"
                )

            logger.info(f"Actor type '{typ}' is allowed")

            # 3) role check
            if isinstance(allowed_roles, Mapping):
                roles_for_type = allowed_roles.get(typ)
                if roles_for_type is not None:
                    logger.info(f"Allowed roles for type '{typ}': {roles_for_type}")
                    if role not in roles_for_type:
                        logger.warning(f"Unauthorized role '{role}' for type '{typ}'")
                        raise Unauthenticated(
                            StatusCode.PERMISSION_DENIED,
                            f"Role '{role}' not allowed for type '{typ}'"
                        )
            else:
                logger.info(f"Allowed roles (flat list): {allowed_roles}")
                if role not in allowed_roles:
                    logger.warning(f"Unauthorized role '{role}'")
                    raise Unauthenticated(
                        StatusCode.PERMISSION_DENIED,
                        f"Role '{role}' not in allowed roles {allowed_roles}"
                    )

            logger.info(f"Role '{role}' is authorized for type '{typ}'")

            # 4) optional resource matching
            if require_resource_match:
                logger.info("Resource matching is enabled")
 
                if typ == "store":
                    req_uuid = getattr(request, "store_uuid", None)
                    logger.info(f"Request store UUID: {req_uuid}")
                    if  req_uuid is not None:
                        raw = meta.get("store_uuids", "[]")
                        try:
                            token_stores = json.loads(raw)
                            logger.info(f"Token store UUIDs: {token_stores}")
                        except Exception as e:
                            logger.error(f"Error parsing store UUIDs from token: {e}")
                            token_stores = raw.split(",") if raw else []
    
                        if not req_uuid or req_uuid not in token_stores:
                            logger.warning("Store UUID mismatch or missing")
                            raise Unauthenticated(
                                StatusCode.PERMISSION_DENIED,
                                "Store UUID mismatch or missing"
                            )

                elif typ == "customer":
                    token_phone = meta.get("phone")
                    req_phone   = getattr(request, "user_phone_no", None)
                    if req_phone != None:
                        logger.info(f"Token phone: {token_phone}, Request phone: {req_phone}")
                        if not req_phone or req_phone != token_phone:
                            logger.warning("Customer phone number mismatch or missing")
                            raise Unauthenticated(
                                StatusCode.PERMISSION_DENIED,
                                "Customer phone number mismatch or missing"
                            )

            logger.info("All access checks passed")
            return handler(self, request, context)

        return wrapper
    return decorator
