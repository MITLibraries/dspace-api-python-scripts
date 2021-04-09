import csv


def create_json_metadata(metadata_csv, multiple_terms):
    """Creates JSON metadata from a CSV."""
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        metadata_group = []
        # WE SHOULD DISCUSS HOW TO HANDLE MAPPING DICT CHANGES
        mapping_dict = {'file_identifier': ['file_identifier'],
                        'dc.title': ['title', 'en_US'],
                        'dc.relation.isversionof': ['uri'],
                        'dc.contributor.author': ['authors', None, '|']
                        }
        for row in reader:
            metadata_rec = []
            if multiple_terms == 'delimited':
                metadata_rec = create_metadata_rec_delim(mapping_dict, row,
                                                         metadata_rec)
            else:
                metadata_rec = create_metadata_rec_num_col(row, metadata_rec)
            item = {'metadata': metadata_rec}
            metadata_group.append(item)
        return metadata_group


def create_metadata_rec_delim(mapping_dict, row, metadata_rec):
    """Uses a mapping dict to create a metadata record from a series of metadata
     elements."""
    for k, v in mapping_dict.items():
        if len(v) == 3:
            metadata_elems = metadata_elems_from_row(row, k, v[0], v[1], v[2])
        elif len(v) == 2:
            metadata_elems = metadata_elems_from_row(row, k, v[0], v[1])
        else:
            metadata_elems = metadata_elems_from_row(row, k, v[0])
        for metadata_elem in metadata_elems:
            metadata_rec.append(metadata_elem)
    return metadata_rec


def create_metadata_rec_num_col(row, metadata_rec):
    """Uses a CSV that contains DC property column names and numbered columns
    for multiple terms to create a metadata record from a series of metadata
     elements."""
    for csv_key, csv_value in row.items():
        if csv_value is not None:
            if csv_key[-1].isdigit():
                dc_key = csv_key[:-2]
            else:
                dc_key = csv_key
            # THE FIELDS THAT SHOULDN'T RECEIVE A LANG TAG IS ALSO LIKELY
            # CHANGE WITH THE MAPPING DICT
            if dc_key not in ['dc.contributor.author', 'file_identifier',
                              'dc.relation.isversionof', 'dc.date.issued']:
                metadata_elems = metadata_elems_from_row(row, dc_key, csv_key,
                                                         'en_US')
            else:
                metadata_elems = metadata_elems_from_row(row, dc_key, csv_key)
            for metadata_elem in metadata_elems:
                metadata_rec.append(metadata_elem)
    return metadata_rec


def metadata_elems_from_row(row, key, field, language=None, delimiter=''):
    """Create a metadata element from a CSV row."""
    metadata_elems = []
    if row[field] != '':
        if delimiter:
            values = row[field].split(delimiter)
        else:
            values = [row[field]]
        for value in values:
            metadata_elem = {'key': key, 'language': language, 'value':
                             value}
            metadata_elems.append({k: v for k, v in metadata_elem.items()
                                  if v is not None})
    return metadata_elems
