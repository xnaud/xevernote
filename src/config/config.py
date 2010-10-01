'''
Created on Sep 7, 2010

@author: xnaud
'''
from os import path

# @todo: replace with a configParser + config file

import sqlalchemy


__URI = "https://sandbox.evernote.com/edam"
__HOME = path.expanduser("~/.evernote")

configuration = {
                 'evernote.consumer_key': "xnaud",
                 'evernote.consumer_secret': "bb052e60507045bf",
                 'evernote.resource_uri': __URI,
                 'evernote.user_store_uri': "%s/user" % (__URI),
                 'evernote.note_store_base_uri': "%s/note" % (__URI),
                 'sqlalchemy.url': "sqlite:///%s/evernotedb" % (__HOME),
                 'sqlalchemy.echo' : 'false',
                 'sqlalchemy.convert_unicode' : 'true',
                 'sqlalchemy.poolclass' : sqlalchemy.pool.SingletonThreadPool,
                 'evernote_home': __HOME,                 
                 'content_path': "%s/content" % (__HOME),
                 'application.name' : 'xevernote',
                 'application.version' : '0.1',
                 
           }


