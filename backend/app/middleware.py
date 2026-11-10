from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .models import RateLimit, User
from .config import settings

def check_rate_limit(user: User, db: Session) -> bool:
    # Admin Override for designated admin email or is_admin flag
    if user.is_admin or user.email == settings.ADMIN_EMAIL:
        return True

    today = date.today().isoformat()
    usage = db.query(RateLimit).filter(RateLimit.user_id == user.id, RateLimit.date == today).first()

    if usage:
        if usage.requests_count >= 30:
            raise HTTPException(status_code=429, detail="Daily rate limit exceeded")
        usage.requests_count += 1
    else:
        try:
            usage = RateLimit(user_id=user.id, date=today, requests_count=1)
            db.add(usage)
            db.commit()
            return True
        except Exception:
            # Handle race condition where another concurrent worker created the record
            db.rollback()
            usage = db.query(RateLimit).filter(RateLimit.user_id == user.id, RateLimit.date == today).first()
            if usage:
                if usage.requests_count >= 30:
                    raise HTTPException(status_code=429, detail="Daily rate limit exceeded")
                usage.requests_count += 1

    db.commit()
    return True
