from dsaps.cli import main


def test_reconcile(runner, input_dir, output_dir):
    """Test reconcile command."""
    result = runner.invoke(main,
                           ['--url', 'mock://example.com/',
                            '--email', 'test@test.mock',
                            '--password', '1234',
                            'reconcile',
                            '--metadata_csv',
                            f'{input_dir}/metadata.csv',
                            '--file_path', 'files',
                            '--file_type', 'pdf',
                            '--output_path', f'{output_dir}'
                            ])
    assert result.exit_code == 0
