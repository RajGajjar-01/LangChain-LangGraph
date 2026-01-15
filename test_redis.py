import redis

# Connect to Redis (same network, so host is "redis")
r = redis.Redis(host="localhost", port=6379, db=0)

# Set a value
r.set("greeting", "Hello from Python!")

# Get the value
value = r.get("greeting")

print("Stored value:", value.decode("utf-8"))
