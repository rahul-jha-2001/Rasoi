import uuid

def is_valid_uuid(uuid_string):
    if isinstance(uuid_string, uuid.UUID):
       
        return True
    
    if isinstance(uuid_string, str):
        try:

            # Attempt to create a UUID object from the string
            val = uuid.UUID(uuid_string, version=4)  # version=4 for random UUIDs
        except ValueError:
            return False  # Not a valid UUID
        return str(val) == uuid_string
  # The input is already a UUID object