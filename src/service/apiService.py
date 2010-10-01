'''
Created on Sep 10, 2010

@author: xnaud
'''
import os


import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore



class ApiService(object):
    '''
    ApiService
    '''

    _configuration = None
    
    _version_valid=False
    _username = None
    _user_password = None
    _user = None
    _token = None

    _note_store_uri = None

    _user_store = None
    _note_store = None
    
    
    def __init__(self, configuration, username, password, ):
        '''
        Constructor
        '''
        assert username
        assert password
        
        self._username = username
        self._password = password
        self._configuration = configuration
        
        
    def _init_user_store(self):
        if self._user_store:
            return
        
        user_store_http_client = THttpClient.THttpClient(self._configuration['evernote.user_store_uri'])
        user_store_protocol = TBinaryProtocol.TBinaryProtocol(user_store_http_client)
        self._user_store = UserStore.Client(user_store_protocol)

        if not self._user_store:
            raise RuntimeError("User store cannot be initialized.")
        
        self._version_valid = self._user_store.checkVersion( self._system_info(self._configuration),
                                           UserStoreConstants.EDAM_VERSION_MAJOR,
                                           UserStoreConstants.EDAM_VERSION_MINOR)
        if not self._version_valid:
            self._user_store=None
            raise RuntimeError("Evernote API v%d.%d not supported by evernote.com" % (UserStoreConstants.EDAM_VERSION_MAJOR,
                                                                                      UserStoreConstants.EDAM_VERSION_MINOR) )
    
    def _system_info(self, configuration):
        info = os.uname()
        return "%s/%s; %s/%s" % (configuration["application.name"], configuration["application.version"], info[0], info[2])
    
    
    def _authenticate(self):
        if not self._token:
            self._init_user_store()
            authResult = self._user_store.authenticate(self._username, self._password, self._configuration['evernote.consumer_key'], self._configuration['evernote.consumer_secret'])
            self._user = authResult.user                                    
            self._token = authResult.authenticationToken

    def _init_note_store(self):
        if self._note_store:
            return
        
        self._authenticate()
        self._note_store_uri = "%s/%s" % (self._configuration['evernote.note_store_base_uri'], self._user.shardId)
        noteStoreHttpClient = THttpClient.THttpClient(self._note_store_uri)
        noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
        self._note_store = NoteStore.Client(noteStoreProtocol)
        if not self._note_store:
            raise RuntimeError("Note store cannot be initialized")
        
        
    def get_notebooks(self):
        self._init_note_store()
        notebooks = self._note_store.listNotebooks(self._token)
        return notebooks
    
    def get_note_content(self, guid):
        return self._note_store.getNoteContent(self._token, guid)

        
    def get_sync_state(self):
        self._init_note_store()
        state = self._note_store.getSyncState(self._token)
        return state
    

    def get_sync_chunk(self, fromVersion=0, maxEntries=10, fullSync=False):
        self._init_note_store()
        chunks = self._note_store.getSyncChunk(self._token, fromVersion, maxEntries, fullSync  )
        return chunks
    
    
    def create_notebook(self, notebook):
        self._init_note_store()
        notebook = self._note_store.create_notebook(self._token, notebook)
        return notebook 
    
    def create_tag(self, tag):
        self._init_note_store()
        tag = self._note_store.create_notebook(self._token, tag)
        return tag
    
    
    def create_note(self, note):
        self._init_note_store()
        note = self._note_store.create_notebook(self._token, note)
        return note

    
