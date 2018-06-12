import json
import requests
import time
import csv
import urllib3
import argparse


def main():
    # NOTE: this is the secrets file, not a module
    import secrets

    # define defaults
    response_timeout = 1
    limit = 100

    # begin: argument parsing
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')

    parser.add_argument('-i', '--handle',
                        help='handle of the object to retreive. optional - if not provided, the script will ask for input')

    # bitstream formats:
    # REM: set number of args
    # '+' == 1 or more.
    # '*' == 0 or more.
    # '?' == 0 or 1.
    # An int is an explicit number of arguments to accept.
    parser.add_argument('-f', '--formats', nargs='*',
                        help='optional list of bitstream formats. will return all formats if not provided')

    parser.add_argument('-dl', '--download', action='store_true',
                        help='download bitstreams (rather than just retreive metadata about them). default: false')

    parser.add_argument('-rt', '--rtimeout', type=int,
                        help='response timeout - number of seconds to wait for a response. not a timeout for a download or run of the entire script. default: ' + str(response_timeout))

    parser.add_argument('-l', '--limit', type=int,
                        help='limit to the number of objects to return in a given request. default: ' + str(limit))

    args = parser.parse_args()

    if args.rtimeout:
        response_timeout = args.rtimeout

    if args.limit:
        limit = args.limit

    if args.verbose:
        print('verbosity turned on')

        if args.handle:
            print('retreiving object with handle {}').format(args.handle)

        if args.formats:
            print('filtering results to the following bitstream formats: {}').format(args.formats)
        else:
            print('returning bitstreams of any format')

        if args.download:
            print('downloading bitstreams')

        if args.rtimeout:
            print('response_timeout set to {}').format(response_timeout)

    # end: argument parsing

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
    if secretsVersion != '':
        try:
            secrets = __import__(secretsVersion)
            print('Accessing Production')
        except ImportError:
            print('Accessing Stage')
    else:
        print('Accessing Stage')

    baseURL = secrets.baseURL
    email = secrets.email
    password = secrets.password
    filePath = secrets.filePath
    verify = secrets.verify

    if args.handle:
        handle = args.handle
    else:
        handle = raw_input('Enter handle: ')

    startTime = time.time()
    data = {'email': email, 'password': password}
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data, timeout=response_timeout).cookies['JSESSIONID']
    cookies = {'JSESSIONID': session}
    headerFileUpload = {'accept': 'application/json'}
    cookiesFileUpload = cookies
    status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify, timeout=response_timeout).json()
    userFullName = status['fullname']
    print 'authenticated'

    # NOTE: expanding bitstreams to get the count, in case this is an item
    endpoint = baseURL+'/rest/handle/'+handle+'?expand=bitstreams'
    dsObject = requests.get(endpoint, headers=header, cookies=cookies, verify=verify, timeout=response_timeout).json()
    if args.verbose: print dsObject
    dsObjectID = dsObject['uuid']
    # TODO: extend
    if dsObject['type'] == 'collection':
        if args.verbose: print dsObject['type']

        itemList = []
        offset = 0
        items = ''
        while items != []:
            items = requests.get(baseURL+'/rest/collections/'+str(dsObjectID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify, timeout=response_timeout)
            while items.status_code != 200:
                time.sleep(5)
                items = requests.get(baseURL+'/rest/collections/'+str(dsObjectID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify, timeout=response_timeout)
            items = items.json()
            for k in range(0, len(items)):
                itemID = items[k]['uuid']
                itemID = '/rest/items/'+itemID
                itemHandle = items[k]['handle']
                itemList.append(itemID)
            offset = offset + 200

        f = csv.writer(open(filePath+'handlesAndBitstreams.csv', 'wb'))
        f.writerow(['bitstream']+['handle'])

        for item in itemList:
            bitstreams = requests.get(baseURL+itemID+'/bitstreams', headers=header, cookies=cookies, verify=verify, timeout=response_timeout).json()
            for bitstream in bitstreams:
                fileName = bitstream['name']
                fileName.replace('.pdf', '')
                f.writerow([fileName]+[itemHandle])

    elif dsObject['type'] == 'item':
        if args.verbose: print(dsObject['type'])

        itemHandle = dsObject['handle']

        f = csv.writer(open(filePath+itemHandle.replace('/', '-')+'_bitstreams.csv', 'wb'))
        f.writerow(['sequenceId']+['name']+['format']+['bundleName'])

        bitstreamCount = len(dsObject['bitstreams'])
        dlBitstreams = []
        offset = 0
        bitstreams = ''
        # while bitstreams != []:
        while bitstreamCount > 0:
            # don't retreive more bitstreams than we have left
            if limit > bitstreamCount:
                limit = bitstreamCount
            print('bitstreamCount: {0} offset: {1} limit: {2}').format(bitstreamCount, offset, limit)
            bitstreams = requests.get(baseURL+'/rest/items/' + str(dsObjectID) + '/bitstreams?limit=' + str(limit) + '&offset='+str(offset), headers=header, cookies=cookies, verify=verify, timeout=response_timeout)
            bitstreams.raise_for_status()  # ensure we notice bad responses
            bitstreams = bitstreams.json()
            for bitstream in bitstreams:
                if args.formats and bitstream['format'] in args.formats or not args.formats:
                    if args.verbose: print(bitstream)
                    sequenceId = str(bitstream['sequenceId'])
                    fileName = bitstream['name']
                    fileFormat = bitstream['format']
                    bundleName = bitstream['bundleName']
                    f.writerow([sequenceId]+[fileName]+[fileFormat]+[bundleName])

                    if args.download:
                        dlBitstreams.append(bitstream)
            offset += limit
            bitstreamCount -= limit

        for dlBitstream in dlBitstreams:
            response = requests.get(baseURL + str(dlBitstream['retrieveLink']), headers=header, cookies=cookies, verify=verify, timeout=response_timeout)
            response.raise_for_status()  # ensure we notice bad responses
            file = open(filePath + dlBitstream['name'], 'wb')
            file.write(response.content)
            file.close()
    else:
        print('object is of an invalid type for this script ({}). please enter the handle of an item or a collection.').format(dsObject['type'])


    logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify, timeout=response_timeout)

    elapsedTime = time.time() - startTime
    m, s = divmod(elapsedTime, 60)
    h, m = divmod(m, 60)
    print('Total script run time: {:01.0f}:{:02.0f}:{:02.0f}').format(h, m, s)


if __name__ == "__main__": main()
