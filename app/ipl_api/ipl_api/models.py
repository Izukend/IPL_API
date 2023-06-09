from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Regions(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(String(33))
    def __repr__(self):
       return "<Regions(name='%s')>" % (self.name)

class Serveurs(Base):
    __tablename__ = 'serveurs'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    ip_address = Column(String(13))
    def __repr(self):
        return "<Serveurs(name='%s', ip_address='%s')>" % (self.name, self.ip_address)

class Cpl(Base):
    __tablename__ = 'cpl'

    id = Column(Integer, primary_key=True)
    uid = Column(String(50))
    name = Column(String(30))
    def __repr__(self):
        return "<Cpl(uid='%s', name='%s')>" % (self.uid, self.name)
