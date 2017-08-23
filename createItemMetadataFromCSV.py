# -*- coding: utf-8 -*-
import json
import csv

def createMetadataElementCSV (key, valueSource, language):
    value = row[valueSource]
    if value != '':
        if language != '':
            metadataElement = {'key': key, 'language': language, 'value': value}
            metadata.append(metadataElement)
        else:
            metadataElement = {'key': key, 'value': value}
            metadata.append(metadataElement)
    else:
        pass

def createMetadataElementDirect (key, value, language):
    if language != '':
        metadataElement = {'key': key, 'language': language, 'value': value}
        metadata.append(metadataElement)
    else:
        metadataElement = {'key': key, 'value': value}
        metadata.append(metadataElement)

filename = raw_input('Enter filename (including \'.csv\'): ')

with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    counter = 0
    metadataGroup = []
    for row in reader:
        metadata = []
        createMetadataElementCSV('dc.creator', 'Creator', '')
        createMetadataElementCSV('dc.date.issued', 'structuredDate', '')
        createMetadataElementCSV('dc.title', 'fullTitle', 'en_US')
        createMetadataElementCSV('dc.description.abstract', 'Description', 'en_US')
        createMetadataElementCSV('dc.description', 'Notes:', 'en_US')
        createMetadataElementCSV('fileIdentifier', 'File name', '')
        createMetadataElementDirect('dc.identifier.other', 'MS.0504','')
        createMetadataElementDirect('dc.language.iso', 'en_US', 'en_US')
        createMetadataElementDirect('dc.type', 'Text', 'en_US')
        createMetadataElementDirect('dc.format.mimetype', 'application/pdf', 'en_US')
        createMetadataElementDirect('dc.subject', 'magazines (periodicals)', 'en_US')
        createMetadataElementDirect('dc.subject', 'Maryland--Baltimore', 'en_US')
        createMetadataElementDirect('dc.subject', 'Engineering', 'en_US')
        createMetadataElementDirect('dc.subject', 'City planning', 'en_US')
        createMetadataElementDirect('dc.relation', 'Access the finding aid for the full Roland Park Company Records collection at http://archivesspace.library.jhu.edu/repositories/3/resources/533', '')
        # createMetadataElementCSV('dc.relation.ispartof', 'location', 'en_US')
        # createMetadataElementCSV('dc.identifier', 'identifier', '')
        # createMetadataElementCSV('dc.format.extent', 'size', '')
        # createMetadataElementCSV('dc.format.medium', 'medium', 'en_US')
        # createMetadataElementCSV('dc.title', 'title', 'en_US')
        # createMetadataElementCSV('dc.subject', 'subjectType', 'en_US')

        item = {'metadata': metadata}
        metadataGroup.append(item)
        counter = counter + 1
        print counter

f=open('metadata.json', 'w')
json.dump(metadataGroup, f)
