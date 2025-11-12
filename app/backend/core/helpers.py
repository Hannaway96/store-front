from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

class API_Client(APIClient):
    """Class to mamage Authorization for Test API Clients"""

    def __init__(self):
        super().__init__()

    def get_access_token(self, user):
        """Helper function to get auth tokens for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def authorize(self, user):
        """Helper function to assign different creds to the API requests"""
        token = self.get_access_token(user)
        self.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

