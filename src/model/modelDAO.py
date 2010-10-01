'''
Created on Sep 8, 2010

@author: xnaud
'''
from datetime import datetime

import model

class ModelDAO(object):
    '''
    classdocs
    '''

    _session = None
    

    def __init__(self, session):
        '''
        Constructor
        '''
        self._session = session
        
    ########################################
    # Helper methods
    
    def _convert_value(self, key, value):
#        if key in ['created', 'updated']:
#            return datetime.utcfromtimestamp(value/1000)
#        else:
            return value
        
    def update_object(self, note, **kwargs):
        for k in kwargs:
            if hasattr(note, k):
                setattr(note, k, self._convert_value(k, kwargs[k]) )
        self._session.add(note)
    
    def delete_objects(self, a_class, a_prop, uuids):
        for i in uuids:
            self._session.query(a_class).filter(a_prop=i).delete()
        
        
    def get_dirty_objects(self, a_class):
        return self._session.query(a_class).filter_by(is_dirty=True).all()
    
    #############################################
    #### Tag methods
    
    def get_all_tags(self):
        return self._session.query(model.Tag).all()
    
    def get_tag_by_guid(self, guid):
        return self._session.query(model.Tag).filter(model.Tag.guid==guid).first()
        
    def get_tag_by_name(self, name):
        return self._session.query(model.Tag).filter(model.Tag.name==name).first()
    
    def create_tag(self, **kwargs):
        tag = model.Tag(kwargs['name'])
        self.update_object(tag, **kwargs)
        return tag
 
    def create_update_tag(self, tag, **kwargs):
        if tag:
            self.update_object(tag, **kwargs)
        else:
            tag = self.create_tag(**kwargs)
        return tag
    
    def create_update_tag_by_name_or_guid(self, guid=None, name=None, **kwargs):
        if not guid and not name:
            return None
        
        tag = self.get_tag_by_guid(guid)
        if not tag:
            tag = self.get_tag_by_name(name)
            if not tag:
                tag = self.create_tag(name=name, **kwargs)
        tag.name=name
        tag.guid=guid
        return tag
    
    #############################################
    #### Notebook methods
    
    def get_all_notebooks(self):
        return self._session.query(model.Notebook).all()
    
    def get_notebook_by_guid(self, guid):
        return self._session.query(model.Notebook).filter(model.Notebook.guid==guid).first()
        
    def create_notebook(self, **kwargs):
        notebook = model.Notebook(kwargs['name'])
        self.update_object(notebook, **kwargs)
        return notebook
 
    def create_update_notebook(self, notebook, **kwargs):
        if notebook:
            self.update_object(notebook, **kwargs)
        else:
            notebook = self.create_notebook(**kwargs)
        return notebook
    
    
    ##########################
    ### NOTES Methods
    
    def get_all_notes(self):
        return self._session.query(model.Note).all()
        
    def get_note_by_guid(self, guid):
        return self._session.query(model.Note).filter(model.Note.guid==guid).first()
        
    def create_note(self, **kwargs):
        note = model.Note(kwargs['title'])
        self.update_object(note, **kwargs)
        return note
        
    def create_update_note(self, note, **kwargs):
        if note:
            self.update_object(note, **kwargs)
        else:
            note = self.create_note(**kwargs)
        return note
    



    ################################
    ######## LastSync methods
    
    '''
    Return the LastSync object or none
    '''
    def get_or_create_last_sync(self):
        result = self._session.query(model.LastSync).first()
        if not result:
            result = model.LastSync()
            self._session.add(result)
        return result   
        
    
    def update_last_sync(self, update_count):
        sync = self.get_or_create_last_sync()
        sync.last_update_count=update_count
        sync.last_sync_time=datetime.now()

