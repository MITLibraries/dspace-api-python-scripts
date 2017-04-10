import json
import requests
import secrets
import datetime

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath

directory = filePath+raw_input('Enter directory name: ')

data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
headerAuthFileUpload = {'accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'

#Post community
communityName = 'Test Community'
community = json.dumps({'name': communityName})
post = requests.post(baseURL+'/rest/communities', headers=headerAuth, data=community).json()
print json.dumps(post)
communityID = post['link']

#Post collection
collectionName = 'Test Collection'
collection = json.dumps({'name': collectionName})
post = requests.post(baseURL+communityID+'/collections', headers=headerAuth, data=collection).json()
print json.dumps(post)
collectionID = post['link']

#Post items
collectionMetadata = json.load(open(filePath+'sampleCollectionMetadata.json'))
for itemMetadata in collectionMetadata:
    for element in itemMetadata['metadata']:
        if element['key'] == 'dc.identifier.other':
            imageIdentifier = element['value']
    itemMetadata = json.dumps(itemMetadata)
    post = requests.post(baseURL+collectionID+'/items', headers=headerAuth, data=itemMetadata).json()
    print json.dumps(post)
    itemID = post['link']

    #Post bitstream
    bitstream = directory+'/'+imageIdentifier+'.jpg'
    fileName = bitstream[bitstream.rfind('/')+1:]
    data = open(bitstream, 'rb')
    files = {'file': open(bitstream, 'rb')}
    post = requests.post(baseURL+itemID+'/bitstreams?name='+fileName, headers=headerAuthFileUpload, data=data).json()

    #Create provenance note
    provNote = {}
    provNote['key'] = 'dc.description.provenance'
    provNote['language'] = 'en_US'
    bitstreams = requests.get(baseURL+itemID+'/bitstreams', headers=headerAuth).json()
    bitstreamCount = len(bitstreams)
    utc= datetime.datetime.utcnow()
    utcTime = utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    provNoteValue = 'Made available in DSpace on '+utcTime+' (GMT). No. of bitstreams: '+str(bitstreamCount)
    for bitstream in bitstreams:
        fileName = bitstream['name']
        size = str(bitstream['sizeBytes'])
        checksum = bitstream['checkSum']['value']
        algorithm = bitstream ['checkSum']['checkSumAlgorithm']
        provNoteValue = provNoteValue+' '+fileName+': '+size+' bytes, checkSum: '+checksum+' ('+algorithm+')'
    provNote['value'] = provNoteValue
    provNote = json.dumps([provNote])

    #Post provenance note
    post = requests.put(baseURL+itemID+'/metadata', headers=headerAuth, data=provNote)
    print post

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)
