import sqlalchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.schema import ForeignKeyConstraint
from sqlalchemy_utils.types.password import PasswordType

from data.db.init_db import ModelBase
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_utils import force_auto_coercion


class Admins(ModelBase):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, unique=True)
    is_active = Column(Boolean)

    ForeignKeyConstraint(
        ('user_id',), ['users.id']
    )

