import operator
from functools import partial
from typing import Optional

import attr
import boto3
import requests
import smart_open
import structlog

from attrs import field

from dsaps.helpers import filter_files_by_prefix

logger = structlog.get_logger()
op = operator.attrgetter("name")


class Client:
    def __init__(self, url):
        header = {"content-type": "application/json", "accept": "application/json"}
        self.url = url.rstrip("/")
        self.cookies = None
        self.header = header
        logger.info("Initializing client")

    def authenticate(self, email, password):
        """Authenticate user to DSpace API."""
        header = self.header
        data = {"email": email, "password": password}
        session = requests.post(
            f"{self.url}/login", headers=header, params=data, timeout=30
        ).cookies["JSESSIONID"]
        cookies = {"JSESSIONID": session}
        status = requests.get(
            f"{self.url}/status", headers=header, cookies=cookies, timeout=30
        ).json()
        self.user_full_name = status["fullname"]
        self.cookies = cookies
        self.header = header
        logger.info(f"Authenticated to {self.url} as " f"{self.user_full_name}")

    def filtered_item_search(self, key, string, query_type, selected_collections=""):
        """Perform a search against the filtered items endpoint."""
        offset = 0
        items = ""
        item_links = []
        while items != []:
            endpoint = f"{self.url}/filtered-items?"
            params = {
                "query_field[]": key,
                "query_op[]": query_type,
                "query_val[]": string,
                "&collSel[]": selected_collections,
                "limit": 200,
                "offset": offset,
            }
            logger.info(params)
            response = requests.get(
                endpoint,
                headers=self.header,
                params=params,
                cookies=self.cookies,
                timeout=30,
            )
            logger.info(f"Response url: {response.url}")
            response = response.json()
            items = response["items"]
            for item in items:
                item_links.append(item["link"])
            offset = offset + 200
        return item_links

    def get_uuid_from_handle(self, handle):
        """Get UUID for an object based on its handle."""
        hdl_endpoint = f"{self.url}/handle/{handle}"
        rec_obj = requests.get(
            hdl_endpoint, headers=self.header, cookies=self.cookies, timeout=30
        ).json()
        return rec_obj["uuid"]

    def get_record(self, uuid, record_type):
        """Get an individual record of a specified type."""
        url = f"{self.url}/{record_type}/{uuid}?expand=all"
        record = requests.get(
            url, headers=self.header, cookies=self.cookies, timeout=30
        ).json()
        if record_type == "items":
            rec_obj = self._populate_class_instance(Item, record)
        elif record_type == "communities":
            rec_obj = self._populate_class_instance(Community, record)
        elif record_type == "collections":
            rec_obj = self._populate_class_instance(Collection, record)
        else:
            logger.info("Invalid record type.")
            exit()
        return rec_obj

    def post_bitstream(self, item_uuid, bitstream):
        """Post a bitstream to a specified item and return the bitstream
        ID."""
        endpoint = f"{self.url}/items/{item_uuid}" f"/bitstreams?name={bitstream.name}"
        header_upload = {"accept": "application/json"}
        with smart_open.open(bitstream.file_path, "rb") as data:
            post_response = requests.post(
                endpoint,
                headers=header_upload,
                cookies=self.cookies,
                data=data,
                timeout=30,
            )
            logger.info(f"Bitstream POST status: {post_response}")
            response = post_response.json()
            logger.info(f"Bitstream POST response: {response}")
            bitstream_uuid = response["uuid"]
            return bitstream_uuid

    def post_coll_to_comm(self, comm_handle, coll_name):
        """Post a collection to a specified community."""
        hdl_endpoint = f"{self.url}/handle/{comm_handle}"
        community = requests.get(
            hdl_endpoint, headers=self.header, cookies=self.cookies, timeout=30
        ).json()
        comm_uuid = community["uuid"]
        uuid_endpoint = f"{self.url}/communities/{comm_uuid}/collections"
        coll_uuid = requests.post(
            uuid_endpoint,
            headers=self.header,
            cookies=self.cookies,
            json={"name": coll_name},
            timeout=30,
        ).json()
        coll_uuid = coll_uuid["uuid"]
        logger.info(f"Collection posted: {coll_uuid}")
        return coll_uuid

    def post_item_to_collection(self, collection_uuid, item):
        """Post item to a specified collection and return the item ID."""
        endpoint = f"{self.url}/collections/{collection_uuid}/items"
        logger.info(endpoint)
        post_resp = requests.post(
            endpoint,
            headers=self.header,
            cookies=self.cookies,
            json={"metadata": attr.asdict(item)["metadata"]},
            timeout=30,
        )
        logger.info(f"Item POST status: {post_resp}")
        post_response = post_resp.json()
        logger.info(f"Item POST response: {post_response}")
        item_uuid = post_response["uuid"]
        item_handle = post_response["handle"]
        return item_uuid, item_handle

    def _populate_class_instance(self, class_type, rec_obj):
        """Populate class instance with data from record."""
        fields = [op(field) for field in attr.fields(class_type)]
        kwargs = {k: v for k, v in rec_obj.items() if k in fields}
        kwargs["objtype"] = rec_obj["type"]
        if class_type == Community:
            collections = self._build_uuid_list(rec_obj, kwargs, "collections")
            rec_obj["collections"] = collections
        elif class_type == Collection:
            items = self._build_uuid_list(rec_obj, "items")
            rec_obj["items"] = items
        rec_obj = class_type(**kwargs)
        return rec_obj

    def _build_uuid_list(self, rec_obj, children):
        """Build list of the uuids of the object's children."""
        child_list = []
        for child in rec_obj[children]:
            child_list.append(child["uuid"])
        return child_list


class S3Client:
    @classmethod
    def get_client(cls):
        return boto3.client("s3")

    @classmethod
    def list_objects(cls, bucket: str, prefix: str) -> list:
        client = cls.get_client()
        s3_objects = []
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(
            Bucket=bucket.removeprefix("s3://"), Prefix=prefix
        ):
            s3_objects.extend([file["Key"] for file in page["Contents"]])
        return s3_objects


@attr.s
class BaseRecord:
    uuid: str = field(default=None)
    name: str = field(default=None)
    handle: str = field(default=None)
    link: str = field(default=None)
    objtype: str = field(default=None)


@attr.s
class Collection(BaseRecord):
    items = field(factory=list)

    def post_items(self, client):
        """Post items to collection."""
        for item in self.items:
            logger.info(f"Posting item: {item}")
            item_uuid, item_handle = client.post_item_to_collection(self.uuid, item)
            item.uuid = item_uuid
            item.handle = item_handle
            logger.info(f"Item posted: {item_uuid}")
            for bitstream in item.bitstreams:
                bitstream_uuid = client.post_bitstream(item_uuid, bitstream)
                bitstream.uuid = bitstream_uuid
                logger.info(f"Bitstream posted: {bitstream_uuid}")
            yield item

    @classmethod
    def create_metadata_for_items_from_csv(cls, csv_reader, field_map):
        """Create metadata for the collection's items based on a CSV and a JSON mapping
        field map."""
        items = [Item.metadata_from_csv_row(row, field_map) for row in csv_reader]
        return cls(items=items)


@attr.s
class Community(BaseRecord):
    collections = field(default=None)


@attr.s
class Item(BaseRecord):
    metadata: list = field(factory=list)
    bitstreams: list = field(factory=list)
    file_identifier: str = field(default=None)
    source_system_identifier: str = field(default=None)

    def bitstreams_in_directory(
        self, s3_client, bucket: str, prefix="", search_in="", delimiter: str = "-"
    ):
        """Create a list of bitstreams from S3 file objects.

        Args:
            s3_client (S3Client): S3Client object.
            bucket (str): Name of S3 bucket containing files.
            prefix (str): Folder (or prefix pattern) within the S3 bucket in which
                to look for files.
            delimiter (str, optional): Delimiter used to retrieve the file identifier from the filename.
                Defaults to "-".
        """
        file_paths = s3_client.list_objects(bucket=bucket, prefix=prefix)
        if search_in:
            file_paths = filter_files_by_prefix(file_paths, prefixes=search_in)

        for file_path in file_paths:
            file_name = file_path.split("/")[-1]
            file_directory = "/".join([bucket, *file_path.split("/")[:-1]])
            self.bitstreams.append(
                Bitstream(name=file_name, file_path=f"{file_directory}/{file_name}")
            )
        self.bitstreams.sort(key=lambda x: x.name)

    @classmethod
    def metadata_from_csv_row(cls, row, field_map):
        """Create metadata for an item based on a CSV row and a JSON mapping field map."""
        metadata = []
        for f in field_map:
            field = row[field_map[f]["csv_field_name"]]
            if field != "":
                if f == "file_identifier":
                    file_identifier = field
                    continue  # file_identifier is not included in DSpace metadata
                if f == "source_system_identifier":
                    source_system_identifier = field
                    continue  # source_system_identifier is not included in DSpace
                metadata
                delimiter = field_map[f]["delimiter"]
                language = field_map[f]["language"]
                if delimiter:
                    metadata.extend(
                        [
                            MetadataEntry(key=f, value=v, language=language)
                            for v in field.split(delimiter)
                        ]
                    )
                else:
                    metadata.append(MetadataEntry(key=f, value=field, language=language))
        return cls(
            metadata=metadata,
            file_identifier=file_identifier,
            source_system_identifier=source_system_identifier,
        )


@attr.s
class Bitstream:
    name: str = field(default=None)
    file_path = field(default=None)


@attr.s
class MetadataEntry:
    key = field(default=None)
    value = field(default=None)
    language = field(default=None)
