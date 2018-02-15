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
        
def createMetadataElementCSVSplitField (key, valueSource, language):
    if row[valueSource] != '':
        if '|' in row[valueSource]:
            values = row[valueSource].split('|')
            for value in values:
                if language != '':
                    metadataElement = {'key': key, 'language': language, 'value': value}
                    metadata.append(metadataElement)
                else:
                    metadataElement = {'key': key, 'value': value}
                    metadata.append(metadataElement)
        else:
            value = row[valueSource]
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
        createMetadataElementCSV('fileIdentifier', '????', '')
        createMetadataElementCSV('dc.contributor.author', '????', '')
        createMetadataElementCSV('dc.contributor.other', '????', '')
        createMetadataElementCSV('dc.date.created', '????', '')
        createMetadataElementCSV('dc.description.abstract', '????', 'en_US')
        createMetadataElementCSV('dc.format.extent', '????', '')
        createMetadataElementDirect('dc.format.mimetype', '????', 'en_US')
        createMetadataElementDirect('dc.identifier.other', '????','')
        createMetadataElementDirect('dc.language.iso', '????', 'en_US')
        createMetadataElementDirect('dc.publisher', 'Johns Hopkins University Sheridan Libraries', 'en_US')
        createMetadataElementDirect('dc.relation', 'Access the finding aid for the full ???? collection at ?????.', '')
        createMetadataElementCSV('dc.relation.ispartof', '????', 'en_US')
        createMetadataElementDirect('dc.rights', 'Single copies may be made for research purposes. Researchers are responsible for determining any copyright questions. It is not necessary to seek our permission as the owner of the physical work to publish or otherwise use public domain materials that we have made available for use, unless Johns Hopkins University holds the copyright. If you are the copyright owner of this content and wish to contact us regarding our choice to provide access to this material online, please visit our takedown policy at https://www.library.jhu.edu/policy/digital-collections-statement-use-takedown-policy/.', 'en_US')
        createMetadataElementDirect('dc.subject', '????', 'en_US')
        createMetadataElementCSV('dc.title', '????', 'en_US')
        createMetadataElementDirect('dc.type', '????', 'en_US')


        item = {'metadata': metadata}
        metadataGroup.append(item)
        counter = counter + 1
        print counter

f=open('metadata.json', 'w')
json.dump(metadataGroup, f)
