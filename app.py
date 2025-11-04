from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
username="tanvi.beri@grazitti.com"
password="G@123456"
token="FaE4YWTQADwkJT3jrnUULKX2"
domain="login"
try:
    sf = Salesforce(username=username, password=password + token, domain=domain)
except SalesforceAuthenticationFailed as e:
    print(e)
