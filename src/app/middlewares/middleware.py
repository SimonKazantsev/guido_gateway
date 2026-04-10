from fastapi import Request


class JWTMiddleware:
    def __init__(self, *args, **kwds):
        pass
    def __call__(self, request: Request, call_next):
        pass
        