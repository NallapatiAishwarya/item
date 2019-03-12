import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class UniversityName(Base):
    __tablename__ = 'universityname'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="universityname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class CollegeName(Base):
    __tablename__ = 'collegename'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    establishedyear = Column(String(150))
    rating=Column(String(150))
    
    universitynameid = Column(Integer, ForeignKey('universityname.id'))
    universityname = relationship(
        UniversityName, backref=backref('collegename', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="collegename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'establishedyear': self. establishedyear,
            'rating': self. rating,
            'id': self. id
        }

engin = create_engine('sqlite:///universities.db')
Base.metadata.create_all(engin)
