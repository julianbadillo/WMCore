#!/usr/bin/python
"""
_WMInit

Init class that can be used by external projects
that only use part of the libraries
"""

__revision__ = "$Id: WMInit.py,v 1.3 2008/11/19 14:55:20 swakef Exp $"
__version__ = "$Revision: 1.3 $"
__author__ = "fvlingen@caltech.edu"

import logging
import threading

from WMCore.Database.DBFactory import DBFactory
from WMCore.Database.Transaction import Transaction
from WMCore.WMFactory import WMFactory

class WMInit:

    def __init__(self):
        # pass for the moment
        pass

    def setLogging(self,logFile = None, logName = None, logLevel = logging.INFO, logExists = True):
        """
        Sets logging parameters, depending on the settings,
        this method will create a logging file.
        """
        # use logName as name for file is no log file is given
        if not logExists:
            logging.basicConfig(level=logLevel,\
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',\
            datefmt='%m-%d %H:%M',\
            filename='%s.log' % logFile,\
            filemode='w')
            logging.debug("Log file ready")

        myThread = threading.currentThread()
        if logName != None:
            myThread.logger = logging.getLogger(logName)
        else:
            myThread.logger = logging.getLogger()


    def setDatabaseConnection(self, dbConfig, dialect = None, socketLoc = None, flavor = 'ProdAgent'):
        """
        Sets the default connection parameters, without having to worry
        much on what attributes need to be set. This is esepcially 
        advantagous for developers of third party projects that want
        to use only parts of the WMCore lib.

        The class differentiates between different formats used by external 
        projects. External project formats that are supported can activated 
        it by setting the flavor flag.
        """

        # check if connection string is  a string, if not it might be a dictionary.
        if not type(dbConfig) == str and flavor == 'ProdAgent':
            # modify db params to new WMCore conventions
            wmDbConf = {}
            wmDbConf['dialect'] =  dbConfig['dbType'].lower()
            dialect  =  dbConfig['dbType']
            wmDbConf['user'] = dbConfig['user']
            wmDbConf['password'] = dbConfig['passwd']
            wmDbConf['database'] = dbConfig['dbName']
            wmDbConf['host'] = dbConfig['host']
            
            if dbConfig['portNr']:
                wmDbConf['port'] = dbConfig['portNr']
            if dbConfig['socketFileLocation']:
                wmDbConf['unix_socket'] = dbConfig['socketFileLocation']

        # note: setLogging needs to have been set prior to calling this!
        myThread = threading.currentThread()
        if dialect == 'mysql':
            dialect = 'MySQL'
        elif dialect == 'oracle':
            dialect = 'Oracle'

        myThread.dialect = dialect

        options = {}
        if not type(dbConfig) == str:
            myThread.dbFactory = DBFactory(myThread.logger, dburl = None, options = wmDbConf)
        else:
            if myThread.dialect == 'MySQL':
                if socketLoc != None:
                    options['unix_socket'] = socketLoc
            myThread.dbFactory = DBFactory(myThread.logger, dbConfig, options)

        myThread.dbi = myThread.dbFactory.connect()
        myThread.transaction = Transaction(myThread.dbi)
        myThread.transaction.commit()



    def setSchema(self, modules = []):
        """
        Creates the schema in the database based on the modules
        input.

        This method needs to have been preceded by the 
        setDatabaseConnection.
        """
        myThread = threading.currentThread()

        # filter out unique modules

        myThread.transaction.begin()
        for factoryName in modules:
            # need to create these tables for testing.
            # notice the default structure: <dialect>/Create
            factory = WMFactory(factoryName, factoryName + "." + \
                myThread.dialect)
            create = factory.loadObject("Create")
            createworked = create.execute(conn = myThread.transaction.conn)
            if createworked:
                logging.debug("Tables for "+ factoryName + " created")
            else:
                logging.debug("Tables " + factoryName + \
                " could not be created, already exists?")
        myThread.transaction.commit()

    def clearDatabase(self, modules = []):
        """
        Enables clearing particular tables in the database
        Associated to modules. Note this only works if there 
        is the module has a Destroy class.
        """
        myThread = threading.currentThread()
        for module in modules:
            factory = WMFactory("clear", module)
            destroy = factory.loadObject(myThread.dialect+".Destroy")
            myThread.transaction.begin()
            destroyworked = destroy.execute(conn = myThread.transaction.conn)
            if not destroyworked:
                raise Exception(module  +" tables could not be destroyed")
            myThread.transaction.commit()
            del factory
 































