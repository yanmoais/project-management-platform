from sqlalchemy import String, Integer, BigInteger, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend_fastapi.db.session import Base
from typing import Optional

class SysDictType(Base):
    """
    字典类型表
    """
    __tablename__ = 'sys_dict_type'

    dict_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dict_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dict_type: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    status: Mapped[int] = mapped_column(Integer, default=1)
    remark: Mapped[Optional[str]] = mapped_column(String(500))
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'dict_id': self.dict_id,
            'dict_name': self.dict_name,
            'dict_type': self.dict_type,
            'status': self.status,
            'remark': self.remark,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None
        }

class SysDictData(Base):
    """
    字典数据表
    """
    __tablename__ = 'sys_dict_data'

    dict_data_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dict_id: Mapped[int] = mapped_column(BigInteger, nullable=False) # Changed from dict_type string to dict_id integer as per sql
    dict_label: Mapped[str] = mapped_column(String(100), nullable=False)
    dict_value: Mapped[str] = mapped_column(String(100), nullable=False)
    dict_sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)
    remark: Mapped[Optional[str]] = mapped_column(String(500))
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'dict_data_id': self.dict_data_id,
            'dict_id': self.dict_id,
            'dict_label': self.dict_label,
            'dict_value': self.dict_value,
            'dict_sort': self.dict_sort,
            'status': self.status,
            'remark': self.remark,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None
        }
