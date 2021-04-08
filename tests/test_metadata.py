import csv

from dsaps import metadata


def test_create_json_metadata(input_dir, json_metadata_delim):
    """Test create_json_metadata function."""
    md_group = metadata.create_json_metadata('tests/fixtures/metadata_delim.csv',
                                             'delimited')
    assert md_group[0]['metadata'] == json_metadata_delim[0]['metadata']
    assert md_group[1]['metadata'] == json_metadata_delim[1]['metadata']


def test_create_metadata_rec_delim(json_metadata_delim):
    """Test create_metadata_rec function."""
    mapping_dict = {'file_identifier': ['file_identifier'],
                    'dc.title': ['title', 'en_US'],
                    'dc.relation.isversionof': ['uri'],
                    'dc.contributor.author': ['authors', None, '|']}
    with open('tests/fixtures/metadata_delim.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        metadata_rec_1 = metadata.create_metadata_rec_delim(mapping_dict,
                                                            next(reader), [])
        assert metadata_rec_1 == json_metadata_delim[0]['metadata']
        metadata_rec_2 = metadata.create_metadata_rec_delim(mapping_dict,
                                                            next(reader), [])
        assert metadata_rec_2 == json_metadata_delim[1]['metadata']


def test_create_metadata_rec_num_col(json_metadata_num_col):
    """Test create_metadata_rec_num_col function."""
    with open('tests/fixtures/metadata_num_col.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        metadata_rec = metadata.create_metadata_rec_num_col(next(reader), [])
        assert metadata_rec == json_metadata_num_col[0]['metadata']


def test_metadata_elems_from_row():
    """Test metadata_elems_from_row function."""
    row = {'title': 'Test title'}
    metadata_elem = metadata.metadata_elems_from_row(row, 'dc.title', 'title',
                                                     'en_US')
    assert metadata_elem[0]['key'] == 'dc.title'
    assert metadata_elem[0]['value'] == 'Test title'
    assert metadata_elem[0]['language'] == 'en_US'
    metadata_elem = metadata.metadata_elems_from_row(row, 'dc.title', 'title')
    assert metadata_elem[0]['key'] == 'dc.title'
    assert metadata_elem[0]['value'] == 'Test title'
    assert 'language' not in metadata_elem[0]
    row = {'title': ''}
    metadata_elem = metadata.metadata_elems_from_row(row, 'dc.title', 'title')
    assert metadata_elem == []
    row = {'title': 'Test title 1|Test title 2'}
    metadata_elem = metadata.metadata_elems_from_row(row, 'dc.title', 'title',
                                                     'en_US', '|')
    assert metadata_elem[0]['key'] == 'dc.title'
    assert metadata_elem[0]['value'] == 'Test title 1'
    assert metadata_elem[0]['language'] == 'en_US'
    assert metadata_elem[1]['key'] == 'dc.title'
    assert metadata_elem[1]['value'] == 'Test title 2'
    assert metadata_elem[1]['language'] == 'en_US'
