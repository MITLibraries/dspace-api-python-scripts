import json
import requests
import csv
import argparse
import urllib3
import dsFunc

inst = input('To edit production server, enter the name of the secrets file: ')
secrets = dsFunc.instSelect(inst)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skipColl = secrets.skipColl

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fileNameCSV', help='the metadata CSV file. \
optional - if not provided, the script will ask for input')
parser.add_argument('-i', '--handle', help='handle of the collection. \
optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.fileNameCSV:
    fileNameCSV = args.fileNameCSV
else:
    fileNameCSV = input('Enter the metadata CSV file (including \'.csv\'): ')
if args.handle:
    handle = args.handle
else:
    handle = input('Enter collection handle: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

endpoint = baseURL + '/rest/handle/' + handle
collection = requests.get(endpoint, headers=header, cookies=cookies,
                          verify=verify).json()
collectionID = collection['uuid']
print(collection)

# Enter abstract text here
abstractText = ''

seriesTitles = []

with open(fileNameCSV) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        seriesTitle = row['Series title']
        if seriesTitle not in seriesTitles:
            seriesTitles.append(seriesTitle)

seriesLinks = ''

for seriesTitle in seriesTitles:
    handleEdited = handle.replace('/', '%2F')
    editedSeriesTitle = seriesTitle.replace(' ', ' + ')
    seriesLink = '<li><a href="https://jscholarship.library.jhu.edu/'
    seriesLinks += 'discover?scope=' + handleEdited + '&query=%22'
    seriesLinks += editedSeriesTitle
    seriesLinks += '%22&sort_by=dc.title_sort&order=asc&submit=">'
    seriesLinks += seriesTitle + '</a></li>'
    seriesLinks += seriesLink

abstractText = '<p>' + abstractText + '</p>'
seriesLinks = '<ul>' + seriesLinks + '</ul>'
introductoryText = abstractText + seriesLinks

collection['introductoryText'] = introductoryText
collection = json.dumps(collection)
print(collection)
post = requests.put(baseURL + '/rest/collections/' + collectionID,
                    headers=header, cookies=cookies, verify=verify,
                    data=collection)
print(post)

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)
