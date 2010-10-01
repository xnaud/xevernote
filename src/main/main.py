'''
Created on Sep 8, 2010

@author: xnaud
'''
import os
import logging.config

logging.config.fileConfig( "logging.conf" )
logger = logging.getLogger(__name__)


from sqlalchemy import engine_from_config
from sqlalchemy.orm import session
from model import model, modelDAO
from service import syncService, modelHelper
from ui.application import UIXevernote
from config import config






def create_home(config):
    home = config.get('evernote_home', None)
    if not os.path.exists(home):
        os.makedirs(home)

    
def init_db():
    create_home(config.configuration)
    engine = engine_from_config(config.configuration)
    model.Base.metadata.create_all(engine)
    return session.sessionmaker(bind=engine)
    
    
    
def main():
    logger.info("xevernote starting...")
    
    Session = init_db()
    #session = Session()
    

    #api = apiService.ApiService(config.configuration, "xnaud", "xevernote")
    #sync = syncService.SyncService(dao, api)
    
    #sync_thread = syncService.SyncThread(Session, 'xnaud', 'xevernote')

    #dao = modelDAO.ModelDAO(session)    
    #model_helper = modelHelper.ModelHelper(dao)
    app=UIXevernote(Session)

    app.main()
    
    
if __name__ == '__main__':
    main()
    
    