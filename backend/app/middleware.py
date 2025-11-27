from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from datetime import date
from .database import SessionLocal
from .models import RateLimit, User
from .config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only rate limit prediction endpoints
        if request.url.path in ["/predict", "/simulate-match"]:
            # Extract user from JWT (simplified: assume auth dependency runs inside route, 
            # but for global middleware we need to peek at header or use dependency injection in route)
            # STRATEGY: We will enforce rate limits inside the route dependency for cleanliness
            # This middleware just adds DB session to request state if needed.
            pass
        
        response = await call_next(request)
        return response

def check_rate_limit(user: User, db: Session):
    # Admin Override
    if user.email == settings.ADMIN_EMAIL:
        return True
        
    today = date.today().isoformat()
    usage = db.query(RateLimit).filter(RateLimit.user_id == user.id, RateLimit.date == today).first()
    
    if usage:
        if usage.requests_count >= 30:
            raise HTTPException(status_code=429, detail="Daily rate limit exceeded")
        usage.requests_count += 1
    else:
        usage = RateLimit(user_id=user.id, date=today, requests_count=1)
        db.add(usage)
    
    db.commit()
    return True
