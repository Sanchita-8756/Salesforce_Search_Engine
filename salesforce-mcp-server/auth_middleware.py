"""
Authentication middleware for Salesforce MCP server.
"""
import os
import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.requests import Request


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth0_domain: str):
        super().__init__(app)
        self.auth0_domain = auth0_domain
        self.public_paths = {"/login", "/callback", "/static"}

    async def dispatch(self, request: Request, call_next):
        # Allow public paths
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)

        # Check for auth token in localStorage (handled by frontend)
        # For API endpoints, check Authorization header
        if request.url.path.startswith("/sse") or request.url.path.startswith("/messages"):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return RedirectResponse(url="/login")
            
            try:
                token = auth_header.split(" ")[1]
                # Verify JWT token (simplified - in production, verify signature)
                decoded = jwt.decode(token, options={"verify_signature": False})
                request.state.user = decoded
            except jwt.InvalidTokenError:
                return RedirectResponse(url="/login")

        return await call_next(request)