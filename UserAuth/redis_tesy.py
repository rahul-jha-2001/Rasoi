import redis
import redis.connection
from uuid import uuid4
from datetime import datetime
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
# Data to store

# Save a dictionary
OTP_key = f"OTP:{uuid4()}"
# data = {"UserName": "Alice", "PhoneNo": "9977636633", "OTP_refrences":f"{OTP_key}","created_at":f"{datetime.now()}"}
# r.expire(OTP_key, 20)
# r.hset(OTP_key, mapping=data,)

# Retrieve the dictionary
retrieved_data = r.hgetall(OTP_key)
print(retrieved_data)  # Output: {'name': 'Alice', 'age': '30', 'city': 'New York'}

# Access a specific field# Output: Alice