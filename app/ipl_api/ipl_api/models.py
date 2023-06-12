from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

Base = declarative_base()

class Regions(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(String(33), default=None)
    def __repr__(self):
       return "<Regions(name='%s')>" % (self.name)

class Serveurs(Base):
    __tablename__ = 'serveurs'

    id = Column(Integer, primary_key=True)
    id_regions = Column(Integer, ForeignKey("regions.id"))
    name = Column(String(50), default=None)
    ip_address = Column(String(13), default=None)
    def __repr__(self):
        return "<Serveurs(name='%s', ip_address='%s', id_regions='%s')>" % (self.name, self.ip_address, self.id_regions)

class Cpl(Base):
    __tablename__ = 'cpl'

    uid = Column(String(50), primary_key=True)
    name = Column(String(30),default=None)
    def __repr__(self):
        return "<Cpl(name='%s')>" % (self.name)

class Relations(Base):
    __tablename__= 'relations'

    id = Column(Integer, primary_key=True)
    uid_cpl = Column(String, ForeignKey("cpl.uid"))
    id_serveurs = Column(Integer, ForeignKey("serveurs.id"))
    def __repr__(self):
        return "<Relations(uid_cpl='%s', id_serveur='%s')>" % (self.uid_cpl, self.id_serveurs)
