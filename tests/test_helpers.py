import csv
import requests_mock

from dsaps import helpers


def test_build_file_dict_remote():
    """Test build_file_dict_remote function."""
    content = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>'
    content += '<head><title>Index of /pdf</title></head><body><h1>Index of /'
    content += 'pdf</h1><table><tr><th>Name</th><th>Last modified</th><th>'
    content += 'Size</th></tr><tr><td><a href="999.pdf">999.pdf</a></td><td>'
    content += '2001-02-16 11:59 </td><td>107K</td></tr></table></body></html>'
    with requests_mock.Mocker() as m:
        directory_url = 'mock://test.com/pdfs/'
        file_type = 'pdf'
        file_dict = {}
        m.get(directory_url, text=content)
        file_list = helpers.build_file_dict_remote(directory_url, file_type,
                                                   file_dict)
        assert '999' in file_list


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


def test_create_ingest_report(runner):
    """Test create_ingest_report function."""
    with runner.isolated_filesystem():
        file_name = 'ingest_report'
        ingest_data = {'/repo/0/ao/123': '111.1111'}
        helpers.create_ingest_report(ingest_data, file_name)
        with open(f'{file_name}.csv') as csvfile:
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


def test_select_bitstreams(input_dir):
    """Test select_bitstreams function."""
    file_dict_remote = {'test_01': 'mock://remoteserver.com/files/test_01.pdf',
                        'tast_01': 'mock://remoteserver.com/files/tast_01.pdf'}
    sel_bitstreams = helpers.select_bitstreams('remote', file_dict_remote,
                                               'test')
    assert sel_bitstreams[0] == b'Sample'
    file_dict_local = {'test_01': f'{input_dir}test_01.pdf',
                       'tast_01': f'{input_dir}tast_01.pdf'}
    sel_bitstreams = helpers.select_bitstreams('local', file_dict_local,
                                               'test')
    assert sel_bitstreams[0].name == open(f'{input_dir}test_01.pdf', 'rb').name


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
