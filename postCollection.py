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
communityHandle = raw_input('Enter community handle: ')
collectionName = raw_input('Enter collection name: ')

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

#create file list and export csv
fileList = {}
for root, dirs, files in os.walk(directory, topdown=True):
    print 'building file list'
    for file in files:
        if file.endswith(fileExtension):
            fileList[file[:file.index('.')]] = os.path.join(root, file).replace('\\','/')
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'File list creation time: ','%d:%02d:%02d' % (h, m, s)

f=csv.writer(open(collectionName.replace(' ','')+'fileList.csv', 'wb'))
f.writerow(['itemID'])

for k,v in fileList.items():
    f.writerow([v[v.rindex('/')+1:]])

f2=open('fileListDict.txt', 'wb')
f2.write(json.dumps(fileList))

# f3=open('fileListDict.txt', 'rb')
# fileList = json.load(f3)

#Get community ID
endpoint = baseURL+'/rest/handle/'+communityHandle
community = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
communityID = str(community['uuid'])

#Post collection
collection = json.dumps({'name': collectionName})
post = requests.post(baseURL+'/rest/communities/'+communityID+'/collections', headers=header, cookies=cookies, verify=verify, data=collection).json()
collectionID = post['link']

# Post items
collectionMetadata = json.load(open(directory+'/'+'metadata.json'))
for itemMetadata in collectionMetadata:
    fileExists = ''
    updatedItemMetadata = {}
    updatedItemMetadataList = []
    for element in itemMetadata['metadata']:
        if element['key'] == 'fileIdentifier':
            fileIdentifier = element['value']
        else:
            updatedItemMetadataList.append(element)
    updatedItemMetadata['metadata'] = updatedItemMetadataList
    updatedItemMetadata = json.dumps(updatedItemMetadata)
    for k in fileList:
        if fileIdentifier in k:
            fileExists = True
    if fileExists == True:
        print fileIdentifier
        post = requests.post(baseURL+collectionID+'/items', headers=header, cookies=cookies, verify=verify, data=updatedItemMetadata).json()
        print json.dumps(post)
        itemID = post['link']

        # #Post bitstream - front and back
        # for k,v in fileList.items():
        #     if k == fileIdentifier + '-Front':
        #         bitstream = fileList[k]
        #         fileName = bitstream[bitstream.rfind('/')+1:]
        #         data = open(bitstream, 'rb')
        #         post = requests.post(baseURL+itemID+'/bitstreams?name='+fileName, headers=headerFileUpload, verify=verify, data=data).json()
        #         print post
        #
        # for k,v in fileList.items():
        #     if k == fileIdentifier + '-Back':
        #         bitstream = fileList[k]
        #         fileName = bitstream[bitstream.rfind('/')+1:]
        #         data = open(bitstream, 'rb')
        #         post = requests.post(baseURL+itemID+'/bitstreams?name='+fileName, headers=headerFileUpload, verify=verify, data=data).json()
        #         print post

        #Post bitstream - starts with file identifier
        for k,v in fileList.items():
            if k.startswith(fileIdentifier):
                bitstream = fileList[k]
                fileName = bitstream[bitstream.rfind('/')+1:]
                data = open(bitstream, 'rb')
                post = requests.post(baseURL+itemID+'/bitstreams?name='+fileName, headers=headerFileUpload, cookies=cookies, verify=verify, data=data).json()
                print post

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
