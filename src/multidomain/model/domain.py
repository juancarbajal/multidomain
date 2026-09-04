"""Model Domain."""

from peewee import Model, CharField, TextField, DateTimeField
import datetime

# import json
from .constants import Constants
from .proxy import databaseProxy

# databaseProxy = DatabaseProxy()


class DomainTable(Model):
    """Domain Table definition."""

    company_id = CharField(primary_key=True)
    url = CharField(unique=True)
    owner = TextField()
    aws_r53_id = CharField()
    aws_acm_id = CharField()
    aws_clf_id = CharField()
    status = CharField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    release_date = DateTimeField()
    renewal_type = CharField()
    error = TextField()

    class Meta:
        """fisical connection to database."""

        database = databaseProxy
        table_name = "domains"
        


class DomainModel:
    """Model of Domain table."""

    def createDomain(self, aCompanyId: str, aUrl: str, aOwner: str):
        """
        Create a multidomain record in the state table.

        Parameters:
            aUrl(str): Url of the record
            aStatus(int): Status of the process
        """
        try:
            DomainTable.create(
                company_id=aCompanyId,
                url=aUrl,
                owner=aOwner,
                created_at=datetime.datetime.now(),
            )
            return 0, "Ok"
        except Exception as e:
            return 1, e.__str__()

    def updateDomain(self, aUrl, aStatus, aRoute53=None, aAcm=None, aCloudFront=None):
        """
        Update domain status.

        Parameters:
            aUrl(str): Url to update the status and values
            aStatus(str): New status to update
            aRoute53(str): ARN of Route53
            aAcm(str): Identification of SSL certificate
            aCloudFront(str): Id of CLoudfront.
        """
        now = datetime.datetime.now()
        updSet = {DomainTable.updated_at: now, DomainTable.status: aStatus}
        if aRoute53 is not None:
            updSet[DomainTable.aws_r53_id] = aRoute53
        if aAcm is not None:
            updSet[DomainTable.aws_acm_id] = aAcm
        if aCloudFront is not None:
            updSet[DomainTable.aws_clf_id] = aCloudFront
        if aStatus == "finished":
            updSet[DomainTable.release_date] = now
        q = DomainTable.update(updSet).where(DomainTable.url == aUrl)
        q.execute()
        return 0, "Ok"

    def fetchAll(self):
        """
        Fetch all (url,status) records order by status.

        Returns:
            List of records
        """
        return DomainTable.select(DomainTable.url, DomainTable.status).order_by(
            DomainTable.status
        )

    def fetchAllPending(self):
        """
        Fetch url, status.

        Returns:
            List of domains with status distint to FINISHED or CANCELLED
        """
        q = DomainTable.select(
            DomainTable.company_id,
            DomainTable.url,
            DomainTable.status,
            DomainTable.owner,
            DomainTable.aws_r53_id,
            DomainTable.aws_acm_id,
            DomainTable.aws_clf_id,
        ).where(
            DomainTable.status.not_in(
                [
                    Constants.MULTIDOMAIN_STATE_FINISHED,
                    Constants.MULTIDOMAIN_STATE_CANCEL,
                ]
            )
        )
        return q

    def getDomainByCompany(self, companyId: str):
        """
        Get Domain information of a company.

        Parameters:
            companyId(str): Id of company to search
        Returns:
            Info of a domain
        """
        try:
            data = DomainTable.get(DomainTable.company_id == companyId)
            return data
        except Exception:
            return None

    def updDomainOwner(self, aCompanyId: str, aOwner: str):
        """
        Update owner's information of the domain info.

        Returns:
            aCompanyId(str): Id of the company to search
            aOwner(str): Json information of the owner
        """
        try:
            q = DomainTable.update({DomainTable.owner: aOwner}).where(
                DomainTable.company_id == aCompanyId
            )
            q.execute()
            return 0, "Ok"
        except Exception as e:
            return 1, e.__str__()

    def updDomainError(self, companyId: str, error: str):
        """
        Insertar Error del dominio.

        Parameters:
            idCompany(str): Company's id
            error(str): Error message
        """
        try:
            q = DomainTable.update({DomainTable.error: error}).where(
                DomainTable.company_id == companyId
            )
            q.execute()
        except Exception as e:
            return 1, e.__str__()


# db = MySQLDatabase('db_multidomain', user='root', password='R00tP@SSw0rD', host='localhost', port=3306)
# databaseProxy.initialize(db)
# db.connect()

# domain = DomainModel()

# def printAllValues(r):
#     print(r.url, r.status.ljust(20), r.aws_r53_id, r.aws_acm_id, r.aws_clf_id, r.created_at, r.updated_at, r.release_date)

# print(domain.createDomain('google', 'google.com', 'data'))
# r = domain.getDomainByCompany('google')
# printAllValues(r)

# domain.updateDomain('google.com', 'route53_created', aRoute53='test Route53')
# r = domain.getDomainByCompany('google')
# printAllValues(r)

# domain.updateDomain('google.com', 'tucows_created')
# r = domain.getDomainByCompany('google')
# printAllValues(r)

# domain.updateDomain('google.com', 'acm_created', aAcm= 'test acm')
# r = domain.getDomainByCompany('google')
# printAllValues(r)

# domain.updateDomain('google.com', 'route53_updated')
# r = domain.getDomainByCompany('google')
# printAllValues(r)

# domain.updateDomain('google.com', 'acm_validated')
# r = domain.getDomainByCompany('google')
# printAllValues(r)

# domain.updateDomain('google.com', 'cloudfront_created', aCloudFront= 'test CF')
# r = domain.getDomainByCompany('google')
# printAllValues(r)

# domain.updateDomain('google.com', 'finished')
# r = domain.getDomainByCompany('google')
# printAllValues(r)


# domain.updateDomain('google.com', 'cancel')
# r = domain.getDomainByCompany('google')
# printAllValues(r)

# print("List of pendings")
# for d in domain.fetchAllPending():
#     printAllValues(d)
