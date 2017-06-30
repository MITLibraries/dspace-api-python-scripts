import json
import requests
import secrets
import datetime

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

requests.packages.urllib3.disable_warnings()

directory = filePath+raw_input('Enter directory name: ')
fileExtension = '.'+raw_input('Enter file extension: ')
communityName = raw_input('Enter community name: ')
collectionName = raw_input('Enter collectionn name: ')

data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
headerAuthFileUpload = {'accept':'application/json', 'rest-dspace-token':session}
status = requests.get(baseURL+'/rest/status', headers=headerAuth, verify=verify).json()
userFullName = status['fullname']
print 'authenticated'

#Post community
community = json.dumps({'name': communityName})
post = requests.post(baseURL+'/rest/communities', headers=headerAuth, verify=verify, data=community).json()
communityID = post['link']

#Post collection
collection = json.dumps({'name': collectionName})
post = requests.post(baseURL+communityID+'/collections', headers=headerAuth, verify=verify, data=collection).json()
collectionID = post['link']

#Post items
collectionMetadata = json.load(open(directory+'/'+'collectionMetadata.json'))
for itemMetadata in collectionMetadata:
    for element in itemMetadata['metadata']:
        if element['key'] == 'dc.identifier.other':
            fileIdentifier = element['value']
    itemMetadata = json.dumps(itemMetadata)
    post = requests.post(baseURL+collectionID+'/items', headers=headerAuth, verify=verify, data=itemMetadata).json()
    print json.dumps(post)
    itemID = post['link']

    #Post bitstream
    bitstream = directory+'/'+fileIdentifier+fileExtension
    fileName = bitstream[bitstream.rfind('/')+1:]
    data = open(bitstream, 'rb')
    files = {'file': open(bitstream, 'rb')}
    post = requests.post(baseURL+itemID+'/bitstreams?name='+fileName, headers=headerAuthFileUpload, verify=verify, data=data).json()

    #Create provenance notes
    provNote = {}
    provNote['key'] = 'dc.description.provenance'
    provNote['language'] = 'en_US'
    utc= datetime.datetime.utcnow()
    utcTime = utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    bitstreams = requests.get(baseURL+itemID+'/bitstreams', headers=headerAuth, verify=verify).json()
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
    post = requests.put(baseURL+itemID+'/metadata', headers=headerAuth, verify=verify, data=provNote)
    print post

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth, verify=verify)
