'''
Created on Sep 8, 2010

@author: xnaud
'''

from datetime import datetime

from sqlalchemy import Column, Integer, String, Table, Text, Sequence, DateTime, Boolean, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relation


# create a class dynamically
# will contain all metadata to create the DB tables
Base = declarative_base()

tag_note_table = Table("tag_note", Base.metadata, 
                       Column("note_fk", Integer, ForeignKey('note.pk'), primary_key=True), 
                       Column("tag_fk", Integer, ForeignKey('tag.pk'),primary_key=True) ) 


class User(Base):
    '''
    User
    '''
    __tablename__ = 'user'
    
    pk = Column(Integer, Sequence('user_seq'), primary_key=True)
    name = Column(String(50))
    privilege = Column(String(50))
    email = Column(String(20))
    shardId = Column(String(20))
    
    tags = relation("Tag", backref="user")
    notebooks = relation("Notebook", backref="user")
    
    
    def __init__(self, name):
        self.name = name


    def __repr__(self):
        return "<User('%', %s','%s')>" % (self.pk, self.name, self.email)
    
class Tag(Base):
    ''' 
    Tag
    '''
    
    __tablename__ = "tag"
    
    pk = Column(Integer, Sequence('tag_seq'), primary_key=True)
    guid = Column(String(40), unique=True)
    name = Column(String(50), unique=True, nullable=False)
    
    user_fk = Column(Integer, ForeignKey('user.pk'))
    notes = relation("Note", secondary=tag_note_table)
    version = Column(Integer)
    is_dirty = Column(Boolean, default=True)
    
    def __init__(self, name):
        self.name = name


    def __repr__(self):
        return "<Tag('%', %s')>" % (self.pk, self.name)
    
class Notebook(Base):
    '''
    Notebook
    '''
    __tablename__ = 'notebook'

    
    pk = Column(Integer, Sequence('notebook_seq'), primary_key=True)
    guid = Column(String(40), unique=True)
    name = Column(String(50), unique=True)
    version = Column(Integer)
    is_dirty = Column(Boolean, default=True)
    
    created = Column(Integer, nullable=True)
    updated = Column(Integer, nullable=True)
    
    notes = relation("Note", backref="notebook")
    user_fk = Column(Integer, ForeignKey('user.pk'))
    
    def __init__(self, name):
        self.name = name


    def __repr__(self):
        return "<Notebook('%s','%s', '%s')>" % (self.pk, self.guid, self.name)




class Note(Base):
    ''' 
    Note 
    '''
    
    __tablename__ = "note"
    
    pk = Column(Integer, Sequence('note_seq'), primary_key=True)
    guid = Column(String(40), unique=True)
    title = Column(String(40) )
    content = Column(Text(convert_unicode=True) )
    active = Column(Boolean, default=True)
    version = Column(Integer)
    created = Column(Integer, nullable=True)
    updated = Column(Integer, nullable=True)
    is_dirty = Column(Boolean, default=True)
    
    notebook_fk = Column(Integer, ForeignKey('notebook.pk'))
    
    tags = relation("Tag", secondary=tag_note_table)
    
    def __init__(self, title):
        self.title = title


    def __repr__(self):
        return "<Note('%s','%s', '%s')>" % (self.pk, self.guid, self.title)
 
    
class Resource(Base):
    '''
    Resource
    '''
    
    __tablename__ = "resource"
    
    pk = Column(Integer, Sequence('resource_seq'), primary_key=True)
    guid = Column(String(40), unique=True)
    mime = Column(String(40))
    data  = Column(String(40))
    version = Column(Integer)
    recognition = Column(String(512))


class LastSync(Base):
    '''
    keep the UpdateCount of the last sync
    '''
    
    __tablename__="last_sync"
    
    pk = Column(Integer, Sequence('note_seq'), primary_key=True)
    last_sync_time = Column(Integer, nullable=True)
    last_update_count = Column(Integer, default=0)
    
    
    def __init__(self, update_count=0):
        self.update_count = update_count


    def __repr__(self):
        return "<LastSync('%s')>" % (self.last_update_count)

 