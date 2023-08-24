from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types.password import PasswordType

from data.db.init_db import ModelBase
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_utils import force_auto_coercion
from passlib.hash import pbkdf2_sha256
import sqlalchemy
force_auto_coercion()


class Users(ModelBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True)
    _password = Column(String)
    one_time_password = Column(String, default=None)  # One time password, to disallow repeated use of reset confirmation link.
    date_created = Column(sqlalchemy.types.DateTime)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = pbkdf2_sha256.hash(plaintext)

    # Although this should be in a dbapi function, since we want to use the
    # same algorithm and method for encoding as well as decoding, we will
    # keep this here
    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self._password)

