import json
import requests
import time
import urllib3
import csv
from datetime import datetime
import argparse
import dsFunc

baseURL, email, password, filePath, verify, skipColl, sec = dsFunc.instSelect()

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fileName', help='the name of the CSV with the \
bitstream name changes. optional - if not provided, the script will ask for \
input')
args = parser.parse_args()
if args.uri:
    fileName = args.fileName
else:
    fileName = input('Enter file name: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL + '/rest/login', headers=header,
                        verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}

status = requests.get(baseURL + '/rest/status', headers=header,
                      cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated', userFullName)

f = csv.writer(open(filePath + 'editBitstreamName'
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['itemID'] + ['oldBitstreamName'] + ['newBitstreamName'] + ['post'])
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        oldValue = row['oldFileId']
        newValue = row['newFileId']
        handle = row['handle']
        endpoint = baseURL + '/rest/handle/' + handle
        item = requests.get(endpoint, headers=header, cookies=cookies,
                            verify=verify).json()
        itemID = str(item['uuid'])
        bitstreams = requests.get(baseURL + '/rest/items/' + itemID
                                  + '/bitstreams', headers=header,
                                  cookies=cookies, verify=verify).json()
        for bitstream in bitstreams:
            oldBitstreamName = bitstream['name']
            bitstreamID = bitstream['link']
            updatedBitstream = json.dumps(bitstream)
            print(json.dumps(bitstream))
            updatedBitstream = updatedBitstream.replace(oldValue, newValue)
            post = requests.put(baseURL + bitstreamID, headers=header,
                                cookies=cookies, verify=verify,
                                data=updatedBitstream)
            print(post)
            f.writerow([itemID] + [oldValue] + [newValue] + [post])
            updatedItemMetadataList = []
            metadata = requests.get(baseURL + '/rest/items/' + str(itemID)
                                    + '/metadata', headers=header,
                                    cookies=cookies, verify=verify).json()
            for l in range(0, len(metadata)):
                metadata[l].pop('schema', None)
                metadata[l].pop('element', None)
                metadata[l].pop('qualifier', None)
                updatedItemMetadataList.append(metadata[l])
            provNote = 'Bitstream name changed from ' + oldValue + ' to '
            provNote += newValue + ' through a batch process on '
            provNote += datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            provNote += '.'
            provNoteElement = {}
            provNoteElement['key'] = 'dc.description.provenance'
            provNoteElement['value'] = provNote
            provNoteElement['language'] = 'en_US'
            updatedItemMetadataList.append(provNoteElement)
            updatedItemMetadata = json.dumps(updatedItemMetadataList)
            delete = requests.delete(baseURL + '/rest/items/' + str(itemID)
                                     + '/metadata', headers=header,
                                     cookies=cookies, verify=verify)
            print(delete)
            post = requests.put(baseURL + '/rest/items/' + str(itemID)
                                + '/metadata', headers=header, cookies=cookies,
                                verify=verify, data=updatedItemMetadata)
            print(post)

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
