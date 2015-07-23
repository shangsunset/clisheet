from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, event
from .models import engine, TimesheetArchive

# engine = create_engine('sqlite:///timesheet.db')
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
# Base = declarative_base()

archive = TimesheetArchive()
session.add(archive)
session.commit()
