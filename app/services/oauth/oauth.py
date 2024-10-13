# app/services/oauth/oauth.py

from fastapi import HTTPException, Path, Query, Depends
from httpx import AsyncClient
from app.config import settings
import logging
from sqlalchemy.orm import Session  
from app.services.oauth.oauth_providers import GoogleOAuthProvider, GitHubOAuthProvider, LinkedInOAuthProvider
from app.services.oauth.oauth_base import OAuthProvider
from app.db import get_db
from typing import Optional
from app.models import User, UserOAuth
from app.core.security import SecurityManager  
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

class OAuthProviderFactory:
    @staticmethod
    def get_provider(provider: str) -> OAuthProvider:
        if provider == "google":
            return GoogleOAuthProvider()
        elif provider == "github":
            return GitHubOAuthProvider()
        elif provider == "linkedin":
            return LinkedInOAuthProvider()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported OAuth provider: {provider}")

class OAuthService:
    @staticmethod
    async def get_oauth_login_url(provider: str) -> str:
        oauth_provider = OAuthProviderFactory.get_provider(provider)
        return (
            f"{oauth_provider.get_auth_url()}response_type=code&"
            f"client_id={oauth_provider.client_id}&"
            f"redirect_uri={oauth_provider.redirect_uri}&"
            f"scope={oauth_provider.get_scopes()}"
        )

    @staticmethod
    async def exchange_code_for_token(provider: str, code: str) -> dict:
        oauth_provider = OAuthProviderFactory.get_provider(provider)
        data = {
            "code": code,
            "client_id": oauth_provider.client_id,
            "client_secret": oauth_provider.client_secret,
            "redirect_uri": oauth_provider.redirect_uri,
            "grant_type": "authorization_code",
        }
        headers = oauth_provider.generate_auth_header()

        async with AsyncClient() as client:
            response = await client.post(oauth_provider.get_token_url(), data=data, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to exchange code for token with {provider}: {response.text}")

            try:
                return response.json()
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid response format from {provider}: {response.text}")

    @staticmethod
    async def get_oauth_user_data(provider: str, token: str) -> dict:
        oauth_provider = OAuthProviderFactory.get_provider(provider)
        async with AsyncClient() as client:
            response = await client.get(oauth_provider.get_user_info_url(), headers={"Authorization": f"Bearer {token}"})
            if response.status_code != 200:
                logger.error(f"Failed to fetch user data from {provider}. Status: {response.status_code}, Response: {response.text}")
                raise HTTPException(status_code=400, detail=f"Failed to fetch user data from {provider}")

            user_data = response.json()
            logger.info(f"Raw user data from {provider}: {user_data}")

            # Process user data differently based on provider
            processed_user_data = await oauth_provider.process_user_data(user_data, token) if provider == "github" else oauth_provider.process_user_data(user_data)
            logger.info(f"Processed user data for {provider}: {processed_user_data}")
            return processed_user_data

    @staticmethod
    async def oauth_callback(
        provider: str = Path(..., description="OAuth provider name"),
        code: Optional[str] = Query(None, description="Authorization code from the OAuth provider"),
        db: Session = Depends(get_db)
    ):
        if not code:
            logger.error(f"Missing authorization code for {provider}")
            raise HTTPException(status_code=400, detail="Authorization code not provided")

        try:
            token_data = await OAuthService.exchange_code_for_token(provider, code)

            user_data = await OAuthService.get_oauth_user_data(provider, token_data['access_token'])

            logger.info(f"User authenticated via {provider}: {user_data['email'][:5]}****")

            user = await OAuthService.create_or_update_user(db, user_data)

            return OAuthService.create_token_response(user_data["email"])

        except Exception as e:
            logger.exception(f"Error during OAuth callback for {provider}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to authenticate with {provider}")

    @staticmethod
    async def create_or_update_user(db: Session, user_data: dict) -> User:
        oauth_provider = user_data.get("oauth_provider")
        oauth_user_id = user_data.get("oauth_user_id")
        email = user_data.get("email")
        full_name = user_data.get("name")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            random_password = SecurityManager().generate_random_password(12)
            hashed_password = SecurityManager().get_password_hash(random_password)  
            user = User(
                email=email,
                full_name=full_name or "OAuth User",
                hashed_password=hashed_password,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"Generated random password for new user: {random_password}")

        if oauth_provider and oauth_user_id:
            user_oauth = db.query(UserOAuth).filter(
                UserOAuth.user_id == user.id, UserOAuth.oauth_provider == oauth_provider
            ).first()

            if not user_oauth:
                user_oauth = UserOAuth(
                    user_id=user.id,
                    oauth_provider=oauth_provider,
                    oauth_user_id=oauth_user_id
                )
                db.add(user_oauth)
                try:
                    db.commit()
                    db.refresh(user_oauth)
                except IntegrityError as e:
                    db.rollback()
                    raise HTTPException(status_code=500, detail="Failed to link OAuth provider")

        return user 

    @staticmethod
    def create_token_response(email: str) -> dict:
        """Return a token response with the generated token and email."""
        access_token = SecurityManager().create_access_token({"sub": email})
        return {"access_token": access_token, "token_type": "bearer", "email": email}
