import os

# Redis Cache Constants
CACHE_TTL = int(os.getenv("CACHE_TTL"))  # 5 minutes
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# PostgreSQL Constants
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Security
JWT_SECRET = os.getenv("SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# External APIs
ITOP_URL = os.getenv("ITOP_URL", "https://itop.anptic.bf/webservices/rest.php")
ITOP_USER = os.getenv("ITOP_USER", "api_user")
ITOP_PASS = os.getenv("ITOP_PASS", "api_password")
