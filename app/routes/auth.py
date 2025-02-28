from fastapi import APIRouter, HTTPException
import boto3, json
from app.core.config import settings
from app.models.auth import SignupRequest, LoginRequest, ConfirmUserRequest
from supabase import create_client

auth_router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

cognito = boto3.client("cognito-idp", region_name=settings.AWS_REGION)
sqs = boto3.client("sqs", region_name=settings.AWS_REGION)
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

@auth_router.post("/signup")
def signup(user: SignupRequest):
    try:
        response = cognito.sign_up(
            ClientId=settings.COGNITO_CLIENT_ID,
            Username=user.email,
            Password=user.password,
            UserAttributes=[
                {"Name": "email", "Value": user.email},
                {"Name": "name", "Value": user.full_name},
                {"Name": "phone_number", "Value": user.phone_number},
            ]
        )
        user_id = response["UserSub"]
        supabase.table("users").insert({
            "id": user_id,
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "status": "UNCONFIRMED"
        }).execute()

        return {"message": "Signup successful! Verify your email.", "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.post("/confirm")
def confirm_signup(data: ConfirmUserRequest):
    try:
        cognito.confirm_sign_up(
            ClientId=settings.COGNITO_CLIENT_ID,
            Username=data.email,
            ConfirmationCode=data.confirmation_code
        )

        supabase.table("users").update({"status": "CONFIRMED"}).eq("email", data.email).execute()

        sqs.send_message(
            QueueUrl=settings.AWS_SQS_QUEUE_URL,
            MessageBody=json.dumps({"event": "USER_CONFIRMED", "email": data.email})
        )

        return {"message": "User confirmed!"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.post("/login")
def login(credentials: LoginRequest):
    try:
        res = cognito.initiate_auth(
            ClientId=settings.COGNITO_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": credentials.email,
                "PASSWORD": credentials.password
            }
        )

        return res["AuthenticationResult"]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
