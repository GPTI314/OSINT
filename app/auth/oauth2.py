"""
OAuth2 authentication with Google and GitHub
"""
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, status
from typing import Dict, Optional
from app.config import settings
import httpx


class OAuth2Handler:
    """Handle OAuth2 authentication flows"""

    def __init__(self):
        self.oauth = OAuth()

        # Configure Google OAuth2
        if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
            self.oauth.register(
                name='google',
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
                client_kwargs={'scope': 'openid email profile'}
            )

        # Configure GitHub OAuth2
        if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
            self.oauth.register(
                name='github',
                client_id=settings.GITHUB_CLIENT_ID,
                client_secret=settings.GITHUB_CLIENT_SECRET,
                access_token_url='https://github.com/login/oauth/access_token',
                authorize_url='https://github.com/login/oauth/authorize',
                api_base_url='https://api.github.com/',
                client_kwargs={'scope': 'user:email'}
            )

    async def get_google_user_info(self, token: str) -> Optional[Dict]:
        """Get user info from Google using access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {token}'}
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to get Google user info: {str(e)}"
            )
        return None

    async def get_github_user_info(self, token: str) -> Optional[Dict]:
        """Get user info from GitHub using access token"""
        try:
            async with httpx.AsyncClient() as client:
                # Get user profile
                response = await client.get(
                    'https://api.github.com/user',
                    headers={'Authorization': f'token {token}'}
                )
                if response.status_code == 200:
                    user_data = response.json()

                    # Get primary email
                    email_response = await client.get(
                        'https://api.github.com/user/emails',
                        headers={'Authorization': f'token {token}'}
                    )
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        primary_email = next(
                            (e['email'] for e in emails if e['primary']),
                            emails[0]['email'] if emails else None
                        )
                        user_data['email'] = primary_email

                    return user_data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to get GitHub user info: {str(e)}"
            )
        return None

    def get_authorization_url(self, provider: str, redirect_uri: str) -> str:
        """Get OAuth2 authorization URL for a provider"""
        if provider == 'google':
            return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=openid%20email%20profile"
        elif provider == 'github':
            return f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={redirect_uri}&scope=user:email"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth2 provider: {provider}"
            )

    async def exchange_code_for_token(self, provider: str, code: str, redirect_uri: str) -> str:
        """Exchange authorization code for access token"""
        if provider == 'google':
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://oauth2.googleapis.com/token',
                    data={
                        'code': code,
                        'client_id': settings.GOOGLE_CLIENT_ID,
                        'client_secret': settings.GOOGLE_CLIENT_SECRET,
                        'redirect_uri': redirect_uri,
                        'grant_type': 'authorization_code'
                    }
                )
                if response.status_code == 200:
                    return response.json()['access_token']

        elif provider == 'github':
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://github.com/login/oauth/access_token',
                    data={
                        'code': code,
                        'client_id': settings.GITHUB_CLIENT_ID,
                        'client_secret': settings.GITHUB_CLIENT_SECRET,
                        'redirect_uri': redirect_uri
                    },
                    headers={'Accept': 'application/json'}
                )
                if response.status_code == 200:
                    return response.json()['access_token']

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to exchange code for token"
        )


# Global OAuth2 handler instance
oauth2_handler = OAuth2Handler()
