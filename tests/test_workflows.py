import csv

from dsaps import workflows


def test_create_file_dict(input_dir):
    """Test create_file_dict function."""
    file_dict = workflows.create_file_dict(input_dir, 'pdf')
    assert file_dict['test_02'] == f'{input_dir}more_files/test_02.pdf'
    assert file_dict['test_01'] == f'{input_dir}test_01.pdf'
    assert file_dict['best_01'] == f'{input_dir}best_01.pdf'


def test_create_metadata_id_list(input_dir):
    """Test create_metadata_id_list function."""
    metadata_path = f'{input_dir}metadata.csv'
    metadata_ids = workflows.create_metadata_id_list(metadata_path)
    assert 'test' in metadata_ids
    assert 'tast' in metadata_ids


def test_match_files_to_metadata():
    """Test match_files_to_metadata function."""
    file_dict = {'test_01': 'files/test_01.pdf'}
    metadata_ids = ['test', 'tast']
    file_matches = workflows.match_files_to_metadata(file_dict, metadata_ids)
    assert len(file_matches) == 1
    assert 'test_01' in file_matches


def test_match_metadata_to_files():
    """Test match_metadata_to_files function."""
    file_dict = {'test_01': 'files/test_01.pdf',
                 'tast_01': 'files/tast_01.pdf'}
    metadata_ids = ['test']
    file_matches = workflows.match_metadata_to_files(file_dict, metadata_ids)
    assert len(file_matches) == 1
    assert 'test' in file_matches


def test_populate_new_coll(client, json_metadata, input_dir):
    """Test populate_new_coll function."""
    coll_name = 'Collection Name'
    items = workflows.populate_new_coll(client, '111.1111', coll_name,
                                        json_metadata, input_dir, 'pdf',
                                        'local', {}, 'True')
    for item in items:
        assert item == 'e5f6'


def test_reconcile_files_and_metadata(input_dir, output_dir):
    """Test reconcile function."""
    metadata_path = f'{input_dir}metadata.csv'
    workflows.reconcile_files_and_metadata(metadata_path, output_dir,
                                           input_dir, 'pdf')
    with open(f'{output_dir}updated-metadata.csv') as csvfile2:
        reader = csv.DictReader(csvfile2)
        for row in reader:
            assert row['uri'] == '/repo/0/ao/123'
            assert row['title'] == 'Test Item'
            assert row['file_identifier'] == 'test'
    with open(f'{output_dir}no_metadata.csv') as csvfile3:
        reader = csv.DictReader(csvfile3)
        for row in reader:
            assert row['id'] == 'best_01'
    with open(f'{output_dir}no_files.csv') as csvfile4:
        reader = csv.DictReader(csvfile4)
        for row in reader:
            assert row['id'] == 'tast'


def test_update_metadata_csv(input_dir, output_dir):
    """Test update_metadata_csv function."""
    metadata_matches = ['test']
    workflows.update_metadata_csv(f'{input_dir}metadata.csv', output_dir,
                                  metadata_matches)
    with open(f'{output_dir}updated-metadata.csv') as csvfile2:
        reader = csv.DictReader(csvfile2)
        for row in reader:
            assert row['uri'] == '/repo/0/ao/123'
            assert row['title'] == 'Test Item'
            assert row['file_identifier'] == 'test'
