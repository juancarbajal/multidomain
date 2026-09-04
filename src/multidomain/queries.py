import os
# import sqlite3
import mysql.connector
from .constants import *

class Db:
    host = ''
    def __init__(self, aConfig):
        """
        Create Db
        Parameters:
        aHost: str
            Host of the database 
        """
        # self.host = aHost
        self.config = aConfig

    def createDomain(self, aCompanyId:str, aUrl:str, aOwner: str):
        """
        Create a multidomain record in the state table
        Parameters:
        aUrl: str
            Url of the record
        aStatus: int
            Status of the process 
        """
        try:
            con = mysql.connector.connect(**self.config)
            cur = con.cursor()
            sql = f'insert into domains(company_id, url, owner, status) values(%s, %s, %s, %s)'
            cur.execute(sql, (aCompanyId, aUrl, aOwner, MULTIDOMAIN_STATE_INITIATED))
            con.commit()
            con.close()
            return 0, 'Ok'
        except mysql.connector.Error as e:
            return 1, e.__str__() + " " + sql
    
    def updateDomain(self, aUrl, aStatus, aRoute53 = None, aAcm = None, aCloudFront = None):
        """
        Update the status in database
        """
        try:
            sql = f"update domains set updated_at=now(), status = '{aStatus}'"
            if aRoute53 != None:
                sql += f", aws_r53_id = '{aRoute53}' "
            if aAcm != None:
                sql += f", aws_acm_id = '{aAcm}' "
            if aCloudFront != None:
                sql += f", aws_clf_id = '{aCloudFront}' "
            if aStatus == 'finished':
                sql += f", release_date = now()"
            sql += f" where url = '{aUrl}'"
            con = mysql.connector.connect(**self.config)
            cur = con.cursor()
            cur.execute(sql)
            con.commit()
            con.close()
            return 0, 'Ok'
        except mysql.connector.Error as e:
            return 1, e.__str__()

    def getDomain(self, companyId):
        """
        Get info a a domain
        """
        try:
            sql = f"select * from domain where companyId = '{companyId}'";
            con = mysql.connector.connect(**self.config)
            cur = con.cursor()
            cur.execute(sql)
            con.close()
        except mysql.connector.Error as e:
            return 1, e.__str__()
        
    def fetchAllPending(self):
        """
        Fetch all record pending
        """
        con = mysql.connector.connect(**self.config)
        cur = con.cursor()
        cur.execute(f"select company_id, url, status, owner, aws_r53_id, aws_acm_id, aws_clf_id from domains where status not in ('{MULTIDOMAIN_STATE_FINISHED}', '{MULTIDOMAIN_STATE_CANCEL}')")
        r = cur.fetchall()
        con.close()
        return r

    def fetchAll(self):
        """
        Fetcha all records to send to client
        """
        con = mysql.connector.connect(**self.config)
        cur = con.cursor()
        cur.execute(f"select url, status from domains order by status")
        r = cur.fetchall()
        con.close()
        return r

    def status(self, aCompanyId:str):
        """
        Fetch status for a company ID
        """
        try:
            sql = f"select status from domains where company_id = '{aCompanyId} limit 1'"
            con = mysql.connector.connect(**self.config)
            cur = con.cursor()
            cur.execute(sql)
            con.commit()
            con.close()
            return 0, 'Ok'
        except mysql.connector.Error as e:
            return 1, e.__str__()


    
# db = Db(os.getenv('DATABASE_HOST',os.getcwd() + '\db\mdb.sdb'))
# print(db.host)
# #db.saveDomainStatus('test.jarvis', MULTIDOMAIN_STATE_CREATE_TUCOWS)
# print(db.fetchStatus())
