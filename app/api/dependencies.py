from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Gets the current authenticated user based on the provided token
    In a real application, this would verify the token
    """
    # This is a stub - in a real app you would verify JWT tokens
    # and fetch the user from the database
    user_id = "user_from_token"  # Mock user ID
    return user_id

async def get_api_version(x_api_version: Optional[str] = Header(None)):
    """
    Get API version from header if specified
    This can be used to override the version in the URL
    """
    return x_api_version or "default"

async def verify_api_key(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Optional dependency to verify API key for protected endpoints
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="API key is required"
        )
    
    # In a real app, you would validate the API key against your database/service
    # This is just a placeholder implementation
    if api_key != "your_valid_api_key":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return api_key
