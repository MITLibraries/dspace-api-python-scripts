# -*- coding: utf-8 -*-
import json
import csv

def createMetadataElement (key, value, language):
    value = row[value]
    if value != '':
        if language != '':
            metadataElement = {'key': key, 'language': language, 'value': value}
            metadata.append(metadataElement)
        else:
            metadataElement = {'key': key, 'value': value}
            metadata.append(metadataElement)
    else:
        pass

filename = raw_input('Enter filename (including \'.csv\'): ')

with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    counter = 0
    metadataGroup = []
    for row in reader:
        metadata = []
        createMetadataElement('dc.creator', 'creator', '')
        createMetadataElement('dc.date', 'date', '')
        createMetadataElement('dc.subject', 'decade', 'en_US')
        createMetadataElement('dc.description.abstract', 'description', 'en_US')
        createMetadataElement('dc.description', 'notes', 'en_US')
        createMetadataElement('dc.subject', 'photographType', 'en_US')
        createMetadataElement('dc.relation.ispartof', 'location', 'en_US')
        createMetadataElement('dc.identifier', 'identifier', '')
        createMetadataElement('dc.format.extent', 'size', '')
        createMetadataElement('dc.format.medium', 'medium', 'en_US')
        createMetadataElement('dc.title', 'title', 'en_US')
        createMetadataElement('dc.subject', 'subjectType', 'en_US')

        item = {'metadata': metadata}
        metadataGroup.append(item)
        counter = counter + 1
        print counter

f=open('metadata.json', 'w')
json.dump(metadataGroup, f)
