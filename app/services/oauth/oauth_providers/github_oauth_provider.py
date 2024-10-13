from app.services.oauth.oauth_base import OAuthProvider
from app.config import settings
from fastapi import HTTPException
from httpx import AsyncClient
import base64
from typing import Dict


class GitHubOAuthProvider(OAuthProvider):
    def get_client_id(self) -> str:
        return settings.GITHUB_CLIENT_ID

    def get_client_secret(self) -> str:
        return settings.GITHUB_CLIENT_SECRET

    def get_redirect_uri(self) -> str:
        return settings.GITHUB_REDIRECT_URI

    def get_auth_url(self) -> str:
        return "https://github.com/login/oauth/authorize?"

    def get_token_url(self) -> str:
        return "https://github.com/login/oauth/access_token"

    def get_user_info_url(self) -> str:
        return "https://api.github.com/user"

    def get_scopes(self) -> str:
        return "user:email"

    def generate_auth_header(self) -> Dict[str, str]:
        credentials = f"{self.client_id}:{self.client_secret}"
        auth_value = base64.b64encode(credentials.encode()).decode()
        return {"Accept": "application/json", "Authorization": f"Basic {auth_value}"}

    async def process_user_data(self, user_data: dict, token: str) -> dict:
        async with AsyncClient() as client:
            email_url = "https://api.github.com/user/emails"
            email_response = await client.get(email_url, headers={"Authorization": f"Bearer {token}"})
            if email_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch email data from GitHub")
            emails = email_response.json()
            primary_email = next((email for email in emails if email.get("primary")), None)
            if primary_email:
                user_data["email"] = primary_email["email"]
        return user_data
