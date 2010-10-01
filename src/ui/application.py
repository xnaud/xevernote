'''
Created on Sep 21, 2010

@author: xnaud
'''

import sys
import logging

try:
    import pygtk
    #tell pyGTK, if possible, that we want GTKv2
    pygtk.require("2.16")
except:
    #Some distributions come with GTK2, but not pyGTK
    pass

import os

try:
    import gtk
except:
    print "You need to install pyGTK or GTKv2 ",
    print "or set your PYTHONPATH correctly."
    sys.exit(1)

import gobject

from model import modelDAO
from service import syncService, modelHelper

_logger = logging.getLogger(__name__)

# allows threads with gtk
gtk.gdk.threads_init()

gobject.threads_init()

class UIXevernote:

    _logger = None
    _model_helper = None
            
    _builder = None
    _main_window = None
    
    _tag_model = None 
    _notebook_model = None
    
    _icon_factory = None
    
    _sync_thread=None
    
    def __init__(self, session_class):        
        (dir, _) = os.path.split(__file__)
        glade_path = os.path.join( dir , 'xevernote.glade' ) 
        self._builder = gtk.Builder()
        self._builder.add_from_file( glade_path )

        self._main_window = self._builder.get_object('mainwindow')
        self._tag_model = self._builder.get_object('tagmodel')
        
        self._notebook_model = self._builder.get_object('notebookmodel')
        
        print self._builder.connect_signals(self)
        
        # TODO deals with user/pwd from preferences
        self._sync_thread = syncService.SyncThread(session_class, 'xnaud', 'xevernote', self._refresh_data)

        dao = modelDAO.ModelDAO(session_class())    
        self._model_helper = modelHelper.ModelHelper(dao)
        
        # load the initial data
        self.refresh_notebooks()
        self.refresh_tags()

        
    def refresh_notebooks(self):
        self._model_helper.populate_notebook_model( self._notebook_model)
        
    def refresh_tags(self):
        self._model_helper.populate_tag_model( self._tag_model)

    def _refresh_data(self):
        _logger.debug('refreshing data')
        self.refresh_notebooks()
        self.refresh_tags()
        return False
        
        
###############################
# callback triggered by the sync thread

    def sync_progress(self, progress):
        pass
    
    def sync_completed(self):
        gobject.idle_add(self._refresh_data)

#######################################


    def show(self):
        _logger.debug('UIXevernote.show called')        
#        dic = { 
#            'on_mainwindow_destroy' : self.quit,
#            'on_quitmenuitem_clicked' : self.quit,
#            'gtk_main_quit' : self.quit,
#            'on_syncbutton_clicked': self.request_sync,
#
#        }
        
        self._main_window.show_all()
    
    def quit(self, widget, data=None):
        _logger.debug('UIXevernote.quit called')
        self._sync_thread.request_quit()
        _logger.debug('Waiting for thread %s to exit' % self._sync_thread.name )
        self._sync_thread.join()
        _logger.debug('Thread %s exited. Quitting now!' % self._sync_thread.name )
        gtk.main_quit()


    def on_syncbutton_clicked(self, widget, data=None):
        _logger.debug('Requesting sync')
        self._sync_thread.request_sync()
        

#####################################
        
    def main(self):
        self.refresh_notebooks()
        self.refresh_tags()
        self.show()
        self._sync_thread.start()
        gtk.main()


