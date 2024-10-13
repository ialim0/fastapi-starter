from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models import User, UserOAuth
from app.schemas import UserCreate
from app.core.security import SecurityManager
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise UserAlreadyExistsException(user.email)

        hashed_password = SecurityManager().get_password_hash(user.password)
        db_user = User(
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password
        )

        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
        except IntegrityError:
            db.rollback()
            raise DatabaseErrorException(user.email)

        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        user = db.query(User).filter(User.email == email).first()
        if not user or not SecurityManager().verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def get_or_create_oauth_user(db: Session, email: str, oauth_provider: str, oauth_user_id: str, full_name: str = None) -> User:
        logger.info(f"Getting or creating OAuth user: email={email}, provider={oauth_provider}, oauth_user_id={oauth_user_id}")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            logger.info(f"Creating new user for email: {email}")
            hashed_password = SecurityManager().get_password_hash("oauth-placeholder")
            user = User(
                email=email,
                full_name=full_name or "OAuth User",
                hashed_password=hashed_password
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"New user created: {user.id}")

        user_oauth = UserService._get_user_oauth(db, user.id, oauth_provider)

        if not user_oauth:
            logger.info(f"Linking new OAuth provider {oauth_provider} to user {user.id}")
            user_oauth = UserOAuth(
                user_id=user.id,
                oauth_provider=oauth_provider,
                oauth_user_id=oauth_user_id
            )
            db.add(user_oauth)
            try:
                db.commit()
                db.refresh(user_oauth)
                logger.info(f"OAuth provider {oauth_provider} linked to user {user.id}")
            except IntegrityError as e:
                logger.error(f"Failed to link OAuth provider: {str(e)}")
                db.rollback()
                raise HTTPException(status_code=500, detail="Failed to link OAuth provider")
        else:
            logger.info(f"OAuth provider {oauth_provider} already linked to user {user.id}")

        return user

    @staticmethod
    def _get_user_oauth(db: Session, user_id: int, oauth_provider: str) -> UserOAuth:
        return db.query(UserOAuth).filter(
            UserOAuth.user_id == user_id, UserOAuth.oauth_provider == oauth_provider
        ).first()

class UserAlreadyExistsException(HTTPException):
    def __init__(self, email: str):
        super().__init__(status_code=400, detail=f"A user with email '{email}' already exists.")

class DatabaseErrorException(HTTPException):
    def __init__(self, email: str):
        super().__init__(status_code=500, detail=f"Failed to create user with email '{email}' due to a database error.")
