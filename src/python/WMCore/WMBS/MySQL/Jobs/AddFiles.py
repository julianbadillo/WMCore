#!/usr/bin/env python
"""
_AddFiles_
MySQL implementation of Jobs.AddFiles
"""
__all__ = []
__revision__ = "$Id: AddFiles.py,v 1.5 2008/10/01 21:54:39 metson Exp $"
__version__ = "$Revision: 1.5 $"

from WMCore.Database.DBFormatter import DBFormatter

class AddFiles(DBFormatter):
    sql = "insert into wmbs_job_assoc (job, file) values (:jobid, :fileid)"
               
    def execute(self, id=0, file=0, conn = None, transaction = False):
        binds = self.getBinds(jobid = id, fileid=file)
        
        result = self.dbi.processData(self.sql, binds)
        
        return self.format(result)