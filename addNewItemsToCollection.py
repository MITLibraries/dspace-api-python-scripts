import json
import requests
import secrets
import datetime
import time
import os
import csv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

directory = raw_input('Enter directory name: ')
fileExtension = '.'+raw_input('Enter file extension: ')
collectionHandle = raw_input('Enter collection handle: ')

startTime = time.time()

#create file list and export csv
fileList = {}
for root, dirs, files in os.walk(directory, topdown=True):
    for file in files:
        if file.endswith(fileExtension):
            fileList[file[:file.index('.')]] = os.path.join(root, file).replace('\\','/')
            print file
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'File list creation time: ','%d:%02d:%02d' % (h, m, s)

f=csv.writer(open(collectionHandle.replace('/','-')+'addedFilesList.csv', 'wb'))
f.writerow(['itemID'])

for k,v in fileList.items():
    f.writerow([v[v.rindex('/')+1:]])
counter = len(fileList)

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

#Get collection ID
endpoint = baseURL+'/rest/handle/'+collectionHandle
collection = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
collectionID = str(collection['uuid'])

# Post items
collectionMetadata = json.load(open(directory+'/'+'metadata.json'))
for itemMetadata in collectionMetadata:
    counter = counter - 1
    print 'Items remaining: ', counter
    updatedItemMetadata = {}
    updatedItemMetadataList = []
    for element in itemMetadata['metadata']:
        if element['key'] == 'fileIdentifier':
            fileIdentifier = element['value']
        else:
            updatedItemMetadataList.append(element)
    updatedItemMetadata['metadata'] = updatedItemMetadataList
    updatedItemMetadata = json.dumps(updatedItemMetadata)
    post = requests.post(baseURL+'/rest/collections/'+collectionID+'/items', headers=header, cookies=cookies, verify=verify, data=updatedItemMetadata).json()
    itemID = post['link']

    #Post bitstream
    bitstream = fileList[fileIdentifier]
    fileName = bitstream[bitstream.rfind('/')+1:]
    data = open(bitstream, 'rb')
    files = {'file': open(bitstream, 'rb')}
    post = requests.post(baseURL+itemID+'/bitstreams?name='+fileName, headers=headerFileUpload, verify=verify, data=data).json()

    #Create provenance notes
    provNote = {}
    provNote['key'] = 'dc.description.provenance'
    provNote['language'] = 'en_US'
    utc= datetime.datetime.utcnow()
    utcTime = utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    bitstreams = requests.get(baseURL+itemID+'/bitstreams', headers=header, cookies=cookies, verify=verify).json()
    bitstreamCount = len(bitstreams)
    provNoteValue = 'Submitted by '+userFullName+' ('+email+') on '+utcTime+' (GMT). No. of bitstreams: '+str(bitstreamCount)
    for bitstream in bitstreams:
        fileName = bitstream['name']
        size = str(bitstream['sizeBytes'])
        checksum = bitstream['checkSum']['value']
        algorithm = bitstream ['checkSum']['checkSumAlgorithm']
        provNoteValue = provNoteValue+' '+fileName+': '+size+' bytes, checkSum: '+checksum+' ('+algorithm+')'
    provNote['value'] = provNoteValue

    provNote2 = {}
    provNote2['key'] = 'dc.description.provenance'
    provNote2['language'] = 'en_US'

    provNote2Value = 'Made available in DSpace on '+utcTime+' (GMT). No. of bitstreams: '+str(bitstreamCount)
    for bitstream in bitstreams:
        fileName = bitstream['name']
        size = str(bitstream['sizeBytes'])
        checksum = bitstream['checkSum']['value']
        algorithm = bitstream ['checkSum']['checkSumAlgorithm']
        provNote2Value = provNote2Value+' '+fileName+': '+size+' bytes, checkSum: '+checksum+' ('+algorithm+')'
    provNote2['value'] = provNote2Value

    #Post provenance notes
    provNote = json.dumps([provNote, provNote2])
    post = requests.put(baseURL+itemID+'/metadata', headers=header, cookies=cookies, verify=verify, data=provNote)
    print post

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ','%d:%02d:%02d' % (h, m, s)
