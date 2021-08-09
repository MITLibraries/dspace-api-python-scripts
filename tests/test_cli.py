from dsaps.cli import main


def test_additems(runner, input_dir):
    """Test adding items to a collection."""
    result = runner.invoke(
        main,
        [
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
            input_dir,
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
            input_dir,
            "--file-type",
            "pdf",
        ],
    )
    assert result.exit_code == 0


def test_newcollection(runner, input_dir):
    """Test newcoll command."""
    result = runner.invoke(
        main,
        [
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


def test_reconcile(runner, input_dir, output_dir):
    """Test reconcile command."""
    result = runner.invoke(
        main,
        [
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
            input_dir,
            "--file-type",
            "pdf",
        ],
    )
    assert result.exit_code == 0
