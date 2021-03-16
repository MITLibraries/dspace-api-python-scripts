import csv
import os
import requests_mock

from dsaps.cli import main


def test_reconcile(runner):
    """Test reconcile command."""
    with requests_mock.Mocker() as m:
        with runner.isolated_filesystem():
            os.mkdir('files')
            with open('metadata.csv', 'w') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['uri'] + ['title'] + ['file_identifier'])
                writer.writerow(['/repo/0/ao/123'] + ['Test Item'] + ['test'])
            cookies = {'JSESSIONID': '11111111'}
            user_json = {'fullname': 'User Name'}
            m.post('mock://example.com/login', cookies=cookies)
            m.get('mock://example.com/status', json=user_json)
            result = runner.invoke(main,
                                   ['--url', 'mock://example.com/',
                                    '--email', 'test@test.mock',
                                    '--password', '1234',
                                    'reconcile',
                                    '--metadata_csv', 'metadata.csv',
                                    '--file_path', 'files',
                                    '--file_type', 'pdf'
                                    ])
    assert result.exit_code == 0
