import requests
import csv
import re
import time
import urllib3
import dsFunc

secretsVersion = input('To edit production server, enter the name of the \
secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        secrets = __import__('secrets')
        print('Editing Development')
else:
    secrets = __import__('secrets')
    print('Editing Development')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL + '/rest/login', headers=header, verify=verify,
                        params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}

status = requests.get(baseURL + '/rest/status', headers=header,
                      cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated', userFullName)

collectionIds = []
endpoint = baseURL + '/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies,
                           verify=verify).json()
for community in communities:
    communityID = community['uuid']
    collections = requests.get(baseURL + '/rest/communities/'
                               + str(communityID) + '/collections',
                               headers=header, cookies=cookies,
                               verify=verify).json()
    for collection in collections:
        collectionID = collection['uuid']
        if collectionID not in skippedCollections:
            collectionIds.append(collectionID)

names = []
keys = ['dc.contributor.advisor', 'dc.contributor.author',
        'dc.contributor.committeeMember', 'dc.contributor.editor',
        'dc.contributor.illustrator', 'dc.contributor.other', 'dc.creator']

f = csv.writer(open('initialCountInCollection.csv', 'w'))
f.writerow(['collectionName'] + ['handle'] + ['initialCount'])

for number, collectionID in enumerate(collectionIds):
    initialCount = 0
    collectionsRemaining = len(collectionIds) - number
    print(collectionID, 'Collections remaining: ', collectionsRemaining)
    collection = requests.get(baseURL + '/rest/collections/'
                              + str(collectionID), headers=header,
                              cookies=cookies, verify=verify).json()
    collectionName = collection['name']
    collectionHandle = collection['handle']
    collSels = '&collSel[]=' + collectionID
    offset = 0
    recordsEdited = 0
    items = ''
    regexCI = r'(\s|,|[A-Z]|([A-Z]\.))[A-Z](\s|$|\.|,)'
    regexMI = r'((\w{2,},\s)|(\w{2,},))\w[a-z] + '
    regexPR = r'\(|\)'
    while items != []:
        for key in keys:
            endpoint = baseURL + '/rest/filtered-items?query_field[]=' + key
            endpoint += '&query_op[]=exists&query_val[]=' + collSels
            endpoint += '&limit=100&offset=' + str(offset)
            print(endpoint)
            response = requests.get(endpoint, headers=header, cookies=cookies,
                                    verify=verify).json()
            items = response['items']
            for item in items:
                itemLink = item['link']
                metadata = requests.get(baseURL + itemLink + '/metadata',
                                        headers=header, cookies=cookies,
                                        verify=verify).json()
                for metadata_element in metadata:
                    if metadata_element['key'] == key:
                        indvdl_nm = metadata_element['value']
                        for metadata_element in metadata:
                            if metadata_element['key'] == 'dc.identifier.uri':
                                uri = metadata_element['value']
                                contains_initials = re.search(regexCI,
                                                              indvdl_nm)
                                contains_middleinitial = re.search(regexMI,
                                                                   indvdl_nm)
                                contains_parentheses = re.search(regexPR,
                                                                 indvdl_nm)
                                if contains_middleinitial:
                                    continue
                                elif contains_parentheses:
                                    continue
                                elif contains_initials:
                                    initialCount += 1
                                else:
                                    continue
        offset = offset + 200
        print(offset)
    if initialCount > 0:
        f.writerow([collectionName] + [baseURL + '/' + collectionHandle]
                   + [str(initialCount).zfill(6)])

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
