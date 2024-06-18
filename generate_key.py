import os

# Generate a random 24-byte secret key
secret_key = os.urandom(24)
print(secret_key.hex())
