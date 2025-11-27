import argparse
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash
from app.config import settings

def create_admin(password):
    db = SessionLocal()
    email = settings.ADMIN_EMAIL
    user = db.query(User).filter(User.email == email).first()
    if user:
        print(f"Admin {email} already exists.")
        return

    hashed_pw = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_pw, is_admin=True)
    db.add(new_user)
    db.commit()
    print(f"Admin user {email} created.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--password", required=True, help="Admin password")
    args = parser.parse_args()
    create_admin(args.password)
