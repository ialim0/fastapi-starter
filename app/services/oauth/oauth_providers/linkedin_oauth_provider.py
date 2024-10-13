from app.services.oauth.oauth_base import OAuthProvider
from app.config import settings
from typing import Dict


class LinkedInOAuthProvider(OAuthProvider):
    def get_client_id(self) -> str:
        return settings.LINKEDIN_CLIENT_ID

    def get_client_secret(self) -> str:
        return settings.LINKEDIN_CLIENT_SECRET

    def get_redirect_uri(self) -> str:
        return settings.LINKEDIN_REDIRECT_URI

    def get_auth_url(self) -> str:
        return "https://www.linkedin.com/oauth/v2/authorization?"

    def get_token_url(self) -> str:
        return "https://www.linkedin.com/oauth/v2/accessToken"

    def get_user_info_url(self) -> str:
        return "https://api.linkedin.com/v2/userinfo"

    def get_scopes(self) -> str:
        return "openid profile email"

    def generate_auth_header(self) -> Dict[str, str]:
        return {"Content-Type": "application/x-www-form-urlencoded"}

    def process_user_data(self, user_data: dict) -> dict:
        return {
            "id": user_data.get("sub"),
            "email": user_data.get("email"),
            "name": user_data.get("name", "LinkedIn User")
        }
