from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import User

def create_user(db: Session, username: str, email: str, customer_type: str):
    user = User(username=username, email=email, customer_type=customer_type)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
