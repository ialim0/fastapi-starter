from app.services.oauth.oauth_base import OAuthProvider
from app.config import settings
from typing import Dict


class GoogleOAuthProvider(OAuthProvider):
    def get_client_id(self) -> str:
        return settings.GOOGLE_CLIENT_ID

    def get_client_secret(self) -> str:
        return settings.GOOGLE_CLIENT_SECRET

    def get_redirect_uri(self) -> str:
        return settings.GOOGLE_REDIRECT_URI

    def get_auth_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth?"

    def get_token_url(self) -> str:
        return "https://oauth2.googleapis.com/token"

    def get_user_info_url(self) -> str:
        return "https://www.googleapis.com/oauth2/v2/userinfo"

    def get_scopes(self) -> str:
        return "openid profile email"

    def generate_auth_header(self) -> Dict[str, str]:
        return {"Content-Type": "application/x-www-form-urlencoded"}

    def process_user_data(self, user_data: dict) -> dict:
        return user_data
