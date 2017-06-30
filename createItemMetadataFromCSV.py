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
        createMetadataElementCSV('dc.creator', 'creator', '')
        createMetadataElementCSV('dc.date', 'date', '')
        createMetadataElementCSV('dc.subject', 'decade', 'en_US')
        createMetadataElementCSV('dc.description.abstract', 'description', 'en_US')
        createMetadataElementCSV('dc.description', 'notes', 'en_US')
        createMetadataElementCSV('dc.subject', 'photographType', 'en_US')
        createMetadataElementCSV('dc.relation.ispartof', 'location', 'en_US')
        createMetadataElementCSV('dc.identifier', 'identifier', '')
        createMetadataElementCSV('dc.format.extent', 'size', '')
        createMetadataElementCSV('dc.format.medium', 'medium', 'en_US')
        createMetadataElementCSV('dc.title', 'title', 'en_US')
        createMetadataElementCSV('dc.subject', 'subjectType', 'en_US')

        item = {'metadata': metadata}
        metadataGroup.append(item)
        counter = counter + 1
        print counter

f=open('metadata.json', 'w')
json.dump(metadataGroup, f)
