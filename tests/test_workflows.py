import csv

from dsaps import workflows


def test_create_file_dict_and_id_list(runner, sample_files_dir):
    """Test create_file_dict_and_id_list function."""
    file_path = sample_files_dir
    file_dict, file_ids = workflows.create_file_dict_and_list(sample_files_dir,
                                                              'pdf')
    assert file_dict['test_02'] == f'{file_path}/test_02.pdf'
    assert file_dict['test_01'] == f'{file_path}/test_01.pdf'
    assert file_dict['best_01'] == f'{file_path}/best_01.pdf'
    for id in ['test_02', 'test_01', 'best_01']:
        assert id in file_ids


def test_create_metadata_id_list(runner, sample_files_dir):
    """Test create_metadata_id_list function."""
    metadata_path = f'{sample_files_dir}/metadata.csv'
    metadata_ids = workflows.create_metadata_id_list(metadata_path)
    assert 'test' in metadata_ids


def test_match_files_to_metadata():
    """Test match_files_to_metadata function."""
    file_dict = {'test_01': 'files/test_01.pdf'}
    file_ids = ['test_01']
    metadata_ids = ['test', 'tast']
    file_matches = workflows.match_files_to_metadata(file_dict, file_ids,
                                                     metadata_ids)
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


def test_reconcile_files_and_metadata(runner, sample_files_dir):
    """Test reconcile function."""
    with runner.isolated_filesystem():
        metadata_path = f'{sample_files_dir}/metadata.csv'
        workflows.reconcile_files_and_metadata(metadata_path, sample_files_dir,
                                               'pdf')
        with open('updated-metadata.csv') as csvfile2:
            reader = csv.DictReader(csvfile2)
            for row in reader:
                assert row['uri'] == '/repo/0/ao/123'
                assert row['title'] == 'Test Item'
                assert row['file_identifier'] == 'test'
        with open('no_metadata.csv') as csvfile3:
            reader = csv.DictReader(csvfile3)
            for row in reader:
                assert row['id'] == 'best_01'
        with open('no_files.csv') as csvfile4:
            reader = csv.DictReader(csvfile4)
            for row in reader:
                assert row['id'] == 'tast'


def test_update_metadata_csv(runner, sample_files_dir):
    """Test update_metadata_csv function."""
    with runner.isolated_filesystem():
        metadata_matches = ['test']
        workflows.update_metadata_csv(f'{sample_files_dir}/metadata.csv',
                                      metadata_matches)
        with open('updated-metadata.csv') as csvfile2:
            reader = csv.DictReader(csvfile2)
            for row in reader:
                assert row['uri'] == '/repo/0/ao/123'
                assert row['title'] == 'Test Item'
                assert row['file_identifier'] == 'test'
