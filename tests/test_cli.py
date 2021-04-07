from dsaps.cli import main


def test_additems(runner, input_dir):
    """Test adding items to a collection."""
    result = runner.invoke(main,
                           ['--url', 'mock://example.com/',
                            '--email', 'test@test.mock',
                            '--password', '1234',
                            'existingcollection',
                            '--collection-handle', '333.3333',
                            'additems',
                            '--metadata-csv', 'tests/files/metadata_delim.csv',
                            '--field-map', 'config/standard_mapping.json',
                            '--directory', input_dir,
                            '--file-type', 'pdf'])
    assert result.exit_code == 0
    result = runner.invoke(main,
                           ['--url', 'mock://example.com/',
                            '--email', 'test@test.mock',
                            '--password', '1234',
                            'newcollection',
                            '--community-handle', '111.1111',
                            '--collection-name', 'Test Collection',
                            'additems',
                            '--metadata-csv', 'tests/files/metadata_delim.csv',
                            '--field-map', 'config/standard_mapping.json',
                            '--directory', input_dir,
                            '--file-type', 'pdf'])
    assert result.exit_code == 0


def test_existingcollection(runner, input_dir):
    """Test adding items to a collection."""
    result = runner.invoke(main,
                           ['--url', 'mock://example.com/',
                            '--email', 'test@test.mock',
                            '--password', '1234',
                            'existingcollection',
                            '--collection-handle', '333.3333'])
    assert result.exit_code == 0


def test_newcollection(runner, input_dir):
    """Test newcoll command."""
    result = runner.invoke(main,
                           ['--url', 'mock://example.com/',
                            '--email', 'test@test.mock',
                            '--password', '1234',
                            'newcollection',
                            '--community-handle', '111.1111',
                            '--collection-name', 'Test Collection'])
    assert result.exit_code == 0


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
