import requests
import hashlib
# import os
# from dotenv import load_dotenv
import xml.etree.ElementTree as ET
# from .constants import *
# import constants

#Errors codes  https://domains.opensrs.guide/docs/codes


class TucowsXMLRequest:
    """
    Class to create a XML valid in Tucows 
    """
    def __init__(self, aMethod, aAttributes):
        '''
        Set methods and attributesto XML Request

        Parameters:
        aMethod: Dict
            Dictionary of with format { 'action' : '<ACTION TUCOWS>', 'object' : '<OBJECT TUCOWS>'}
        aAttributes: Dict
            Attributes of the request { '<KEY>' : '<VALUE>', ..., '<KEY>' : '<VALUE>'}
        '''
        self.method = aMethod
        self.attributes = aAttributes
        
    def __str__(self):
        xml = '''
<?xml version='1.0' encoding="UTF-8" standalone="no" ?>
<!DOCTYPE OPS_envelope SYSTEM "ops.dtd">
<OPS_envelope>
    <header>
        <version>0.9</version>
    </header>
    <body>
        <data_block>
            <dt_assoc>
                <item key="protocol">XCP</item>
'''
        for key in self.method:
            xml= xml + '<item key="' + key +'">' + self.method[key] + '</item>\n'

        xml= xml + '<item key="attributes">\n<dt_assoc>\n'
        xml += self.attributesToXml(self.attributes)
        xml= xml + '''</dt_assoc></item>
            </dt_assoc>
        </data_block>
    </body>
</OPS_envelope>
'''
        return xml

    def attributesToXml(self, attr):
        '''
        Buid XML of a list of attributes

        Parameters:
        attr: (str|dict)
            List of parameters or One parameters

        Returns:
        str:
           Xml of attributes
        '''
        xmlAttr = ''
        for key in attr:
            if isinstance(attr[key], dict):
                xmlAttr += '<item key="'+ str(key) +'">\n<dt_assoc>\n' + self.attributesToXml(attr[key]) + '</dt_assoc>\n</item>\n'
            elif isinstance(attr[key], str):
                xmlAttr += '<item key="'+ str(key) +'">' + attr[key] + '</item>\n'
            elif isinstance(attr[key], list):
                xmlAttr += f'<item key="{key}">\n<dt_array>'
                for val in attr[key]:
                    xmlAttr += self.attributesToXml(val)
                xmlAttr += '\n</dt_array>\n</item>\n'
        return xmlAttr
    
class TucowsXMLResponse:
    """
    Class to capture the Reponse of Tucows 
    """
    response = None
    tree = None
    def __init__(self, aResponse):
        self.response = aResponse
        self.tree =  ET.fromstring(self.response.text)
        # self.tree = t.getroot()

    def getIsSuccess(self):
        """
        Get status of the response 1: Success  0: Error of Xml 
        """
        return self.tree.findall(".//*[@key='is_success']")[0].text
    
    def getResponseText(self):
        """
        Get response text of Xml 
        """
        return self.tree.findall(".//*[@key='response_text']")[0].text

    def getErrorText(self):
        """
        Get response error of Xml 
        """
        try:
            return self.tree.findall(".//*[@key='error']")[0].text
        except Exception as e:
            return '-'
        # data = self.tree.findall(".//*[@key='error']")
        # if data == None:
        #     return '-'
        # else:
        #     return data[0].text

    def getResponseCode(self):
        """
        Get response_code of Xml
        """
        return int(self.tree.findall(".//*[@key='response_code']")[0].text)
        
        
class Tucows:
    config = None
    defaultInfo = None
    def __init__(self, aConfig, aDefaultInfo, aDefaultUserInfo):
        '''
        Constructor

        Parameters
        aConfig : dict
            COnfiguration for the conection to Tucows
        aDefaultInfo: dict
            Info of the Reseller
        aDefaultUserInfo: dict
            user and pass info of the client 
        '''
        self.config = aConfig
        self.defaultInfo = aDefaultInfo
        self.defaultUserInfo = aDefaultUserInfo
        
    def test(self):
        '''
        Test of conection 
        '''
        xml = '''
<?xml version='1.0' encoding='UTF-8' standalone='no' ?>
<!DOCTYPE OPS_envelope SYSTEM 'ops.dtd'>
<OPS_envelope>
<header>
    <version>0.9</version>
</header>
<body>
<data_block>
    <dt_assoc>
        <item key="protocol">XCP</item>
        <item key="action">LOOKUP</item>
        <item key="object">DOMAIN</item>
        <item key="attributes">
         <dt_assoc>
                <item key="domain">myfirstopensrsapitest.com</item>
         </dt_assoc>
        </item>
    </dt_assoc>
</data_block>
</body>
</OPS_envelope>
'''
        return self.send(xml)
        
    def send(self, aXml:str):
        '''
        Send XML to Tucows

        Parameters:
        aXml: str

        Return:
        TucowsXMLResponse
            Response of Tucows
        '''
        r = requests.post(self.config['api_host_port'], data = aXml, headers=self.getHttpHeader(aXml) )
        return TucowsXMLResponse(r)

    def getHttpHeader(self, aXml: str):
        '''
        Get header for the http

        Parameters:
        aXML: str
        
        Return:
        Dict
           object of Header for Tucows connection  
        '''
        md5_obj = hashlib.md5()
        md5_obj.update((aXml + self.config['api_key']).encode())
        signature = md5_obj.hexdigest()

        md5_obj = hashlib.md5()
        md5_obj.update((signature + self.config['api_key']).encode())
        signature = md5_obj.hexdigest()

        headers = {
            'Content-Type':'text/xml',
            'X-Username': self.config['reseller_username'],
            'X-Signature':signature,
            };
        return headers

    def isFreeDomain(self, aDomain:str):
        '''
        Check if the domain is free to use.
        
        Parameters:
        aDomain: str

        Returns:
        Dict:
            Dictionary with values code and msg, if code = 1 then the procees is OK, else the msg indicate error
        '''
        xml = TucowsXMLRequest({ 'object' : 'DOMAIN', 'action' : 'LOOKUP'},
            { 'domain' : aDomain, 'no_cache': '1'})
        # print(xml.__str__())
        r = self.send(xml.__str__())
        # print(r.response.text)
        if (r.response.status_code == 200 and r.getIsSuccess() == '1' and r.getResponseCode() == 210):
            return 0, 'Ok'
        else:
            return 1, r.getResponseText()

    def getSuggestions(self, aDomain:str):
        """
        Get suggestion of a domain
        """
        otherName = self.getSimilarUrlName(aDomain)
        # print(otherName)
        baseList = []
        if (otherName != ''):
            resFree, msgFree = self.isFreeDomain(aDomain)
            if resFree == 0:
                baseList.append(otherName)
        
        xml = TucowsXMLRequest({'object' : 'DOMAIN','action': 'name_suggest'},
            {'services' : [{0: 'lookup'}, {1: 'suggestion'}] ,
             'searchstring' : aDomain,
             'languages' : [{0: 'es'}],
             'tlds' : [{0: '.com'}, {1: '.net'}, {2: '.org' }]})

        r = self.send(xml.__str__())
        if (r.response.status_code == 200):
            lookup = r.tree.findall(".//*[@key='lookup']/dt_assoc/item/[@key='items']/dt_array/item/dt_assoc/")
            suggestion = r.tree.findall(".//*[@key='suggestion']/dt_assoc/item/[@key='items']/dt_array/item/dt_assoc/")
            return 0, baseList + self.extractItems(lookup) + self.extractItems(suggestion)
        else:
            return 1, r.getResponseText()

    def getSimilarUrlName(self, domain: str):
        """
        Get similar name of a domain, example: text.com.ar returns text.ar
        """
        ext = [['.com.ar', '.ar'], ['com.br', '.br'], ['.com.pe', 'pe'], ['.com.mx', '.mx']]
        name = ''
        for e in ext:
            if domain[-7:] == e[0]:
                name = domain[0:len(domain)-7] + e[1]
            elif domain[-3:] == e[1]:
                name =  domain[0:len(domain)-3] + e[0]
        return name
        
    def extractItems(self,aValues):
        """
        Symbol’s value as variable is void: text
        """
        l = []
        domain = None
        for child in aValues:
            for i in child.iter():
                if i.get('key') == 'domain':
                    domain = i.text.strip()
                if i.get('key') == 'status':
                    status = i.text.strip()
                    if (status == 'available') and domain != None:
                        l.append(domain)
                    domain = None
        return l 
        
    def getNameserverList(self, aNameserverList: list):
        """
        Get list of nameserver 
        """
        newList = []
        cont = 1
        for idx, val in enumerate(aNameserverList):
            if val[-4:] != '.org':
                newList.append({str(idx): {'name' : val, 'sortorder': str(cont)}})
                cont=cont+1
        return newList

    def registerDomain(self, aDomain: str, aOwnerInfo: dict, aDns: list):
        '''
        Register domain in Tucows

        Parameters:
        aDomain:  str
            Domain to register in tucows
        aOwnerInfo: dict
            Info of the owner
        aDns: list
            List of DNS to configure the new domain
        Chek information https://domains.opensrs.guide/docs/sw_register-domain-or-trust_service-

        Returns:
        Dict:
            Dictionary with values code and msg, if code = 1 then the procees is OK, else the msg indicate error

        '''

        defaultValues = self.defaultInfo

        # dns_template

        params =  {'auto_renew' : '1',
             'custom_nameservers' : '1',
             # 'custom_tech_contact': '0',
             'domain': aDomain,
             'f_lock_domain': '0',
             'f_whois_privacy': '1',
             'handle': 'process',
             'reg_type': 'new',
             'nameserver_list': self.getNameserverList(aDns),
             'period': '1',
             'contact_set': {
                 'owner': aOwnerInfo,
                 'billing': aOwnerInfo,
                 'admin': aOwnerInfo,
                 # 'tech': aOwnerInfo
                 # 'billing': defaultValues,
                 # 'admin': defaultValues,
                 # 'tech': defaultValues
             }}
        params.update(self.defaultUserInfo);
        
        # check https://domains.opensrs.guide/docs/tld
        if (aDomain[-7:] == '.com.br'):
            tldData = {'tld_data' : {'br_register_number':  aOwnerInfo['document_number']}}
            params.update(tldData)

        if (aDomain[-7:] == '.com.mx' or aDomain[-3:] == '.mx'):
            if  aOwnerInfo['document_type'] == 'curp':
                tldData = {'tld_data' : {'registrant_type':  'organization'}}
            else:
                tldData = {'tld_data' : {'registrant_type':  'individual'}}
            params.update(tldData)

        if (aDomain[-7:] == '.com.ar' or aDomain[-7:] == '.com.pt'  or aDomain[-3:] == '.pt'):
            if aOwnerInfo['document_type'] == 'cuit':
                tldData ={'tld_data':  {'registrant_extra_info' : {'registrant_type': 'organization',
                                        'tax_number': aOwnerInfo['document_number']}}}
            elif aOwnerInfo['document_type'] == 'dni':
                tldData = {'tld_data': {'registrant_extra_info' : {'registrant_type': 'individual',
                                        'id_card_number': aOwnerInfo['document_number'],
                                        'tax_number': aOwnerInfo['document_number']}}}
            params.update(tldData)
        
        xml = TucowsXMLRequest( {'action' : 'SW_REGISTER', 'object' : 'DOMAIN'},
            params)
        xmlStr = xml.__str__();
        # print(xmlStr)
        r = self.send(xmlStr)
        if r.response.status_code == 200 and r.getIsSuccess() == '1':
            return 0, 'Ok'
        else:
            # print(r.response.content)
            return r.getResponseCode(), r.getResponseText() + ' : ' + r.getErrorText()
        


        
