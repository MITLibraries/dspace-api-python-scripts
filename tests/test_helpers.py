import csv

from dsaps import helpers
from dsaps.models import Item

# from dsaps.helpers import files_from_location
#
#
# def test_file_list_from_location_with_file_type(input_dir):
#     files = files_from_location(input_dir, 'pdf')
#     assert 3 == len(files)
#     assert {'name': 'test_01', 'path': f'{input_dir}test_01.pdf'} in files
#     assert {'name': 'test_02',
#             'path': f'{input_dir}more_files/test_02.pdf'} in files
#
#
# def test_file_list_from_location_without_file_type(input_dir):
#     files = files_from_location(input_dir)
#     assert 4 == len(files)
#     assert {'name': 'test_01', 'path': f'{input_dir}test_01.pdf'} in files
#     assert {'name': 'test_02',
#             'path': f'{input_dir}more_files/test_02.pdf'} in files
#     assert {'name': 'test_01', 'path': f'{input_dir}test_01.jpg'} in files
#


def test_create_csv_from_list(output_dir):
    """Test create_csv_from_list function."""
    list_name = ['123']
    helpers.create_csv_from_list(list_name, f'{output_dir}output')
    with open(f'{output_dir}output.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row['id'] == '123'


def test_create_file_dict(input_dir):
    """Test create_file_dict function."""
    file_dict = helpers.create_file_dict(input_dir, 'pdf')
    assert file_dict['test_02'] == f'{input_dir}more_files/test_02.pdf'
    assert file_dict['test_01'] == f'{input_dir}test_01.pdf'
    assert file_dict['best_01'] == f'{input_dir}best_01.pdf'


def test_create_ingest_report(runner, output_dir):
    """Test create_ingest_report function."""
    file_name = 'ingest_report.csv'
    items = [
        Item(source_system_identifier='/repo/0/ao/123',
             handle='111.1111')
    ]
    helpers.create_ingest_report(items, f'{output_dir}{file_name}')
    with open(f'{output_dir}{file_name}') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row['uri'] == '/repo/0/ao/123'
            assert row['link'] == 'https://hdl.handle.net/111.1111'


def test_create_metadata_id_list(input_dir):
    """Test create_metadata_id_list function."""
    metadata_path = 'tests/files/metadata_delim.csv'
    metadata_ids = helpers.create_metadata_id_list(metadata_path)
    assert 'test' in metadata_ids
    assert 'tast' in metadata_ids


def test_match_files_to_metadata():
    """Test match_files_to_metadata function."""
    file_dict = {'test_01': 'files/test_01.pdf'}
    metadata_ids = ['test', 'tast']
    file_matches = helpers.match_files_to_metadata(file_dict, metadata_ids)
    assert len(file_matches) == 1
    assert 'test_01' in file_matches


def test_match_metadata_to_files():
    """Test match_metadata_to_files function."""
    file_dict = {'test_01': 'files/test_01.pdf',
                 'tast_01': 'files/tast_01.pdf'}
    metadata_ids = ['test']
    file_matches = helpers.match_metadata_to_files(file_dict, metadata_ids)
    assert len(file_matches) == 1
    assert 'test' in file_matches


def test_update_metadata_csv(input_dir, output_dir):
    """Test update_metadata_csv function."""
    metadata_matches = ['test']
    helpers.update_metadata_csv('tests/files/metadata_delim.csv', output_dir,
                                metadata_matches)
    with open(f'{output_dir}updated-metadata_delim.csv') as csvfile2:
        reader = csv.DictReader(csvfile2)
        for row in reader:
            assert row['uri'] == '/repo/0/ao/123'
            assert row['title'] == 'Test Item'
            assert row['file_identifier'] == 'test'
