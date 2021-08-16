from dsaps.cli import main


def test_additems_existing_collection(runner, input_dir):
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


def test_additems_ingest_report(runner, input_dir, output_dir):
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
            "--ingest-report",
            "--output-directory",
            output_dir,
        ],
    )
    assert result.exit_code == 0


def test_additems_missing_required_options(runner, input_dir):
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
        ],
    )
    assert result.exit_code == 2
    assert (
        "collection_handle option must be used or additems must be run after"
    ) in result.output


def test_additems_new_collection(runner, input_dir):
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


def test_newcollection(client, runner, input_dir):
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


def test_reconcile_bad_output_directory(runner, input_dir, output_dir):
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
            "tests",
            "--content-directory",
            input_dir,
            "--file-type",
            "pdf",
        ],
    )
    assert result.exit_code == 2
    assert "Include / at the end of the path." in result.output
