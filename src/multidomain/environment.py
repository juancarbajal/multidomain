"""Environment class to control all system."""

import os
# import boto3
# from botocore.config import Config
from multidomain.tucows import Tucows
from multidomain.aws import Aws
# from multidomain.queries import Db
from multidomain.statusrecorder import StatusRecorder
from multidomain.model.proxy import databaseProxy
from peewee import MySQLDatabase
from dotenv import load_dotenv

load_dotenv()


class Environment:
    """Environment definition."""

    def getAwsConnection(self):
        """Return the connection to Aws."""
        return Aws(self.getAwsConnectionDetail(), self.getAwsExtraInfo())

    def getAwsConnectionDetail(self):
        """Return the configuration of AWS client."""
        return {
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_KEY"),
            "region_name": "us-east-1",
        }

    def getAwsExtraInfo(self):
        """Return extra info for the process."""
        return {
            "cloudfront_id": os.getenv("MASTER_CLOUDFRONT_ID"),
            "cloudfront_domainname": os.getenv("MASTER_CLOUDFRONT_DOMAINNAME"),
            "cloudfront_targetoriginid": os.getenv(
                "MASTER_CLOUDFRONT_TARGETORIGINID"
            ),
        }

    def getTucowsConnection(self):
        """Return the connection of Tucows."""
        return Tucows(
            self.getTucowsConnectionDetail(),
            self.getMasterInfo(),
            self.getMasterClient(),
        )

    def getTucowsConnectionDetail(self):
        """Get the .env of tucows configuration in a Dict."""
        return {
            "api_key": os.getenv("TUCOWS_API_KEY"),
            "reseller_username": os.getenv("TUCOWS_RESELLER_USERNAME"),
            "api_host_port": os.getenv("TUCOWS_API_HOST_PORT"),
        }

    def getMasterInfo(self):
        """Get default configuration of tucows."""
        return {
            "first_name": os.getenv("MASTER_DEFAULT_NAME", "Master"),
            "last_name": os.getenv("MASTER_DEFAULT_NAME", "Master"),
            "phone": os.getenv("MASTER_DEFAULT_PHONE", "+1.4000000000"),
            "fax": os.getenv("MASTER_DEFAULT_PHONE", "+1.4000000000"),
            "email": os.getenv("MASTER_DEFAULT_EMAIL", "info@master.com"),
            "org_name": os.getenv("My company", "MyCompany"),
            "address1": os.getenv(
                "MASTER_DEFAULT_ADDRESS_1", "2055 Limestone Rd Ste 200-C"
            ),
            "address2": os.getenv("MASTER_DEFAULT_ADDRESS_2", "Wilmington"),
            "address3": "",
            "city": os.getenv("MASTER_DEFAULT_CITY", "Wilmington"),
            "state": os.getenv("MASTER_DEFAULT_STATE", "DE"),
            "country": os.getenv("MASTER_DEFAULT_COUNTRY", "US"),
            "postal_code": os.getenv("MASTER_DEFAULT_POSTAL_CODE", "19808"),
        }

    def getMasterClient(self):
        """Return the configuration of the default user and passwor for the restaurants."""
        return {
            "reg_username": os.getenv("MASTER_CLIENT_USER"),
            "reg_password": os.getenv("MASTER_CLIENT_PASS"),
            "period": os.getenv("MASTER_CLIENT_DEFAULT_PERIOD"),
        }

    def getDbConnection(self):
        """Return the database connection."""
        # config = {
        #     "port": os.getenv("DB_PORT", "3306"),
        #     "host": os.getenv("DB_HOST"),
        #     "database": os.getenv("DB_DATABASE"),
        #     "user": os.getenv("DB_USERNAME"),
        #     "password": os.getenv("DB_PASSWORD"),
        #     "raise_on_warnings": True,
        # }
        db = MySQLDatabase(
            os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
        )
        # databaseProxy = DatabaseProxy()
        databaseProxy.initialize(db)
        db.connect()
        return db
        # return Db(config)

    def getStatusRecorder(self):
        """Get Status recorder configuration."""
        config = {"host": os.getenv("PANEL_API_URL")}
        return StatusRecorder(config)

    def getAppVersion(self):
        """Return the API version value of config file."""
        return os.getenv("APP_VERSION", "NO.ENV")
