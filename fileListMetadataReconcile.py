# -*- coding: utf-8 -*-
import csv
import time
import os
import argparse
import dsFunc

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', help='the directory of the files. '
                    'optional - if not provided, the script will ask for '
                    'input')
parser.add_argument('-f', '--fileNameCSV', help='the metadata CSV file. '
                    'optional - if not provided, the script will ask for '
                    'input')
parser.add_argument('-e', '--fileExtension', help='the file extension. '
                    'optional - if not provided, the script will ask for '
                    'input')
args = parser.parse_args()

if args.directory:
    directory = args.directory
else:
    directory = input('Enter directory (C:/Test/): ')
if args.fileNameCSV:
    fileNameCSV = args.fileNameCSV
else:
    fileNameCSV = input('Enter metadata CSV file: ')
if args.fileExtension:
    fileExtension = args.fileExtension
else:
    fileExtension = input('Enter file extension: ')

startTime = time.time()
fileIdentifierList = []
for root, dirs, files in os.walk(directory, topdown=True):
    for file in files:
        if file.endswith(fileExtension):
            file.replace('.' + fileExtension, '')
            fileIdentifierList.append(file)

dsFunc.elapsedTime(startTime, 'File list creation time')

f = csv.writer(open('collectionfileList.csv', 'w'))
f.writerow(['fileName'])

for file in fileIdentifierList:
    f.writerow([file])

metadataIdentifierList = []
f = csv.writer(open('metadataFileList.csv', 'w'))
f.writerow(['metadataItemID'])
with open(fileNameCSV) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        value = row['fileIdentifier']
        f.writerow([value])
        metadataIdentifierList.append(value)

fileMatches = []
for fileID in fileIdentifierList:
    for metadataID in metadataIdentifierList:
        if fileID.startswith(metadataID):
            fileMatches.append(fileID)

f = csv.writer(open('filesNotInMetadata.csv', 'w'))
f.writerow(['fileItemID'])
filesNotInMetadata = set(fileIdentifierList) - set(fileMatches)
for file in filesNotInMetadata:
    f.writerow([file])

metadataMatches = []
for metadataID in metadataIdentifierList:
    for fileID in fileIdentifierList:
        if fileID.startswith(metadataID):
            metadataMatches.append(metadataID)

metadataWithNoFiles = set(metadataIdentifierList) - set(metadataMatches)

with open(fileNameCSV) as csvfile:
    f = csv.writer(open('metadataWithNoFiles.csv', 'w'))
    reader = csv.DictReader(csvfile)
    header = next(reader)
    headerRow = []
    for k, v in header.iteritems():
        headerRow.append(k)
    f.writerow(headerRow)
    for row in reader:
        csvRow = []
        for metadata in metadataWithNoFiles:
            if metadata == row['fileIdentifier']:
                for value in headerRow:
                    csvRow.append(row[value])
                f.writerow(csvRow)

with open(fileNameCSV) as csvfile:
    f = csv.writer(open('metadataWithFiles.csv', 'w'))
    reader = csv.DictReader(csvfile)
    header = next(reader)
    headerRow = []
    for k, v in header.iteritems():
        headerRow.append(k)
    f.writerow(headerRow)
    for row in reader:
        csvRow = []
        for metadata in metadataMatches:
            if metadata == row['fileIdentifier']:
                for value in headerRow:
                    csvRow.append(row[value])
                f.writerow(csvRow)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
