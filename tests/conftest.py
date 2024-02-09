import csv
import json

import boto3
import pytest
import requests_mock
from click.testing import CliRunner
from moto import mock_aws

from dsaps import models


# Env fixtures
@pytest.fixture(autouse=True)
def _test_environment(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")


@pytest.fixture()
def mocked_s3():
    with mock_aws():
        s3_instance = boto3.client("s3", region_name="us-east-1")
        s3_instance.create_bucket(Bucket="test-bucket")
        s3_instance.put_object(
            Body="",
            Bucket="test-bucket",
            Key="test_01.pdf",
        )
        s3_instance.put_object(
            Body="",
            Bucket="test-bucket",
            Key="test_02.pdf",
        )
        s3_instance.put_object(
            Body="",
            Bucket="test-bucket",
            Key="best_01.pdf",
        )
        s3_instance.put_object(
            Body="",
            Bucket="test-bucket",
            Key="test_01.jpg",
        )
        yield s3_instance


@pytest.fixture()
def s3_client():
    return boto3.client("s3", region_name="us-east-1")


@pytest.fixture()
def client():
    client = models.Client("mock://example.com/")
    client.header = {}
    client.cookies = {}
    client.user_full_name = ""
    return client


@pytest.fixture()
def aspace_delimited_csv():
    with open("tests/fixtures/aspace_metadata_delimited.csv") as f:
        reader = csv.DictReader(f)
        yield reader


@pytest.fixture()
def aspace_mapping():
    with open("config/aspace_mapping.json") as f:
        mapping = json.load(f)
        yield mapping


@pytest.fixture()
def output_dir(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return str(f"{output_dir}/")


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def web_mock():
    with requests_mock.Mocker() as m:
        cookies = {"JSESSIONID": "11111111"}
        m.post("mock://example.com/login", cookies=cookies)
        user_json = {"fullname": "User Name"}
        m.get("mock://example.com/status", json=user_json)
        rec_json = {"metadata": {"title": "Sample title"}, "type": "item"}
        m.get("mock://example.com/items/123?expand=all", json=rec_json)
        results_json1 = {"items": [{"link": "1234"}]}
        results_json2 = {"items": []}
        m.get(
            "mock://example.com/filtered-items?",
            [{"json": results_json1}, {"json": results_json2}],
        )
        rec_json = {"uuid": "a1b2"}
        m.get("mock://example.com/handle/111.1111", json=rec_json)
        coll_json = {"uuid": "c3d4"}
        m.post("mock://example.com/communities/a1b2/collections", json=coll_json)
        item_json = {"uuid": "e5f6", "handle": "222.2222"}
        m.post("mock://example.com/collections/c3d4/items", json=item_json)
        b_json_1 = {"uuid": "g7h8"}
        url_1 = "mock://example.com/items/e5f6/bitstreams?name=test_01.pdf"
        m.post(url_1, json=b_json_1)
        b_json_2 = {"uuid": "i9j0"}
        url_2 = "mock://example.com/items/e5f6/bitstreams?name=test_02.pdf"
        m.post(url_2, json=b_json_2)
        m.get("mock://remoteserver.com/files/test_01.pdf", content=b"Sample")
        coll_json = {"uuid": "k1l2"}
        m.get("mock://example.com/handle/333.3333", json=coll_json)
        item_json_2 = {"uuid": "e5f6", "handle": "222.2222"}
        m.post("mock://example.com/collections/k1l2/items", json=item_json_2)
        yield m
