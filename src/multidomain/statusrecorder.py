"""Module Satatus recorder."""

import requests


class StatusRecorder:
    """Status Recorder class."""

    def __init__(self, aConf):
        """
        Instance of class.

        Parameters:
        aConf : dict
            Configuration of the host to send de information
        """
        self.config = aConf

    def register(self, companyId: str, url: str, status: str):
        """
        Register the status of the action.

        Parameters:
        url: str
            Url in process and status
        status: str
            Status of the process
        """
        try:
            host = (
                self.config["host"]
                + "/internal/v1/companies/"
                + str(companyId)
                + "/domain"
            )
            newUrl = url.replace("https://", "").replace("http://", "")
            res = requests.patch(
                host, json={"url": newUrl, "registration_status": status}
            )
            return res.status_code
        except Exception as e:
            print(e.__str__())
