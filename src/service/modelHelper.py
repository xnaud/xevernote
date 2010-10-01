'''
Created on Sep 21, 2010

@author: xnaud
'''

import logging


from config import constant

class ModelHelper:

    
    _logger = None
    _dao = None
    
    def __init__(self, dao):
        self._logger = logging.getLogger(__name__)
        self._dao = dao

    '''
        Populate the model with the notebooks available
    '''
    def populate_notebook_model(self, model):
        notebooks = self._dao.get_all_notebooks()
        model.clear()
        for n in notebooks:
            model.append( [ constant.NOTEBOOK_ICON, n.name, len(n.notes) ] )
        return model
    
    '''
        Populate the model with the tags available
    '''
    def populate_tag_model(self, model):
        tags = self._dao.get_all_tags()
        model.clear()
        for t in tags:
            model.append( [constant.TAG_ICON, t.name, len(t.notes)])
        return model
    