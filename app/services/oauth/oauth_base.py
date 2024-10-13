from abc import ABC, abstractmethod
from typing import Dict

class OAuthProvider(ABC):
    def __init__(self):
        self.client_id = self.get_client_id()
        self.client_secret = self.get_client_secret()
        self.redirect_uri = self.get_redirect_uri()

    @abstractmethod
    def get_client_id(self) -> str:
        pass

    @abstractmethod
    def get_client_secret(self) -> str:
        pass

    @abstractmethod
    def get_redirect_uri(self) -> str:
        pass

    @abstractmethod
    def get_auth_url(self) -> str:
        pass

    @abstractmethod
    def get_token_url(self) -> str:
        pass

    @abstractmethod
    def get_user_info_url(self) -> str:
        pass

    @abstractmethod
    def get_scopes(self) -> str:
        pass

    @abstractmethod
    def generate_auth_header(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def process_user_data(self, user_data: dict) -> dict:
        pass
