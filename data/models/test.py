from data.db.init_db import ModelBase
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship


class TestTable(ModelBase):
    __tablename__ = "test"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
