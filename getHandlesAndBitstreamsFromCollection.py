import json
import requests
import secrets
import time
import csv

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'
else:
    print 'Editing Stage'

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

requests.packages.urllib3.disable_warnings()

handle = raw_input('Enter handle: ')

data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'
startTime = time.time()

endpoint = baseURL+'/rest/handle/'+handle
collection = requests.get(endpoint, headers=headerAuth, verify=verify).json()
collectionID = collection['id']
collectionTitle = requests.get(endpoint, headers=headerAuth, verify=verify).json()
endpoint = baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=5000'
itemList = requests.get(endpoint, headers=headerAuth, verify=verify).json()

f=csv.writer(open(filePath+'handlesAndBitstreams.csv', 'wb'))
f.writerow(['bitstream']+['handle'])

for item in itemList:
    itemHandle = item['handle']
    itemID = str(item['link'])

    bitstreams = requests.get(baseURL+itemID+'/bitstreams', headers=headerAuth, verify=verify).json()
    for bitstream in bitstreams:
        fileName = bitstream['name']
        fileName.replace('.pdf','')
        f.writerow([fileName]+[itemHandle])

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ','%d:%02d:%02d' % (h, m, s)
