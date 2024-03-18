import csv
import os


def create_csv_from_list(list_name, output):
    """Create CSV file from list."""
    with open(f"{output}.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id"])
        for item in list_name:
            writer.writerow([item])


def create_file_list(file_path, s3_client, file_type):
    """Create a list of file names."""
    files = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=file_path.removeprefix("s3://")):
        files.extend(
            [
                file["Key"]
                for file in page["Contents"]
                if file["Key"].endswith(f".{file_type}")
            ]
        )
    return files


def create_ingest_report(items, file_name):
    """Create ingest report that matches external systems' identifiers with newly
    created DSpace handles."""
    with open(f"{file_name}", "w") as writecsv:
        writer = csv.writer(writecsv)
        writer.writerow(["uri", "link"])
        for item in items:
            writer.writerow(
                [item.source_system_identifier]
                + [f"https://hdl.handle.net/{item.handle}"]
            )


def create_metadata_id_list(metadata_csv):
    """Create list of IDs from a metadata CSV."""
    metadata_ids = []
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        metadata_ids = [
            row["file_identifier"] for row in reader if row["file_identifier"] != ""
        ]
    return metadata_ids


def filter_files_by_prefix(file_paths, prefixes):
    """Filter file paths to a subset including specified prefixes.

    A prefix represents a subfolder in the filepath, separated by
    a forward slash ("/").

    Args:
        file_paths (list[str]): List of file paths.
        prefixes (str | list): List of prefixes to look for in a given file path.

    Returns:
        list[str]: A subset of file paths that include the specified prefixes.
    """
    filtered_file_paths = []
    if isinstance(prefixes, str):
        prefixes = [prefixes]
    else:
        prefixes = prefixes

    for file in file_paths:
        file_prefix = file.split("/")
        if set(prefixes).intersection(set(file_prefix)):
            filtered_file_paths.append(file)
    return filtered_file_paths


def match_files_to_metadata(file_list, metadata_ids):
    """Create list of files matched to metadata records."""
    file_matches = [
        file_id
        for metadata_id in metadata_ids
        for file_id in file_list
        if file_id.startswith(metadata_id)
    ]
    return file_matches


def match_metadata_to_files(file_list, metadata_ids):
    """Create list of metadata records matched to files."""
    metadata_matches = [
        metadata_id
        for f in file_list
        for metadata_id in metadata_ids
        if f.startswith(metadata_id)
    ]
    return metadata_matches


def update_metadata_csv(metadata_csv, output_directory, metadata_matches):
    """Create an updated CSV of only metadata records that have matching files."""
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        upd_md_file_name = f"updated-{os.path.basename(metadata_csv)}"
        with open(f"{output_directory}{upd_md_file_name}", "w") as updated_csv:
            writer = csv.DictWriter(updated_csv, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                if row["file_identifier"] in metadata_matches:
                    writer.writerow(row)
