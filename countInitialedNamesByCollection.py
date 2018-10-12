import json
import requests
import secrets
import csv
import re
import time
import urllib3

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'
else:
    print 'Editing Stage'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print 'authenticated'

collectionIds = []
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
for community in communities:
    communityID = community['uuid']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies, verify=verify).json()
    for collection in collections:
        collectionID = collection['uuid']
        if collectionID != '45794375-6640-4efe-848e-082e60bae375':
            collectionIds.append(collectionID)

names = []
keys = ['dc.contributor.advisor', 'dc.contributor.author', 'dc.contributor.committeeMember', 'dc.contributor.editor', 'dc.contributor.illustrator', 'dc.contributor.other', 'dc.creator']

f = csv.writer(open('initialCountInCollection.csv', 'wb'))
f.writerow(['collectionName']+['handle']+['initialCount'])

for number, collectionID in enumerate(collectionIds):
    initialCount = 0
    collectionsRemaining = len(collectionIds) - number
    print collectionID, 'Collections remaining: ', collectionsRemaining
    collection = requests.get(baseURL+'/rest/collections/'+str(collectionID), headers=header, cookies=cookies, verify=verify).json()
    collectionName = collection['name'].encode('utf-8')
    collectionHandle = collection['handle']
    collSels = '&collSel[]=' + collectionID
    offset = 0
    recordsEdited = 0
    items = ''
    while items != []:
        for key in keys:
            endpoint = baseURL+'/rest/filtered-items?query_field[]='+key+'&query_op[]=exists&query_val[]='+collSels+'&limit=100&offset='+str(offset)
            print endpoint
            response = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
            items = response['items']
            for item in items:
                itemLink = item['link']
                metadata = requests.get(baseURL + itemLink + '/metadata', headers=header, cookies=cookies, verify=verify).json()
                for metadata_element in metadata:
                    if metadata_element['key'] == key:
                        individual_name = metadata_element['value'].encode('utf-8')
                        for metadata_element in metadata:
                            if metadata_element['key'] == 'dc.identifier.uri':
                                uri = metadata_element['value']
                                contains_initials = re.search(r'(\s|,|[A-Z]|([A-Z]\.))[A-Z](\s|$|\.|,)', individual_name)
                                contains_middleinitial = re.search(r'((\w{2,},\s)|(\w{2,},))\w[a-z]+', individual_name)
                                contains_parentheses = re.search(r'\(|\)', individual_name)
                                if contains_middleinitial:
                                    continue
                                elif contains_parentheses:
                                    continue
                                elif contains_initials:
                                    initialCount += 1
                                else:
                                    continue
        offset = offset + 200
        print offset
    if initialCount > 0:
        f.writerow([collectionName]+[baseURL+'/'+collectionHandle]+[str(initialCount).zfill(6)])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
