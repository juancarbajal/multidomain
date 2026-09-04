"""Cron to create the domain."""

# import os
# from dotenv import load_dotenv
from multidomain.model.constants import Constants
from multidomain.constants import Constants as recConstants
from multidomain import environment
from multidomain.model.domain import DomainModel
import json


class Cron:
    """Manage the process of multidomain."""

    def log(self, text):
        """
        Register in the log.

        Parameters:
            text(str): Text to save in the log
        """
        print("[cron] Processing domains: " + text)

    def __init__(self):
        """Initializate the cron."""
        self.env = environment.Environment()
        self.env.getDbConnection()
        self.db = DomainModel()
        self.tucows = self.env.getTucowsConnection()
        self.aws = self.env.getAwsConnection()
        self.recorder = self.env.getStatusRecorder()

    def createRoute53(self, companyId, url):
        """Create Route53 domains."""
        self.log("AWS: create domain in route53")
        self.log("creando dominio en route 53")
        msg, err = self.aws.route53Zone(url)
        # msg, err = ["error 1", 1]
        if err == 0:
            self.db.updateDomain(
                aUrl=url,
                aStatus=Constants.MULTIDOMAIN_STATE_CREATED_ROUTE53,
                aRoute53=msg,
            )
            self.log("Ok")
        else:
            self.db.updDomainError(companyId, msg)
            self.log(msg)
            self.recorder.register(
                companyId, url, recConstants.REGISTRATION_STATUS_FAILED
            )

    def createDomainTucows(self, companyId, url, owner, route53Id):
        """Create tucows domain."""
        self.log("TUCOWS: create domain")
        route53Info, err = self.aws.getDNS(route53Id)
        # route53Info, err = ['error 2', 1]
        if err == 0:
            self.log("validando si el dominio esta libre")
            resFree, errMsg = self.tucows.isFreeDomain(url)
            if resFree == 0:
                self.log("registrando el dominio en Tucows")
                objOwner = json.loads(
                    owner.encode()
                    .decode("unicode-escape")
                    .encode("ascii", "xmlcharrefreplace")
                )
                resReg, errMsg = self.tucows.registerDomain(url, objOwner, route53Info)
                if resReg == 0:
                    self.db.updateDomain(
                        aUrl=url, aStatus=Constants.MULTIDOMAIN_STATE_CREATED_TUCOWS,
                    )
                    self.log("Ok")
                else:
                    self.db.updDomainError(companyId, errMsg)
                    self.log(errMsg + resReg.__str__())
                    self.recorder.register(
                        companyId, url, recConstants.REGISTRATION_STATUS_FAILED
                    )
            else:
                self.db.updDomainError(companyId, errMsg)
                self.log(errMsg)
        else:
            self.db.updDomainError(companyId, route53Info)
            self.log(route53Info)

    def createCertificateACM(self, companyId, url, route53Id):
        """Create certificate in acm."""
        self.log("AWS: create ssl certificate")
        self.log("solicitando certificado")
        acmInfo, err = self.aws.reqCM(url, route53Id)
        # acmInfo, err = ['error 3', 1]
        if err == 0:
            self.db.updateDomain(
                aUrl=url, aStatus=Constants.MULTIDOMAIN_STATE_CREATED_ACM, aAcm=acmInfo,
            )
            self.log("Ok")
        else:
            self.db.updDomainError(companyId, acmInfo)
            self.log(acmInfo)
            self.recorder.register(
                companyId, url, recConstants.REGISTRATION_STATUS_FAILED
            )

    def updateRoute53DNSwithACM(self, companyId, url, route53Id, acmId):
        """Update the DNS of route53 with record to validate the ACM."""
        self.log("AWS: update DNs validate for SSL in route53")
        self.log("registramos el DNS en Route53")
        res, err = self.aws.addRecordSSLRoute53(route53Id, acmId)
        # res, err = ["error 4", 1]
        if err == 0:
            self.db.updateDomain(
                aUrl=url, aStatus=Constants.MULTIDOMAIN_STATE_UPDATED_ROUTE53
            )
            self.log("Ok")
        else:
            self.db.updDomainError(companyId, res)
            self.log(res)
            self.recorder.register(
                companyId, url, recConstants.REGISTRATION_STATUS_FAILED
            )

    def validateACMSSLstatus(self, companyId, url, acmId):
        """Validte if the certificate is correct."""
        self.log("AWS: validate status of SSL certificate")
        res, err = self.aws.descCMValidation(acmId)
        # res, err = ["error 5", 1]
        if err == 0:
            self.db.updateDomain(
                aUrl=url, aStatus=Constants.MULTIDOMAIN_STATE_VALIDATED_ACM
            )
            self.log("Ok")
        else:
            self.db.updDomainError(companyId, res)
            self.log(res)
            self.recorder.register(
                companyId, url, recConstants.REGISTRATION_STATUS_FAILED
            )

    def createCloudFront(self, companyId, url, acmId):
        """Create the cloudfront."""
        self.log("AWS: create cloudfront")
        self.log("creando cloudfront")
        res, err = self.aws.cloudFront(url, acmId)
        # res, err = ["Test 6", 1]
        if err == 0:
            self.db.updateDomain(
                aUrl=url,
                aCloudFront=res,
                aStatus=Constants.MULTIDOMAIN_STATE_CREATED_CLOUDFRONT,
            )
            self.log("Ok")
        else:
            self.db.updDomainError(companyId, res)
            self.log(res)
            self.recorder.register(
                companyId, url, recConstants.REGISTRATION_STATUS_FAILED
            )

    def updateRoute53DNSCloudfront(self, companyId, url, route53Id, clfId):
        """Update the route53 with the new connection."""
        self.log("ALL: final validation")
        self.log("actualizando route53 para apuntar a cloudfront")
        res, err = self.aws.route53ARecord(url, clfId, route53Id)
        # res, err = ['Test 7', 1]
        if err == 0:
            self.log("actualizando route53 añadiendo redirección www")
            resW, errW = self.aws.route53CMRecord(
                route53Id, "www." + url, "CNAME", url
            )  # Add www redirecto to
            self.db.updateDomain(aUrl=url, aStatus=Constants.MULTIDOMAIN_STATE_FINISHED)
            self.log("Ok")
            self.recorder.register(
                companyId, url, recConstants.REGISTRATION_STATUS_ACTIVE
            )
        else:
            self.db.updDomainError(companyId, res)
            self.log(res)
            self.recorder.register(
                companyId, url, recConstants.REGISTRATION_STATUS_FAILED
            )

    def main(self):
        """Principal cron funtcion."""
        records = self.db.fetchAllPending()
        self.log("Versión v" + self.env.getAppVersion() + "\n")
        for r in records:
            self.log(r.url)
            if r.status == Constants.MULTIDOMAIN_STATE_INITIATED:  # 1
                self.createRoute53(r.company_id, r.url)
            elif r.status == Constants.MULTIDOMAIN_STATE_CREATED_ROUTE53:  # 10
                self.createDomainTucows(
                    r.company_id, r.url, r.owner, r.aws_r53_id
                )
            elif r.status == Constants.MULTIDOMAIN_STATE_CREATED_TUCOWS:  # 20
                self.createCertificateACM(r.company_id, r.url, r.aws_r53_id)
            elif r.status == Constants.MULTIDOMAIN_STATE_CREATED_ACM:  # 30
                self.updateRoute53DNSwithACM(
                    r.company_id, r.url, r.aws_r53_id, r.aws_acm_id
                )
            elif r.status == Constants.MULTIDOMAIN_STATE_UPDATED_ROUTE53:  # 35
                self.validateACMSSLstatus(r.company_id, r.url, r.aws_acm_id)
            elif r.status == Constants.MULTIDOMAIN_STATE_VALIDATED_ACM:  # 40
                self.createCloudFront(r.company_id, r.url, r.aws_acm_id)
            elif r.status == Constants.MULTIDOMAIN_STATE_CREATED_CLOUDFRONT:  # 50
                self.updateRoute53DNSCloudfront(
                    r.company_id, r.url, r.aws_r53_id, r.aws_clf_id
                )


cron = Cron()
cron.main()
