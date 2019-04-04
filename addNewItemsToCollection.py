import json
import requests
import datetime
import time
import os
import csv
import urllib3
import collections
import argparse

secretsVersion = input('To edit production server, enter the name of the \
secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        secrets = __import__(secrets)
        print('Editing Stage')
else:
    print('Editing Stage')

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', help='the directory of files to be \
ingested. optional - if not provided, the script will ask for input')
parser.add_argument('-e', '--fileExtension', help='the extension of files to \
be ingested. optional - if not provided, the script will ask for input')
parser.add_argument('-i', '--handle', help='handle of the object to retreive. \
optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.directory:
    directory = args.directory
else:
    directory = input('Enter directory name: ')
if args.fileExtension:
    fileExtension = args.fileExtension
else:
    fileExtension = '.' + input('Enter file extension: ')
if args.handle:
    handle = args.handle
else:
    handle = input('Enter handle: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

startTime = time.time()

# ccreate file list and export csv
fileList = {}
for root, dirs, files in os.walk(directory, topdown=True):
    for file in files:
        if file.endswith(fileExtension):
            fullFilePath = os.path.join(root, file).replace('\\', '/')
            fileList[file[:file.index('.')]] = fullFilePath
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('File list creation time: ', '%d:%02d:%02d' % (h, m, s))

f = csv.writer(open(handle.replace('/', '-') + 'addedFilesList.csv', 'w'))
f.writerow(['itemID'])

for k, v in fileList.items():
    f.writerow([v[v.rindex('/') + 1:]])
counter = len(fileList)

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL + '/rest/login', headers=header, verify=verify,
                        params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}
status = requests.get(baseURL + '/rest/status', headers=header,
                      cookies=cookies, verify=verify).json()
print(status)
userFullName = status['fullname']
print('authenticated')

# Get collection ID
endpoint = baseURL + '/rest/handle/' + handle
collection = requests.get(endpoint, headers=header, cookies=cookies,
                          verify=verify).json()
collectionID = str(collection['uuid'])
print(collectionID)

# Post items
collectionMetadata = json.load(open(directory + '/' + 'metadataNewFiles.json'))
for itemMetadata in collectionMetadata:
    counter = counter - 1
    print('Items remaining: ', counter)
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
    if fileExists is True:
        print(fileIdentifier)
        post = requests.post(baseURL + '/rest/collections/' + collectionID
                             + '/items', headers=header, cookies=cookies,
                             verify=verify, data=updatedItemMetadata).json()
        print(json.dumps(post))
        itemID = post['link']

    # #Post bitstream - front and back
    # for k, v in fileList.items():
    #     if k == fileIdentifier + '-Front':
    #         bitstream = fileList[k]
    #         fileName = bitstream[bitstream.rfind('/') + 1:]
    #         data = open(bitstream, 'rb')
    #         post = requests.post(baseURL + itemID + '/bitstreams?name='
    #                              + fileName, headers=headerFileUpload,
    #                              cookies=cookies, verify=verify,
    #                              data=data).json()
    #         print(post)
    #
    # for k, v in fileList.items():
    #     if k == fileIdentifier + '-Back':
    #         bitstream = fileList[k]
    #         fileName = bitstream[bitstream.rfind('/') + 1:]
    #         data = open(bitstream, 'rb')
    #         post = requests.post(baseURL + itemID + '/bitstreams?name='
    #                              + fileName, headers=headerFileUpload,
    #                              cookies=cookies, verify=verify,
    #                               data=data).json()
    #         print(post)

    # Post bitstream - starts with file identifier
    orderedFileList = collections.OrderedDict(sorted(fileList.items()))
    for k, v in orderedFileList.items():
        if k.startswith(fileIdentifier):
            bitstream = orderedFileList[k]
            fileName = bitstream[bitstream.rfind('/') + 1:]
            print(fileName)
            data = open(bitstream, 'rb')
            post = requests.post(baseURL + itemID + '/bitstreams?name='
                                 + fileName, headers=headerFileUpload,
                                 cookies=cookies, verify=verify,
                                 data=data).json()
            print(post)

    # Create provenance notes
    provNote = {}
    provNote['key'] = 'dc.description.provenance'
    provNote['language'] = 'en_US'
    utc = datetime.datetime.utcnow()
    utcTime = utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    bitstreams = requests.get(baseURL + itemID + '/bitstreams', headers=header,
                              cookies=cookies, verify=verify).json()
    bitstreamCount = len(bitstreams)
    provNoteValue = 'Submitted by ' + userFullName + ' (' + email + ') on '
    provNoteValue = provNoteValue + utcTime + ' (GMT). No. of bitstreams: '
    provNoteValue = provNoteValue + str(bitstreamCount)
    for bitstream in bitstreams:
        fileName = bitstream['name']
        size = str(bitstream['sizeBytes'])
        checksum = bitstream['checkSum']['value']
        algorithm = bitstream['checkSum']['checkSumAlgorithm']
        provNoteValue = provNoteValue + ' ' + fileName + ': ' + size
        provNoteValue = provNoteValue + ' bytes, checkSum: ' + checksum
        provNoteValue = provNoteValue + ' (' + algorithm + ')'
    provNote['value'] = provNoteValue

    provNote2 = {}
    provNote2['key'] = 'dc.description.provenance'
    provNote2['language'] = 'en_US'
    provNote2Value = 'Made available in DSpace on ' + utcTime
    provNote2Value = provNote2Value + ' (GMT). No. of bitstreams: '
    provNote2Value = provNote2Value + str(bitstreamCount)
    for bitstream in bitstreams:
        fileName = bitstream['name']
        size = str(bitstream['sizeBytes'])
        checksum = bitstream['checkSum']['value']
        algorithm = bitstream['checkSum']['checkSumAlgorithm']
        provNote2Value = provNote2Value + ' ' + fileName + ': ' + size
        provNote2Value = provNote2Value + ' bytes, checkSum: ' + checksum
        provNote2Value = provNote2Value + ' (' + algorithm + ')'
    provNote2['value'] = provNote2Value

    # Post provenance notes
    provNote = json.dumps([provNote, provNote2])
    post = requests.put(baseURL + itemID + '/metadata', headers=header,
                        cookies=cookies, verify=verify, data=provNote)
    print(post)

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
