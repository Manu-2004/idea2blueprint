from typing import Optional

from fastapi import Header, HTTPException

from blueprint_agents.auth import AuthStore, User


def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    return authorization.split(" ", 1)[1].strip()


def make_get_current_user(auth_store: AuthStore):
    """Builds the `Depends(...)` callable for protected routes, closed over the app's
    `AuthStore` instance rather than importing it from `app.py` (which would be circular)."""

    def get_current_user(authorization: Optional[str] = Header(default=None)) -> User:
        token = extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(status_code=401, detail="Missing or malformed Authorization header.")
        user = auth_store.get_user_by_token(token)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired session.")
        return user

    return get_current_user
