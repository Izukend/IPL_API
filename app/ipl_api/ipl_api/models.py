from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Regions(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(String(33))
    servers = relationship("Servers", back_populates="region")

    def __repr__(self):
        return "<Regions(name='%s')>" % (self.name)

class Servers(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True)
    id_region = Column(Integer, ForeignKey("regions.id"))
    name = Column(String(50))
    private_ip = Column(String(13))
    public_ip = Column(String(13))
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    version_sw = Column(String(7))

    region = relationship("Regions", back_populates="servers")
    cpl = relationship("Cpl", back_populates="servers")
    relations = relationship("Relations", back_populates="servers")

    def __repr__(self):
        return "<Servers(name='%s', private_ip='%s', id_region='%s')>" % (self.name, self.private_ip, self.id_region)

class Cpl(Base):
    __tablename__ = 'cpl'
    uid = Column(String(50), primary_key=True)
    name = Column(String(30))
    id_servers = Column(Integer, ForeignKey("servers.id"))
    servers = relationship("Servers", back_populates="cpl")
    relations = relationship("Relations", back_populates="cpl")

    def __repr__(self):
        return "<Cpl(name='%s', id_serveur='%s')>" % (self.name, self.id_servers)

class Relations(Base):
    __tablename__ = 'relations'

    id = Column(Integer, primary_key=True)
    uid_cpl = Column(String(50), ForeignKey("cpl.uid"))
    id_servers = Column(Integer, ForeignKey("servers.id"))
    servers = relationship("Servers", back_populates="relations")
    cpl = relationship("Cpl", back_populates="relations")

    def __repr__(self):
        return "<Relations(uid_cpl='%s', id_servers='%s')>" % (self.uid_cpl, self.id_servers)
