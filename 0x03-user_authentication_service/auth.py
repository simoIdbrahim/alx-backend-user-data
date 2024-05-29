#!/usr/bin/env python3
"""
Auth class to interact with the authentication db.
"""
import bcrypt
from sqlalchemy.orm.exc import NoResultFound
from typing import Union
from db import DB, User


def _generate_uuid() -> str:
    """ Generates a unique id """
    from uuid import uuid4
    return str(uuid4())


def _hash_password(password: str) -> bytes:
    """ Hashes a password """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


class Auth:
    """ auth class"""
    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """ Register a user """
        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            return self._db.add_user(email, _hash_password(password))
        else:
            raise ValueError("User %s already exists" % email)

    def valid_login(self, email: str, password: str) -> bool:
        """ Validate user login """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False
        return bcrypt.checkpw(password.encode(), user.hashed_password)

    def create_session(self, email: str) -> Union[str, None]:
        """ Create a user session id """
        session_id = _generate_uuid()
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            pass
        else:
            try:
                self._db.update_user(user.id, session_id=session_id)
            except (NoResultFound, ValueError):
                pass
        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """ Get user from session id """
        if session_id is not None:
            try:
                user = self._db.find_user_by(session_id=session_id)
                return user
            except NoResultFound:
                pass
        return None

    def destroy_session(self, user_id: str) -> None:
        """Destroy a user session id
        """
        return self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """ Get reset password token """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError
        reset_token = _generate_uuid()
        try:
            self._db.update_user(user.id, reset_token=reset_token)
        except (NoResultFound, ValueError):
            raise ValueError
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """ Update password """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            password = _hash_password(password)
            self._db.update_user(
                user.id, hashed_password=password, reset_token=None)
        except NoResultFound:
            raise ValueError
        return None
