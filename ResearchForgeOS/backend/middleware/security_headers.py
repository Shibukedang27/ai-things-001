from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, hsts_seconds: int, enabled_hsts: bool) -> None:
        super().__init__(app)
        self.hsts_seconds = hsts_seconds
        self.enabled_hsts = enabled_hsts

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        if self.enabled_hsts and self.hsts_seconds > 0:
            response.headers.setdefault("Strict-Transport-Security", f"max-age={self.hsts_seconds}; includeSubDomains")
        return response
