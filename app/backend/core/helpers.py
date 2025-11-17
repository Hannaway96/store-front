from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

class API_Client(APIClient):
    """Class to mamage Authorization for Test API Clients"""

    def __init__(self):
        super().__init__()

    def create_access_token(self, user):
        """Create a set of Auth Tokens for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def authorize(self, user):
        """Sign all test requests for an authenticated user"""
        token = self.create_access_token(user)
        self.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

