import csv
import time
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


engine = create_engine('sqlite:///timesheet.db', echo=True)
Base = declarative_base()



class TimesheetArchive(Base):

    __tablename__ = 'timesheet_archive'

    id = Column(Integer, primary_key=True)
    name = Column(String, default='archive')
    created_date = Column(DateTime, default=datetime.now)


class Timesheet(Base):
    __tablename__ = 'timesheets'

    id = Column(Integer, primary_key=True)
    name = Column(String, default='untitled')
    created_date = Column(DateTime, nullable=False, default=datetime.now)
    total_hours = Column(Integer, default=0)

    timesheet_archive_id = Column(Integer, ForeignKey('timesheet_archive.id'))
    timesheet_archive = relationship('TimesheetArchive', backref=backref('timesheets', order_by=id))



class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    checkin_time = Column(DateTime)
    checkout_time = Column(DateTime, nullable=True)
    task = Column(String, nullable=True)
    timesheet_id = Column(Integer, ForeignKey('timesheets.id'))
    timesheet = relationship('Timesheet', backref=backref('entries', order_by=id))



Base.metadata.create_all(engine)
