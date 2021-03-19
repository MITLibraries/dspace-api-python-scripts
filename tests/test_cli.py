from dsaps.cli import main


def test_newcoll(runner, input_dir):
    """Test newcoll command."""
    result = runner.invoke(main,
                           ['--url', 'mock://example.com/',
                            '--email', 'test@test.mock',
                            '--password', '1234',
                            'newcoll',
                            '--comm_handle', '111.1111',
                            '--coll_name', 'Test Collection',
                            '--metadata_csv', f'{input_dir}metadata.csv',
                            '--file_path', input_dir,
                            '--file_type', 'pdf',
                            '--ingest_type', 'local',
                            '--ingest_report', 'True',
                            '--multiple_terms', 'delimited'
                            ])
    assert result.exit_code == 0


def test_reconcile(runner, input_dir, output_dir):
    """Test reconcile command."""
    result = runner.invoke(main,
                           ['--url', 'mock://example.com/',
                            '--email', 'test@test.mock',
                            '--password', '1234',
                            'reconcile',
                            '--metadata_csv', f'{input_dir}metadata.csv',
                            '--file_path', input_dir,
                            '--file_type', 'pdf',
                            '--output_path', output_dir
                            ])
    assert result.exit_code == 0
