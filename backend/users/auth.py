from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from backend.users.manager import get_user_manager

# JWT authentication settings
SECRET = "YOUR_SECRET_KEY_CHANGE_THIS_IN_PRODUCTION"
LIFETIME_SECONDS = 3600  # 1 hour

# Bearer transport for token
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# JWT strategy for token generation and validation
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=LIFETIME_SECONDS)

# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
