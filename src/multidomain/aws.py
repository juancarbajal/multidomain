import os
import subprocess
import boto3
import botocore.exceptions
import datetime
import json
import sys
# from .environment import Environment
# from .config import Config as Cnf
# from .queries import Db
# from dotenv import load_dotenv
# load_dotenv()

# session = Environment.getAwsConnection()
# croute53 = session.client('route53')
# cacm = session.client('acm')
# ccloud = session.client('cloudfront')

class Aws:
    """
    Class to maange AWS
    """
    def __init__(self, aConfig, aExtraInfo = None):
        session = boto3.Session(aws_access_key_id= aConfig['aws_access_key_id'],
            aws_secret_access_key= aConfig['aws_secret_access_key'],
            region_name= aConfig['region_name'])
        self.croute53 = session.client('route53')
        self.cacm = session.client('acm')
        self.ccloud = session.client('cloudfront')
        self.extra = aExtraInfo

    def route53Zone(self, domain):
        """
        route53 function to create hosted zone

        @param domain: domain to add in hosted zone
        @return: id of hosted zone
        """
        try:
            ct = datetime.datetime.now()
            ts = ct.timestamp()
            response = self.croute53.create_hosted_zone(
                Name=domain,
                CallerReference=domain + str(ts),
                HostedZoneConfig={'Comment': 'add via cli'}
                )
            return response["HostedZone"]["Id"], 0
        except botocore.exceptions.ClientError as error:
            return str(error), 1
            
    def route53CMRecord(self, id, name, type, value):
        """
        route53 function to create a certificate record in a hosted zone

        @param id: id of hosted zone
        @param name: name of record
        @param type: type of record
        @param value: value of record
        @return: json describing the record
        """
        try:
            name = name
            response = self.croute53.change_resource_record_sets(
                HostedZoneId= id,
                ChangeBatch={
                    'Comment': 'add via cli',
                    'Changes': [
                        {
                         'Action': 'CREATE',
                         'ResourceRecordSet': {
                             'Name': name,
                             'Type': type,
                             'TTL': 300,
                             'ResourceRecords': [
                                 {
                                  'Value': value
                                                 },
                                               ],
                         }
                                }
                             ]
                                                            }
                )
            return response, 0
        except botocore.exceptions.ClientError as error:
            return str(error), 1

    def getDNS(self, id):
        """
        route53 function to get DNS in a hosted zone

        @param id: id of hosted zone
        @reutrn: a list of the 4 DNS
        """
        try:
            response = self.croute53.get_hosted_zone(
                Id= id
                )
            return response["DelegationSet"]["NameServers"], 0
        except botocore.exceptions.ClientError as error:
            return str(error), 1


    def reqCM(self, domain, route53Id):
        """
        certificate manager function to request a certificate

        @param domain: domain to request certificate
        @reutrn: id of certificate
        """
        try:
            response = self.cacm.request_certificate(
                DomainName=domain,
                ValidationMethod='DNS',
                SubjectAlternativeNames=[
                    "*." + domain,
                                                ]
                )
            CMid = response["CertificateArn"]
            
            return CMid, 0 
        except botocore.exceptions.ClientError as error:
            return str(error), 1

    def addRecordSSLRoute53(self, route53Id, CMid):
        """
        Add record for SSL DNS validation

        @param CMid: id of the certificate
        @return record added 
        """
        response = self.cacm.describe_certificate(CertificateArn= CMid)
        name = response["Certificate"]["DomainValidationOptions"][0]["ResourceRecord"]["Name"]
        value = response["Certificate"]["DomainValidationOptions"][0]["ResourceRecord"]["Value"]
        msg, err = self.route53CMRecord(route53Id, name, "CNAME", value)
        if err == 0:
            return 'Ok', 0
        else:
            return msg, 1
        
    def descCMValidation(self, CMid):
        """
        certificate manager function describe status of the validation 

        @param CMid: id of certificate
        @return: a string that shows if certificate is pending or valid
        """
        try:
            response = self.cacm.describe_certificate(
                CertificateArn= CMid
                )
            status = response['Certificate']['DomainValidationOptions'][0]['ValidationStatus']
            if status != 'PENDING_VALIDATION':
                return status, 0
            else:
                return status, 1
        except botocore.exceptions.ClientError as error:
            return str(error), 1

    def listCNAMERecords(self, route53Id, name):
        """
        route53 function to search certificate record

        @param route53Id: id of hosted zone
        @param name: name of certificate to validate
        @reutrn: name of certificate to validate
        """
        try:
            response = self.croute53.list_resource_record_sets(
                HostedZoneId=route53Id,
                StartRecordName=name,
                StartRecordType= "CNAME"
                )
            # print(response)
            if len(response['ResourceRecordSets'])>0:
                return response["ResourceRecordSets"][0]["Name"], 0
            else:
                return "No records found", 1
        except botocore.exceptions.ClientError as error:
            return str(error), 1


    def cloudFront(self, domain, CMId):
        """
        cloud front function to create distribution

        @param domain: domain name
        @param CMid: id of certificate
        @return: id of distribution
        """
        try:
            # print(self.extra)
            response = self.ccloud.create_distribution(
                DistributionConfig={
                    'CallerReference': domain,
                    'Aliases': {
                        'Quantity': 3,
                        "Items": [domain, "*."+domain, "www."+domain]
                                    },
                    'Origins': {
                        'Quantity': 1,
                        "Items": [
                            {
                             "Id": self.extra['cloudfront_id'], 
                             "DomainName": self.extra['cloudfront_domainname'],                             
                             "OriginPath": "",
                             "CustomHeaders": {
                                 "Quantity": 0
                             },
                             "CustomOriginConfig": {
                                 "HTTPPort": 80,
                                 "HTTPSPort": 443,
                                 "OriginProtocolPolicy": "http-only",
                                 "OriginSslProtocols": {
                                     "Quantity": 1,
                                     "Items": [
                                         "TLSv1.2"
                                                        ]
                                                    },
                                 "OriginReadTimeout": 30,
                                 "OriginKeepaliveTimeout": 5
                            },
                             # "S3OriginConfig": {
                             #     "OriginAccessIdentity": ""
                             # },
                             "ConnectionAttempts": 3,
                             "ConnectionTimeout": 10,
                             "OriginShield": {
                                 "Enabled": False
                             }
                                  }
                                ]
                                    },
                    "OriginGroups": {
                        "Quantity": 0
                                    },
                    "DefaultCacheBehavior": {                        
                        "TargetOriginId": self.extra['cloudfront_targetoriginid'],                        
                        # "ForwardedValues": {
                        #     "QueryString": False,
                        #     "Cookies": {
                        #         "Forward": "none"
                        #                     },
                        #     "Headers": {
                        #         "Quantity": 0
                        #                     },
                        #     "QueryStringCacheKeys": {
                        #         "Quantity": 0
                        #                     }
                        #                      },
                        "TrustedSigners": {
                            "Enabled": False,
                            "Quantity": 0
                                             },
                        "TrustedKeyGroups": {
                            "Enabled": False,
                            "Quantity": 0
                                             },
                        "ViewerProtocolPolicy": "redirect-to-https",
                        # "MinTTL": 0,
                        "AllowedMethods": {
                            "Quantity": 7,
                            "Items": ["HEAD", "DELETE", "POST", "GET", "OPTIONS", "PUT", "PATCH"],
                            "CachedMethods": {
                                "Quantity": 2,
                                "Items": ["HEAD", "GET"]
                                           }
                                             },
                        "SmoothStreaming": False,
                        "Compress": True,
                        "LambdaFunctionAssociations": {
                            "Quantity": 0
                                             },
                        "FieldLevelEncryptionId": "",
                        "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
                        "OriginRequestPolicyId": "216adef6-5c7f-47e4-b989-5492eafa07d3"
                                    },
                    "CacheBehaviors": {
                        "Quantity": 0
                                    },
                    "CustomErrorResponses": {
                        "Quantity": 0
                                    },
                    "Comment": "add via cli",
                    "Logging": {
                        "Enabled": False,
                        "IncludeCookies": False,
                        "Bucket": "",
                        "Prefix": ""
                                    },
                    "PriceClass": "PriceClass_All",
                    "Enabled": True,
                    "ViewerCertificate": {
                        "ACMCertificateArn": CMId,
                        "SSLSupportMethod": "sni-only",
                        "MinimumProtocolVersion": "TLSv1.2_2021",
                        "Certificate": CMId,
                        "CertificateSource": "acm"
                                    },
                    "Restrictions": {
                        "GeoRestriction": {
                            "RestrictionType": "none",
                            "Quantity": 0
                                     }
                                    },
                    "WebACLId": "",
                    "HttpVersion": "http2",
                    "IsIPV6Enabled": True
                                                  }
                )
            return response["Distribution"]["Id"], 0
        except botocore.exceptions.ClientError as error:
            return str(error), 1
        
    def route53ARecord(self, domain, DNSName, id):
        """
        route53 function to create A record

        @param domain: domain name
        @param DNSName: cloud front domain name
        @param id: id of hosted zone
        @return: id of distribution
        """
        try:
            # print('domain ', domain)
            # print('dnsname ',DNSName)
            # print('id ', id)
            records, error = self.listARecords(id, domain)

            dist = self.ccloud.get_distribution(Id = DNSName)
            cfDomainName = dist['Distribution']['DomainName']
            # print(cfDomainName)
            # res, err = self.route53CMRecord(id, domain, "CNAME", cfDomainName)
            # if err == 0:
            #     return "A record already created", 0
            # else:
            #     return str(res), 1
            
            hostedZone = id[12:]
            if (records != "A"):
                response = self.croute53.change_resource_record_sets(
                    HostedZoneId= id,
                    ChangeBatch={
                        'Comment': 'add via cli',
                        'Changes': [
                            {
                             "Action": "CREATE",
                             "ResourceRecordSet":
                             {
                              "Name": domain,
                              "Type": "A",
                              "AliasTarget":
                              {
                               "HostedZoneId": "Z2FDTNDATAQYW2",
                               # "DNSName": DNSName,
                               "DNSName": cfDomainName,
                               "EvaluateTargetHealth": False
                              }
                             }
                                    }
                                 ]
                                                                     }
                    )
                return response, 0
            else:
                return "A record already created", 0
        except botocore.exceptions.ClientError as error:
            return str(error), 1

    def listARecords(self, route53Id, name):
        """
        route53 function to search certificate record

        @param route53Id: id of hosted zone
        @param name: name of A record
        @reutrn: type of first record
        """
        try:
            response = self.croute53.list_resource_record_sets(
                HostedZoneId=route53Id,
                StartRecordName=name,
                StartRecordType= "A"
                )
            return response["ResourceRecordSets"][0]["Type"], 0
        except botocore.exceptions.ClientError as error:
            return str(error), 1

        
