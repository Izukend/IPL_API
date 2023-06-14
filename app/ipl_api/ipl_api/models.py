from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Regions(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(String(33))
    serveurs = relationship("Serveurs", back_populates="region")

    def __repr__(self):
        return "<Regions(name='%s')>" % (self.name)

class Serveurs(Base):
    __tablename__ = 'serveurs'

    id = Column(Integer, primary_key=True)
    id_region = Column(Integer, ForeignKey("regions.id"))
    name = Column(String(50))
    private_ip_ = Column(String(13))
    public_ip_ = Column(String(13))
    last_seen = Column(DateTime(timezone=True),server_default=func.now())
    version_sw = Column(String(7))

    region = relationship("Regions", back_populates="serveurs")
    cpl = relationship("Cpl", back_populates="serveurs")
    relations = relationship("Relations", back_populates="serveurs")

    def __repr__(self):
        return "<Serveurs(name='%s', ip_address='%s', id_region='%s')>" % (self.name, self.ip_address, self.id_region)



class Cpl(Base):
    __tablename__ = 'cpl'
    uid = Column(String(50), primary_key=True)
    name = Column(String(30))
    id_serveurs = Column(Integer, ForeignKey("serveurs.id"))
    serveurs = relationship("Serveurs", back_populates="cpl")
    relations = relationship("Relations", back_populates="cpl")

    def __repr__(self):
        return "<Cpl(name='%s', id_serveur='%s')>" % (self.name, self.id_serveurs)


class Relations(Base):
    __tablename__ = 'relations'

    id = Column(Integer, primary_key=True)
    uid_cpl = Column(String(50), ForeignKey("cpl.uid"))
    id_serveurs = Column(Integer, ForeignKey("serveurs.id"))
    serveurs = relationship("Serveurs", back_populates="relations")
    cpl = relationship("Cpl", back_populates="relations")

    def __repr__(self):
        return "<Relations(uid_cpl='%s', id_serveurs='%s')>" % (self.uid_cpl, self.id_serveurs)
