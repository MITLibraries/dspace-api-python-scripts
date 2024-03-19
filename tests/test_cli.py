from moto import mock_aws

from dsaps.cli import main


@mock_aws
def test_additems(runner, mocked_s3, caplog):
    """Test adding items to a collection."""
    caplog.set_level("DEBUG")
    result = runner.invoke(
        main,
        [
            "--source-config",
            "tests/fixtures/config/source_simple.json",
            "--url",
            "mock://example.com/",
            "--email",
            "test@test.mock",
            "--password",
            "1234",
            "additems",
            "--metadata-csv",
            "tests/fixtures/aspace_metadata_delimited.csv",
            "--field-map",
            "config/aspace_mapping.json",
            "--content-directory",
            "s3://test-bucket",
            "--file-type",
            "pdf",
            "--collection-handle",
            "333.3333",
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        main,
        [
            "--source-config",
            "tests/fixtures/config/source_simple.json",
            "--url",
            "mock://example.com/",
            "--email",
            "test@test.mock",
            "--password",
            "1234",
            "newcollection",
            "--community-handle",
            "111.1111",
            "--collection-name",
            "Test Collection",
            "additems",
            "--metadata-csv",
            "tests/fixtures/aspace_metadata_delimited.csv",
            "--field-map",
            "config/aspace_mapping.json",
            "--content-directory",
            "s3://test-bucket",
            "--file-type",
            "pdf",
        ],
    )
    assert result.exit_code == 0


def test_newcollection(runner):
    """Test newcoll command."""
    result = runner.invoke(
        main,
        [
            "--source-config",
            "tests/fixtures/config/source_simple.json",
            "--url",
            "mock://example.com/",
            "--email",
            "test@test.mock",
            "--password",
            "1234",
            "newcollection",
            "--community-handle",
            "111.1111",
            "--collection-name",
            "Test Collection",
        ],
    )
    assert result.exit_code == 0


@mock_aws
def test_reconcile(runner, mocked_s3, output_dir):
    """Test reconcile command."""
    result = runner.invoke(
        main,
        [
            "--source-config",
            "tests/fixtures/config/source_simple.json",
            "--url",
            "mock://example.com/",
            "--email",
            "test@test.mock",
            "--password",
            "1234",
            "reconcile",
            "--metadata-csv",
            "tests/fixtures/aspace_metadata_delimited.csv",
            "--output-directory",
            output_dir,
            "--content-directory",
            "s3://test-bucket",
            "--file-type",
            "pdf",
        ],
    )
    assert result.exit_code == 0
