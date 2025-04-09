from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.database import Base
import datetime

class RiverRaceEntry(Base):
    __tablename__ = "river_race"

    id = Column(Integer, primary_key=True, index=True)
    week = Column(String, index=True)
    tag = Column(String, index=True)
    name = Column(String)
    fame = Column(Integer)
    decks_used = Column(Integer)
    decks_possible = Column(Integer)
    excused = Column(Boolean, default=False)
    role = Column(String)
    date_collected = Column(DateTime, default=datetime.datetime.utcnow)
