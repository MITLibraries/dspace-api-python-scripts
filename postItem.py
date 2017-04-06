import json
import requests
import secrets

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath

data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
headerAuthFileUpload = {'accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'
#
#Post community
communityName = 'Test Community'
community = json.dumps({'name': communityName})
post = requests.post(baseURL+'/rest/communities', headers=headerAuth, data=community).json()
print json.dumps(post)
communityID = post['link']
print communityID

#Post collection
collectionName = 'Test Collection'
collection = json.dumps({'name': collectionName})
post = requests.post(baseURL+communityID+'/collections', headers=headerAuth, data=collection).json()
print json.dumps(post)
collectionID = post['link']

#Post item
item = json.dumps({'metadata': [{'key': 'dc.title', 'language': 'en_US', 'value': 'testing123'}]})
post = requests.post(baseURL+collectionID+'/items', headers=headerAuth, data=item).json()
print json.dumps(post)
itemID = post['link']

#Post bitstream
#bitstream = filePath+'test.txt'
bitstream = filePath+'testImage.jpg'
#bitstream = filePath+'A.pdf'
#bitstream = filePath+'test.pdf'

fileName = bitstream[bitstream.rfind('/')+1:]
files = {'file': open(bitstream, 'rb')}
data = json.dumps({'name': fileName, 'sequenceId': 1})
post = requests.post(baseURL+itemID+'/bitstreams?name='+fileName, headers=headerAuthFileUpload, files=files).json()
print json.dumps(post)
metadata = requests.get(baseURL+itemID+'/metadata', headers=headerAuth).json()

updatedMetadata = []
for metadatum in metadata:
    if metadatum['key'] != 'dc.description.provenance':
        print 'yay'
        updatedMetadata.append(metadatum)
    else:
        value = metadatum['value']
        time = value[value.index('DSpace on ')+10:value.index(' (GMT)')]
        print time
        print 'nay'
        provNote = {}
        provNote['key'] = 'dc.description.provenance'
        provNote['language'] = 'en_US'
        bitstreams = requests.get(baseURL+itemID+'/bitstreams', headers=headerAuth).json()
        bitstreamCount = len(bitstreams)
        provNoteValue = 'Made available in DSpace on '+time+' (GMT). No. of bitstreams: '+str(bitstreamCount)
        for bitstream in bitstreams:
            fileName = bitstream['name']
            size = str(bitstream['sizeBytes'])
            checksum = bitstream['checkSum']['value']
            print checksum
            algorithm = bitstream ['checkSum']['checkSumAlgorithm']
            print algorithm
            provNoteValue = provNoteValue+' '+fileName+': '+size+' bytes, checkSum: '+checksum+' ('+algorithm+')'
        print provNoteValue
        provNote['value'] = provNoteValue
        print provNote
        updatedMetadata.append(provNote)
updatedMetadata = json.dumps(updatedMetadata)

delete = requests.delete(baseURL+itemID+'/metadata', headers=headerAuth)
print delete
post = requests.put(baseURL+itemID+'/metadata', headers=headerAuth, data=updatedMetadata)
print post

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)
