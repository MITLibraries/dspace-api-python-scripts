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
        url_1 = 'mock://example.com/items/a1b2/bitstreams?name=123_1.pdf'
        m.post(url_1, json=b_json_1)
        b_json_2 = {'uuid': 'e5f6'}
        url_2 = 'mock://example.com/items/a1b2/bitstreams?name=123_2.pdf'
        m.post(url_2, json=b_json_2)
        yield m


@pytest.fixture(autouse=True)
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def sample_content_1(tmp_path):
    content = 'test'
    dir = tmp_path / 'sub'
    dir.mkdir()
    sample_content = dir / '123_1.pdf'
    sample_content.write_text(content)
    return sample_content


@pytest.fixture(autouse=True)
def sample_content_2(tmp_path):
    content = 'test'
    dir = tmp_path / 'sub'
    sample_content = dir / '123_2.pdf'
    sample_content.write_text(content)
    return sample_content
