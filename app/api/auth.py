
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging
from app.models.user import User
from app.db import get_db
from app.schemas import UserCreate, UserOut, Token, OAuthURLResponse, LoginRequest, LoginResponse
from app.services.user import UserService
from app.core.security import SecurityManager
from app.services.oauth.oauth import OAuthService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthRouter:
    def __init__(self):
        self.router = APIRouter()
        self.security_manager = SecurityManager()
        self.user_service = UserService()
        self.oauth_service = OAuthService()

        self._register_routes()

    def _register_routes(self):
        self.router.post("/register", response_model=UserOut, status_code=201)(self.register_user)
        self.router.post("/login", response_model=LoginResponse)(self.login_user)
        self.router.get("/{provider}/url", response_model=OAuthURLResponse)(self.get_oauth_url)
        self.router.get("/{provider}/callback", response_model=Token)(self.oauth_callback)

    def create_token_response(self, email: str) -> Token:
        access_token = self.security_manager.create_access_token({"sub": email})
        return Token(access_token=access_token, token_type="bearer")

    async def register_user(self, user: UserCreate, db: Session = Depends(get_db)):
        try:
            return self.user_service.create_user(db, user)
        except ValueError as e:
            logger.error(f"Registration failed for user {user.email[:5]}****: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    async def login_user(self, login_data: LoginRequest, db: Session = Depends(get_db)):
        try:
            user = self.user_service.authenticate_user(db, login_data.email, login_data.password)
            if not user:
                logger.warning(f"Failed login attempt for {login_data.email[:5]}****: Invalid credentials")
                raise HTTPException(status_code=400, detail="Invalid credentials")
            logger.info(f"User {login_data.email[:5]}**** successfully logged in")
            return self.create_token_response(user.email)
        except ValueError as e:
            logger.warning(f"Failed login attempt for {login_data.email[:5]}****")
            raise HTTPException(status_code=400, detail=str(e))

    async def get_oauth_url(self, provider: str = Path(..., description="OAuth provider name")):
        try:
            oauth_url = await self.oauth_service.get_oauth_login_url(provider)
            logger.info(f"Generated OAuth URL for provider: {provider}")
            return OAuthURLResponse(url=oauth_url)
        except Exception as e:
            logger.error(f"Failed to generate OAuth URL for {provider}: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate OAuth login URL")

    async def oauth_callback(
        self,
        provider: str = Path(..., description="OAuth provider name"),
        code: Optional[str] = Query(None, description="Authorization code from the OAuth provider"),
        db: Session = Depends(get_db)
    ):
        if not code:
            logger.error(f"Missing authorization code for {provider}")
            raise HTTPException(status_code=400, detail="Authorization code not provided")

        try:
            logger.info(f"Exchanging code for access token with {provider}")
            token_data = await self.oauth_service.exchange_code_for_token(provider, code)

            if "access_token" not in token_data:
                logger.error(f"Failed to retrieve access token from {provider}")
                raise HTTPException(status_code=400, detail="Failed to retrieve access token")

            logger.info(f"Fetching user data from {provider}")
            user_data = await self.oauth_service.get_oauth_user_data(provider, token_data['access_token'])

            if "email" not in user_data:
                logger.error(f"Email not provided by {provider}")
                raise HTTPException(status_code=400, detail="Email not provided by the OAuth provider")

            logger.info(f"Creating or updating user for {provider}")
            user = self.user_service.get_or_create_oauth_user(
                db, user_data["email"], provider, user_data["id"], user_data.get("name")
            )

            return self.create_token_response(user.email)

        except Exception as e:
            logger.exception(f"Error during OAuth callback for {provider}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to authenticate with {provider}")


auth_router = AuthRouter().router
