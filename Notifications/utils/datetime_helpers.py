from google.protobuf.timestamp_pb2 import Timestamp
from django.utils import timezone
from datetime import datetime
from typing import Optional, Union

def proto_to_django(
    timestamp: Optional[Timestamp]
) -> Optional[datetime]:
    """
    Convert Protobuf Timestamp to Django timezone-aware datetime.
    
    Args:
        timestamp: Protobuf Timestamp object or None
        
    Returns:
        Timezone-aware datetime object or None if input is None
    """
    if not timestamp:
        return None
        
    dt = timezone.datetime.fromtimestamp(timestamp.seconds, tz=timezone.utc)
    return dt.replace(microsecond=timestamp.nanos // 1000)  # Convert nanoseconds to microseconds


def django_to_proto(
    dt: Optional[Union[datetime, str]]
) -> Optional[Timestamp]:
    """
    Convert Django datetime or ISO string to Protobuf Timestamp.
    
    Args:
        dt: Django datetime object, ISO format string, or None
        
    Returns:
        Protobuf Timestamp object or None if input is None
    """
    if dt is None:
        return None

    # Ensure datetime is timezone-aware (convert to UTC if needed)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)  # Convert to UTC

    # Convert to Protobuf Timestamp
    timestamp = Timestamp()
    timestamp.seconds = int(dt.timestamp())  # Get seconds since epoch
    timestamp.nanos = dt.microsecond * 1000  # Convert microseconds to nanoseconds
    return timestamp

def now_proto() -> Timestamp:
    """
    Get current time as Protobuf Timestamp.
    
    Returns:
        Protobuf Timestamp object set to current time
    """
    return django_to_proto(timezone.now())

