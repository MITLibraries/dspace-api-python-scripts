from dsaps.cli import main


def test_additems(runner, input_dir):
    """Test adding items to a collection."""
    result = runner.invoke(main,
                           ['--url', 'mock://example.com/',
                            '--email', 'test@test.mock',
                            '--password', '1234',
                            'additems',
                            '--collection-handle', '333.3333',
                            '--metadata-csv', 'tests/files/metadata_delim.csv',
                            '--field-map', 'tests/files/aspace_mapping.json',
                            '--directory', input_dir,
                            '--file-type', 'pdf'])
    assert result.exit_code == 0


# def test_newcoll(runner, input_dir):
#     """Test newcoll command."""
#     result = runner.invoke(main,
#                            ['--url', 'mock://example.com/',
#                             '--email', 'test@test.mock',
#                             '--password', '1234',
#                             'newcoll',
#                             '--comm_handle', '111.1111',
#                             '--coll_name', 'Test Collection',
#                             '--metadata_csv', 'tests/files/metadata_delim.csv',
#                             '--file_path', input_dir,
#                             '--file_type', 'pdf',
#                             '--ingest_type', 'local',
#                             '--ingest_report', 'False',
#                             '--multiple_terms', 'delimited'
#                             ])
#     assert result.exit_code == 0


# def test_reconcile(runner, input_dir, output_dir):
#     """Test reconcile command."""
#     result = runner.invoke(main,
#                            ['--url', 'mock://example.com/',
#                             '--email', 'test@test.mock',
#                             '--password', '1234',
#                             'reconcile',
#                             '--metadata_csv', 'tests/files/metadata_delim.csv',
#                             '--file_path', input_dir,
#                             '--file_type', 'pdf',
#                             '--output_path', output_dir
#                             ])
#     assert result.exit_code == 0
