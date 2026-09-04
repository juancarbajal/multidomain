from multidomain.tucows import *
from  multidomain.environment import Environment

e = Environment()
tucows = e.getTucowsConnection()

domain = 'test.com.br'
xml = TucowsXMLRequest({ 'object' : 'DOMAIN', 'action' : 'get_price'},
                       { 'domain' : domain,
                        'period' : '1',
                        'all_periods':'1',
                        'no_cache': '1',
                        'reg_type': 'new'})

r = tucows.send(xml.__str__())
print(r.response.status_code)
print(r.response.text)
