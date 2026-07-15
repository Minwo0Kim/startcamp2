from sqlalchemy import Column, DateTime, Integer, String, Text, func

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


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    password = Column(String(100), nullable=False)
    route_json = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())