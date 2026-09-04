import smtplib
from multidomain import environment
from multidomain import constants
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Report:
    db = None
    conf = None
    def main(self):
        """
        Principal method 
        """

        mail_content = '''
Estado de las peticiones de dominio propio:
'''
        mail_content += self.getBody()

        print(mail_content)
        return 0
        sender_address = self.conf['smtp_sender']
        sender_pass = self.conf['smtp_pass']
        receiver_address = self.conf['smtp_receiver']
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Dominio propio -  Reporte Diario'
        message.attach(MIMEText(mail_content, 'plain'))

        session = smtplib.SMTP(self.conf['smtp_server'], self.conf['smtp_port'])
        session.starttls()
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()

    def getBody(self):
        """
        get content for the report
        """
        records = self.db.fetchAll()
        s = ''
        for record in records:
            s += record[0].ljust(40, ' ') + ' : ' + self.getStatusString(record[1]) + '\n'
        return s 

    def getStatusString(self, status):
        """
        Return the status in string format 
        """
        if status == constants.MULTIDOMAIN_STATE_INIT:
            return 'SOLICITUD'
        if status == constants.MULTIDOMAIN_STATE_CREATE_ROUTE53:
            return 'AWS - Dominio creado'
        if status == constants.MULTIDOMAIN_STATE_CREATE_TUCOWS:
            return 'Tucows - Dominio creado'
        if status == constants.MULTIDOMAIN_STATE_CREATE_ACM:
            return 'AWS - Certificado creado'
        if status == constants.MULTIDOMAIN_STATE_VALIDATE_ACM:
            return 'AWS - Certificado aceptado'
        if status == constants.MULTIDOMAIN_STATE_CREATE_CLOUDFRONT:
            return 'AWS - Cloudfront configurado'
        if status == constants.MULTIDOMAIN_STATE_FINISH:
            return 'TERMINADO'


    def __init__(self, aConfiguration: dict, aDb):
        """
        Constructor of the class
        """
        self.db = aDb
        self.conf = aConfiguration


env = environment.Environment()
smtpConfiguration = {'smtp_server': 'smtp.gmail.com',
                     'smtp_port' : 587,
                     'smtp_sender': 'juancarbajal@gmail.com',
                     'smtp_pass': 'A23aJ17nG18jA26aM12o@@',
                     'smtp_receiver': 'juancarbajal@gmail.com'}
r = Report(smtpConfiguration, env.getDbConnection())
r.main()
