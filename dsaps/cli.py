import csv
import datetime
import json
import logging
import os
import time

import click
import structlog

from dsaps import helpers
from dsaps.models import Client, Collection

logger = structlog.get_logger()


def validate_path(ctx, param, value):
    """Validates the formatting of the submitted path"""
    if value[-1] == "/":
        return value
    else:
        raise click.BadParameter("Include / at the end of the path.")


@click.group(chain=True)
@click.option(
    "--config-file", required=True, help="File path to source configuration JSON."
)
@click.option(
    "--url",
    envvar="DSPACE_URL",
    required=True,
    help="The url for the DSpace REST API. Defaults to env var DSPACE_URL if not set.",
)
@click.option(
    "-e",
    "--email",
    envvar="DSPACE_EMAIL",
    required=True,
    help=(
        "The email associated with the DSpace user account used for authentication. "
        "Defaults to env var DSPACE_EMAIL if not set."
    ),
)
@click.option(
    "-p",
    "--password",
    envvar="DSPACE_PASSWORD",
    required=True,
    hide_input=True,
    help=(
        "The password associated with the DSpace user account used for authentication. "
        "Defaults to env var DSPACE_PASSWORD if not set."
    ),
)
@click.pass_context
def main(ctx, config_file, url, email, password):
    ctx.obj = {}
    if os.path.isdir("logs") is False:
        os.mkdir("logs")
    dt = datetime.datetime.utcnow().isoformat(timespec="seconds")
    log_suffix = f"{dt}.log"
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        handlers=[logging.FileHandler(f"logs/log-{log_suffix}", "w")],
        level=logging.INFO,
    )
    logger.info("Application start")
    client = Client(url)
    client.authenticate(email, password)
    start_time = time.time()
    ctx.obj["config"] = helpers.load_source_config(config_file)
    ctx.obj["client"] = client
    ctx.obj["start_time"] = start_time
    ctx.obj["log_suffix"] = log_suffix


@main.command()
@click.option(
    "-m",
    "--metadata-csv",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="The filepath to a CSV file containing metadata for Dspace uploads.",
)
@click.option(
    "-f",
    "--field-map",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="The filepath to a JSON document that maps columns in the metadata CSV file to a DSpace schema.",
)
@click.option(
    "-d",
    "--content-directory",
    required=True,
    help="The name of the S3 bucket containing files for DSpace uploads.",
)
@click.option(
    "-t",
    "--file-type",
    help="The file type for DSpace uploads (i.e., the file extension, excluding the dot).",
    default="*",
)
@click.option(
    "-r",
    "--ingest-report",
    is_flag=True,
    help="Create ingest report for updating other systems.",
)
@click.option(
    "-c",
    "--collection-handle",
    help="The handle identifying a DSpace collection into which uploads are deposited.",
    default=None,
)
@click.pass_context
def additems(
    ctx,
    metadata_csv,
    field_map,
    content_directory,
    file_type,
    ingest_report,
    collection_handle,
):
    """Add items to a DSpace collection.

    The method relies on a CSV file with metadata for uploads, a JSON document that maps
    metadata to a DSpace schema, and a directory containing the files to be uploaded.
    """
    client = ctx.obj["client"]
    start_time = ctx.obj["start_time"]
    if "collection_uuid" not in ctx.obj and collection_handle is None:
        raise click.UsageError(
            "collection_handle option must be used or "
            "additems must be run after newcollection "
            "command."
        )
    elif "collection_uuid" in ctx.obj:
        collection_uuid = ctx.obj["collection_uuid"]
    else:
        collection_uuid = client.get_uuid_from_handle(collection_handle)
    with open(metadata_csv, "r") as csvfile, open(field_map, "r") as jsonfile:
        metadata = csv.DictReader(csvfile)
        mapping = json.load(jsonfile)
        collection = Collection.create_metadata_for_items_from_csv(metadata, mapping)
    for item in collection.items:
        item.bitstreams_in_directory(content_directory, client.s3_client, file_type)
    collection.uuid = collection_uuid
    for item in collection.post_items(client):
        logger.info(item.file_identifier)
    elapsed_time = datetime.timedelta(seconds=time.time() - start_time)
    logger.info(f"Total runtime : {elapsed_time}")


@main.command()
@click.option(
    "-c",
    "--community-handle",
    required=True,
    help="The handle identifying a DSpace community in which a new collection is created.",
)
@click.option(
    "-n",
    "--collection-name",
    required=True,
    help="The name assigned to the DSpace collection being created.",
)
@click.pass_context
def newcollection(ctx, community_handle, collection_name):
    """Create a new DSpace collection within a community."""
    client = ctx.obj["client"]
    collection_uuid = client.post_coll_to_comm(community_handle, collection_name)
    ctx.obj["collection_uuid"] = collection_uuid


@main.command()
@click.option(
    "-m",
    "--metadata-csv",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="The filepath to a CSV file containing metadata for Dspace uploads.",
)
@click.option(
    "-o",
    "--output-directory",
    default=f"{os.getcwd()}/",
    callback=validate_path,
    help="The filepath where output files are written.",
)
@click.option(
    "-d",
    "--content-directory",
    required=True,
    help="The name of the S3 bucket containing files for DSpace uploads.",
)
@click.pass_context
def reconcile(ctx, metadata_csv, output_directory, content_directory):
    """Match files in the content directory with entries in the metadata CSV file.

    Running this method creates the following CSV files:

        * metadata_matches.csv: File identifiers for entries in metadata CSV file with a
        corresponding file in the content directory.

        * no_files.csv: File identifiers for entries in metadata CSV file without a
        corresponding file in the content directory.

        * no_metadata.csv: File identifiers for files in the content directory without a
        corresponding entry in the metadata CSV file.

        * updated-<metadata-csv>.csv: Entries from the metadata CSV file with a
        corresponding file in the content directory.
    """
    source_settings = ctx.obj["config"]["settings"]
    client = ctx.obj["client"]
    files_dict = helpers.get_files_from_s3(
        s3_path=content_directory,
        s3_client=client.s3_client,
        bitstream_folders=source_settings.get("bitstream_folders"),
        id_regex=source_settings["id_regex"],
    )
    metadata_ids = helpers.create_metadata_id_list(metadata_csv)
    metadata_matches = helpers.match_metadata_to_files(files_dict.keys(), metadata_ids)
    file_matches = helpers.match_files_to_metadata(files_dict.keys(), metadata_ids)
    no_files = set(metadata_ids) - set(metadata_matches)
    no_metadata = set(files_dict.keys()) - set(file_matches)
    helpers.create_csv_from_list(no_metadata, f"{output_directory}no_metadata")
    helpers.create_csv_from_list(no_files, f"{output_directory}no_files")
    helpers.create_csv_from_list(metadata_matches, f"{output_directory}metadata_matches")
    helpers.update_metadata_csv(
        metadata_csv, output_directory, metadata_matches, files_dict
    )
