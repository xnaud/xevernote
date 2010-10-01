'''
Created on Sep 10, 2010

@author: xnaud
'''

import threading


import logging

from model import modelDAO
from model.model import Note, Notebook, Tag


from service import apiService

from config import config



_BATCH_SIZE_=10

_logger=logging.getLogger(__name__)


# Thread status
STATUS_RUNNING=1
STATUS_IDLE=0

# Request Type
SYNCHRONIZE=1
TERMINATE=2


#class SyncEvent(threading.Event):
#    _type=None
#    
#    def __init__(self, type=SYNCHRONIZE, *args, **kwargs):
#        super(SyncRequestEvent, self).__init__(*args, **kwargs)
#        self._type=type
        
        
class SyncThread(threading.Thread):
    _sync_service=None
    _sync_request=None
    _sync_complete_callback=None
    _sync_progress_callback=None
    _quit=False
    
    
    status = STATUS_IDLE
    
    
    def __init__(self, session_cls, user, password, sync_complete_callback=None, sync_progress_callback=None ):
        super(SyncThread, self).__init__()
        self._logger = logging.getLogger(__name__)
        
        # wire the entire set of objects with sqlite object bound to this thread. Silly!!
        self._session = session_cls()
        dao = modelDAO.ModelDAO(self._session)
        api = apiService.ApiService(config.configuration, user, password)
        self._sync_service = SyncService(dao, api)
        # TODO: deal with the progress callback
        self._sync_progress_callback = sync_progress_callback
        self._sync_complete_callback = sync_complete_callback
        
        # event used to block till the event occurs. Avoid polling or a timer
        self._event = threading.Event()

    def run(self):
        actions = { SYNCHRONIZE: self._perform_sync, TERMINATE: self._perform_quit }
        
        while not self._quit:
            self._event.wait()
            _logger.debug('thread %s: event triggered:%s' % (self.name, self._sync_request) )
            action = actions.get(self._sync_request, None)
            if action:
                action()
            self._event.clear()
            #gobject.idle_add(self.update_label, counter)
#            _logger.debug('thread %s sleeping' % self.name )
#            time.sleep(10)
#            _logger.debug('thread %s waking up' % self.name)
        _logger.debug('thread %s exiting' % self.name )


##########################
# perform methods are executed by the sync thread

    def _perform_sync(self):
        #self._sync_service.sync()
        if self._sync_complete_callback:
            self._sync_complete_callback()
        
    def _perform_quit(self):
        self._quit=True


#############################
# request methods are executed by non sync thread to request the sync thread to perform some tasks

    def request_sync(self):     
        _logger.debug('Sync requested')
        self._sync_request=SYNCHRONIZE
        self._event.set()
    
    def request_quit(self):
        self._sync_request=TERMINATE
        self._event.set()






class SyncService(object):
    
    # init of the logger is in the init to make sure the logger config is loaded first
    _logger=None
    
    _dao = None
    _api_service = None

    _notebook_mapping = { 'name':'name',  'updated':'serviceUpdated', 'created': 'serviceCreated',  'guid':'guid',
                            # not supported yet
                            # 'updateSequenceNum':None, 'published':None,
                            # 'defaultNotebook':None,
                            # 'publishing':None, 
                        }
    
    _note_mapping = { 'active': 'active', 'content':'content', 'created':'created', 'updated':'updated', 
                    'guid': 'guid',  'title':'title', 
                     #'deleted':None,
                     #'contentHash':None, 'notebookGuid': 'notebook', 'resources': None, 'tagGuids':'tags', 
                     }
    
    _tag_mapping = { 'guid' : 'guid', 'name':'name' ,
                    }
    def __init__(self, dao, api):
        self._dao = dao
        self._api_service = api
        
    
    def _sync_notes(self, notes):
        _logger.debug("Synching notes")
        conflict=[]
        for note in notes:
            # get the note from the local cache
            cached_note = self._dao.get_note_by_guid(note.guid)
            # is cached_note is dirty (i.e. it has been changed locally
            # then we have a conflict
            if cached_note and cached_note.is_dirty:
                _logger.warning("Note %s conflict. Manual merge required" % cached_note)
                conflict.append(cached_note)
            else:
                # the content is separate
                content = self._api_service.get_note_content(note.guid)
                cached_note = self._dao.create_update_note(cached_note, **self._convert_to_properties(self._note_mapping, note) )
                cached_note.content = unicode(content)
                # deal with relationships to notebook and to tags
                cached_note.notebook = self._dao.get_notebook_by_guid(note.notebookGuid)
                
                if note.tagGuids:
                    for guid in note.tagGuids:
                        tag = self._dao.create_update_tag_by_name_or_guid(guid, guid, is_dirty=False)
                        cached_note.tags.append(tag)

                # reset the dirty flag
                cached_note.is_dirty=False
        _logger.debug("Synching notes done!")
        return conflict
    
    def _convert_to_properties(self, mapping, object):
        remote_props = object.__dict__
        result = {}
        for prop,remote_prop in mapping.iteritems():
            result[prop] = remote_props[remote_prop]
        return result
    
        
    def _sync_notebooks(self, notebooks):
        _logger.debug("Synching notebooks")
        conflict=[]
        for notebook in notebooks:
            # get the notebook from the local cache
            cached_notebook = self._dao.get_notebook_by_guid(notebook.guid)
            # if cached_note is dirty (i.e. it has been changed locally
            # then we have a conflict
            if cached_notebook and cached_notebook.is_dirty:
                _logger.warning("Notebook %s conflict. Manual merge required" % cached_notebook)
                conflict.append(cached_notebook)
            else:
                cached_notebook = self._dao.create_update_notebook(cached_notebook, 
                                                                   **self._convert_to_properties(self._notebook_mapping, notebook) )
                cached_notebook.is_dirty=False
        _logger.debug("Synching notebooks done!")
        return conflict
        
    def _sync_tags(self, tags):
        _logger.debug("Synching tags")
        conflict=[]
        for tag in tags:
            # get the notebook from the local cache
            cached_tag = self._dao.get_tag_by_guid(tag.guid)
            if not cached_tag:
                # try to look by name
                cached_tag = self._dao.get_tag_by_name(tag.name)
                
            # if cached_tag is dirty (i.e. it has been changed locally
            # then we have a conflict
            if cached_tag and cached_tag.is_dirty:
                _logger.warning("Tag %s conflict. Manual merge required" % cached_tag)
                conflict.append(cached_tag)
            else:
                cached_tag = self._dao.create_update_tag(cached_tag, 
                                                         **self._convert_to_properties(self._tag_mapping, tag) )
                cached_tag.is_dirty=False
        _logger.debug("Synching tags done!")
        return conflict
    
    
    def _sync(self, count_start, sync_state):
        delete_tag=[]
        create_tag=[]
        delete_note=[]
        create_note=[]
        delete_notebook=[]
        create_notebook=[]
        delete_resource=[]
        create_resource=[]
        count=count_start
        
        # no changes on the server?
        if count == sync_state.updateCount:
            return count
        
        # build a list of changes / deletion...
        while True:
            # get the first or notext chunk
            chunk = self._api_service.get_sync_chunk(count, _BATCH_SIZE_,True)

            # store the various info of the chunk
            create_tag.extend(chunk.tags or [])
            create_notebook.extend(chunk.notebooks or [])
            create_note.extend(chunk.notes or [])
            create_resource.extend(chunk.resources or [])

            delete_tag.extend(chunk.expungedTags or [])
            delete_notebook.extend(chunk.expungedNotebooks or [])
            delete_note.extend(chunk.expungedNotes or [])
            #delete_resource.extend(chunk.expungedResources or [])
            
            count = chunk.updateCount
            
            # exit condition: are we done getting all the chunks?
            if count >= chunk.chunkHighUSN:
                break

        # start the synching    
        self._sync_notebooks(create_notebook)
        self._sync_tags(create_tag)
        self._sync_notes(create_note)
        
        self._dao.delete_objects(Tag, Tag.guid, delete_tag)
        self._dao.delete_objects(Notebook, Notebook.guid, delete_notebook)
        self._dao.delete_objects(Note, Note.guid, delete_note)
        
        # TODO send the changes
        return count         


    '''
        _send_changes
        send all local changes to the remote server
    '''
    def _send_changes(self):
        notebooks = self._dao.get_dirty_objects(Notebook)
        tags = self._dao.get_dirty_objects(Tag)
        notes = self._dao.get_dirty_objects(Note)
        

    
    def sync(self, full=False):        
        sync_state = self._api_service.get_sync_state()
        last_sync = self._dao.get_or_create_last_sync()
        
        # check if full sync required
        if full or sync_state.fullSyncBefore  > last_sync.last_sync_time:
            #full sync, start from state 0
            count_start=0
            full=True
        else:
            count_start = last_sync.last_update_count

        count = self._sync(count_start, sync_state)        

        # same count, no change on server side
        #if last_sync.last_update_count==sync_state.updateCount:
        self._send_changes()
            
        # update the last count
        self._dao.update_last_sync(count)   

        


