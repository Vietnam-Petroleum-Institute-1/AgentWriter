import jwt
from datetime import datetime, timedelta

# Thông tin cần mã hóa
user_id = "phuongpd"
secret_key = "secret"  # Khóa bí mật để mã hóa

# Thời gian hiện tại
now = datetime.utcnow()
now = now + timedelta(hours=7)
# Thời điểm hết hạn (11:00:00)
expiration_time = now + timedelta(hours=1, minutes=0)
exp_timestamp = expiration_time.timestamp()

# Payload của token
payload = {
    'user_id': user_id,
    'exp': exp_timestamp
}
print(payload)

# Tạo JWT token
token = jwt.encode(payload, "96fc0cc6-3531-435d-9279-368691964ed3", algorithm='HS256')

print(f"Generated token: {token}")

token_decode = jwt.decode(token, "96fc0cc6-3531-435d-9279-368691964ed3", algorithms='HS256')
print("decode:", token_decode)




