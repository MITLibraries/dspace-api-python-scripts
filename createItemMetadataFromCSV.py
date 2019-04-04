# -*- coding: utf-8 -*-
import json
import csv


def createMetadataElementCSV(key, valueSource, language):
    """Create metadata element."""
    value = row[valueSource]
    if value != '':
        if language != '':
            metadataElement = {'key': key, 'language': language,
                               'value': value}
            metadata.append(metadataElement)
        else:
            metadataElement = {'key': key, 'value': value}
            metadata.append(metadataElement)
    else:
        pass


def createMetadataElementCSVSplitField(key, valueSource, language):
    """Create multiple metadata elements from one field."""
    if row[valueSource] != '':
        if '|' in row[valueSource]:
            values = row[valueSource].split('|')
            for value in values:
                if language != '':
                    metadataElement = {'key': key, 'language': language,
                                       'value': value}
                    metadata.append(metadataElement)
                else:
                    metadataElement = {'key': key, 'value': value}
                    metadata.append(metadataElement)
        else:
            value = row[valueSource]
            if language != '':
                metadataElement = {'key': key, 'language': language,
                                   'value': value}
                metadata.append(metadataElement)
            else:
                metadataElement = {'key': key, 'value': value}
                metadata.append(metadataElement)
    else:
        pass


def createMetadataElementDirect(key, value, language):
    """Create metadata element with specified value."""
    if language != '':
        metadataElement = {'key': key, 'language': language, 'value': value}
        metadata.append(metadataElement)
    else:
        metadataElement = {'key': key, 'value': value}
        metadata.append(metadataElement)


fileName = input('Enter fileName (including \'.csv\'): ')

with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    counter = 0
    metadataGroup = []
    for row in reader:
        metadata = []
        createMetadataElementCSV('fileIdentifier', '????', '')
        createMetadataElementCSV('dc.contributor.author', '????', '')
        createMetadataElementCSV('dc.contributor.other', '????', '')
        createMetadataElementCSV('dc.date.issued', '????', '')
        createMetadataElementCSV('dc.description.abstract', '????', 'en_US')
        createMetadataElementCSV('dc.format.extent', '????', '')
        createMetadataElementDirect('dc.format.mimetype', '????', 'en_US')
        createMetadataElementDirect('dc.identifier.other', '????', '')
        createMetadataElementDirect('dc.language.iso', '????', 'en_US')
        createMetadataElementDirect('dc.publisher', '????', 'en_US')
        createMetadataElementDirect('dc.relation', 'Access other ?????.', '')
        createMetadataElementCSV('dc.relation.ispartof', '????', 'en_US')
        createMetadataElementDirect('dc.rights', '????', 'en_US')
        createMetadataElementDirect('dc.subject', '????', 'en_US')
        createMetadataElementCSV('dc.title', '????', 'en_US')
        createMetadataElementDirect('dc.type', '????', 'en_US')

        item = {'metadata': metadata}
        metadataGroup.append(item)
        counter = counter + 1
        print(counter)

f = open('metadata.json', 'w')
json.dump(metadataGroup, f)
