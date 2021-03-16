import csv

from click.testing import CliRunner
import pytest
import requests_mock

from dsaps import models


@pytest.fixture(autouse=True)
def client():
    client = models.Client('mock://example.com/')
    client.header = {}
    client.cookies = {}
    client.user_full_name = ''
    return client


@pytest.fixture(autouse=True)
def ds_mock():
    with requests_mock.Mocker() as m:
        cookies = {'JSESSIONID': '11111111'}
        m.post('mock://example.com/login', cookies=cookies)
        user_json = {'fullname': 'User Name'}
        m.get('mock://example.com/status', json=user_json)
        rec_json = {'metadata': {'title': 'Sample title'}, 'type': 'item'}
        m.get('mock://example.com/items/123?expand=all', json=rec_json)
        results_json1 = {'items': [{'link': '1234'}]}
        results_json2 = {'items': []}
        m.get('mock://example.com/filtered-items?', [{'json': results_json1},
              {'json': results_json2}])
        rec_json = {'uuid': '123'}
        m.get('mock://example.com/handle/111.1111', json=rec_json)
        comm_json = {'uuid': 'a1b2'}
        m.get('mock://example.com/handle/1234', json=comm_json)
        coll_json = {'uuid': '5678'}
        m.post('mock://example.com/communities/a1b2/collections',
               json=coll_json)
        item_json = {'uuid': 'a1b2', 'handle': '1111.1/1111'}
        m.post('mock://example.com/collections/789/items', json=item_json)
        b_json_1 = {'uuid': 'c3d4'}
        url_1 = 'mock://example.com/items/a1b2/bitstreams?name=test_01.pdf'
        m.post(url_1, json=b_json_1)
        b_json_2 = {'uuid': 'e5f6'}
        url_2 = 'mock://example.com/items/a1b2/bitstreams?name=test_02.pdf'
        m.post(url_2, json=b_json_2)
        yield m


@pytest.fixture(autouse=True)
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def sample_files_dir(tmp_path):
    sample_files_dir = tmp_path / 'files'
    sample_files_dir.mkdir()
    with open(f'{sample_files_dir}/test_01.pdf', 'w'):
        pass
    with open(f'{sample_files_dir}/test_02.pdf', 'w'):
        pass
    with open(f'{sample_files_dir}/best_01.pdf', 'w'):
        pass
    with open(f'{sample_files_dir}/metadata.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['uri'] + ['title'] + ['file_identifier'])
        writer.writerow(['/repo/0/ao/123'] + ['Test Item'] + ['test'])
        writer.writerow(['/repo/0/ao/456'] + ['Tast Item'] + ['tast'])
    return str(sample_files_dir)
