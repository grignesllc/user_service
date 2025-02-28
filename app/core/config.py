from pydantic import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    COGNITO_USER_POOL_ID: str
    COGNITO_CLIENT_ID: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    AWS_SQS_QUEUE_URL: str

settings = Settings()
