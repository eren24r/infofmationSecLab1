from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.security import get_current_user

router = APIRouter(prefix="/api", tags=["Data"])


@router.get("/data", response_model=List[UserResponse])
def get_users_data(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    users = db.query(User).all()
    return users
