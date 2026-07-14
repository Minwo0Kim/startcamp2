from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func

from .database import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contenttypeid = Column(String(10), nullable=False)
    title = Column(String(255), nullable=False)
    addr1 = Column(String(512), nullable=False)
    firstimage = Column(String(1024), nullable=True)
    mapx = Column(String(50), nullable=False)
    mapy = Column(String(50), nullable=False)
    cat3 = Column(String(20), nullable=True)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String(100), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True) #routes 테이블의 id 참조
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
