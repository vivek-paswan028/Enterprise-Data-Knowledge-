from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.config.settings import settings
from src.api.schemas import TokenResponse
from src.api.security import create_access_token, hash_password

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Dummy credentials for demonstration/testing
DEMO_USERS = {
    "admin": {"password_hash": hash_password("admin123"), "role": "admin"},
    "engineer": {"password_hash": hash_password("datapulse2026"), "role": "data_engineer"},
    "analyst": {"password_hash": hash_password("analyst123"), "role": "analyst"},
}


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = DEMO_USERS.get(form_data.username)
    if not user or user["password_hash"] != hash_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": form_data.username, "role": user["role"]}
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
