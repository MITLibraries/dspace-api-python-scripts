import csv

from dsaps import helpers
from dsaps.models import Item


def test_create_csv_from_list(output_dir):
    """Test create_csv_from_list function."""
    list_name = ["123"]
    helpers.create_csv_from_list(list_name, f"{output_dir}output")
    with open(f"{output_dir}output.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row["id"] == "123"


def test_create_file_list(mocked_s3, s3_client):
    """Test create_file_list function."""
    file_list = helpers.create_file_list("s3://test-bucket", s3_client, "pdf")
    for file_id in ["test_02.pdf", "test_01.pdf", "best_01.pdf"]:
        assert file_id in file_list


def test_create_ingest_report(runner, output_dir):
    """Test create_ingest_report function."""
    file_name = "ingest_report.csv"
    items = [Item(source_system_identifier="/repo/0/ao/123", handle="111.1111")]
    helpers.create_ingest_report(items, f"{output_dir}{file_name}")
    with open(f"{output_dir}{file_name}") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row["uri"] == "/repo/0/ao/123"
            assert row["link"] == "https://hdl.handle.net/111.1111"


def test_create_metadata_id_list():
    """Test create_metadata_id_list function."""
    metadata_path = "tests/fixtures/aspace_metadata_delimited.csv"
    metadata_ids = helpers.create_metadata_id_list(metadata_path)
    assert "test" in metadata_ids
    assert "tast" in metadata_ids


def test_match_files_to_metadata():
    """Test match_files_to_metadata function."""
    file_list = ["test_01.pdf"]
    metadata_ids = ["test", "tast"]
    file_matches = helpers.match_files_to_metadata(file_list, metadata_ids)
    assert len(file_matches) == 1
    assert "test_01.pdf" in file_matches


def test_match_metadata_to_files():
    """Test match_metadata_to_files function."""
    file_list = ["test_01.pdf", "tast_01.pdf"]
    metadata_ids = ["test"]
    file_matches = helpers.match_metadata_to_files(file_list, metadata_ids)
    assert len(file_matches) == 1
    assert "test" in file_matches


def test_update_metadata_csv(output_dir):
    """Test update_metadata_csv function."""
    metadata_matches = ["test"]
    helpers.update_metadata_csv(
        "tests/fixtures/aspace_metadata_delimited.csv", output_dir, metadata_matches
    )
    with open(f"{output_dir}updated-aspace_metadata_delimited.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row["uri"] == "/repo/0/ao/123"
            assert row["title"] == "Test Item"
            assert row["file_identifier"] == "test"
