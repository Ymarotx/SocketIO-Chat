from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from .database import Base

class Users(Base):
    __tablename__ = 'users_socket_io'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    sid: Mapped[str]

    __table_args__ = (UniqueConstraint('id',name='unique_user_id_socket_io'),)



