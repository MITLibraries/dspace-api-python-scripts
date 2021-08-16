import glob
import operator
import os
from functools import partial

import attr
import requests
import structlog

Field = partial(attr.ib, default=None)
Group = partial(attr.ib, default=[])

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
            f"{self.url}/login", headers=header, params=data
        ).cookies["JSESSIONID"]
        cookies = {"JSESSIONID": session}
        status = requests.get(
            f"{self.url}/status", headers=header, cookies=cookies
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
                endpoint, headers=self.header, params=params, cookies=self.cookies
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
            hdl_endpoint, headers=self.header, cookies=self.cookies
        ).json()
        return rec_obj["uuid"]

    def get_record(self, uuid, record_type):
        """Get an individual record of a specified type."""
        url = f"{self.url}/{record_type}/{uuid}?expand=all"
        record = requests.get(url, headers=self.header, cookies=self.cookies).json()
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

    def _build_uuid_list(self, rec_obj, children):
        """Build list of the uuids of the object's children."""
        child_list = []
        for child in rec_obj[children]:
            child_list.append(child["uuid"])
        return child_list

    def _populate_class_instance(self, class_type, rec_obj):
        """Populate class instance with data from record."""
        fields = [op(field) for field in attr.fields(class_type)]
        kwargs = {k: v for k, v in rec_obj.items() if k in fields}
        kwargs["objtype"] = rec_obj["type"]
        if class_type == Community:
            collections = self._build_uuid_list(rec_obj, "collections")
            rec_obj["collections"] = collections
        elif class_type == Collection:
            items = self._build_uuid_list(rec_obj, "items")
            rec_obj["items"] = items
        rec_obj = class_type(**kwargs)
        return rec_obj


@attr.s
class BaseRecord:
    uuid = Field()
    name = Field()
    handle = Field()
    link = Field()
    objtype = Field()


@attr.s
class Collection(BaseRecord):
    items = Group()

    def post_items(self, client):
        """Post items to collection."""
        for item in self.items:
            item_uuid, item_handle = item.post_to_collection(client, self.uuid, item)
            item.uuid = item_uuid
            item.handle = item_handle
            logger.info(f"Item posted: {item_uuid}")
            for bitstream in item.bitstreams:
                bitstream_uuid = bitstream.post_bitstream(client, item_uuid, bitstream)
                bitstream.uuid = bitstream_uuid
                logger.info(f"Bitstream posted: {bitstream_uuid}")
            yield item

    def post_to_community(self, client, community_handle, coll_name):
        """Post a collection to a specified community."""
        hdl_endpoint = f"{client.url}/handle/{community_handle}"
        community = requests.get(
            hdl_endpoint, headers=client.header, cookies=client.cookies
        ).json()
        community_uuid = community["uuid"]
        uuid_endpoint = f"{client.url}/communities/{community_uuid}/collections"
        coll_uuid = requests.post(
            uuid_endpoint,
            headers=client.header,
            cookies=client.cookies,
            json={"name": coll_name},
        ).json()
        coll_uuid = coll_uuid["uuid"]
        logger.info(f"Collection posted: {coll_uuid}")
        return coll_uuid

    @classmethod
    def create_metadata_for_items_from_csv(cls, csv_reader, field_map):
        """Create metadata for the collection's items based on a CSV and a JSON mapping
        field map."""
        items = [Item.metadata_from_csv_row(row, field_map) for row in csv_reader]
        return cls(items=items)


@attr.s
class Community(BaseRecord):
    collections = Field()


@attr.s
class Item(BaseRecord):
    metadata = Group()
    bitstreams = Group()
    file_identifier = Field()
    source_system_identifier = Field()

    def bitstreams_in_directory(self, directory, file_type="*"):
        """Create a list of bitstreams from the specified directory and sort the list."""
        files = glob.iglob(
            f"{directory}/**/{self.file_identifier}*.{file_type}", recursive=True
        )
        self.bitstreams = [
            Bitstream(name=os.path.basename(f), file_path=f) for f in files
        ]
        self.bitstreams.sort(key=lambda x: x.name)

    def delete(self, client):
        """Delete item."""
        endpoint = f"{client.url}/items/{self.uuid}"
        response = requests.delete(
            endpoint, headers=client.header, cookies=client.cookies
        )
        return response.status_code

    @classmethod
    def metadata_from_csv_row(cls, row, field_map):
        """Create metadata for an item based on a CSV row and a JSON mapping field map."""
        metadata = []
        file_identifier = None
        source_system_identifier = None
        for f in field_map:
            field = row[field_map[f]["csv_field_name"]]
            if f == "file_identifier":
                file_identifier = field
                continue  # file_identifier is not included in DSpace metadata
            if f == "source_system_identifier":
                source_system_identifier = field
                continue  # source_system_identifier is not included in DSpace
                # metadata
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

    def post_to_collection(self, client, collection_uuid, item):
        """Post item to a specified collection and return the item ID."""
        endpoint = f"{client.url}/collections/{collection_uuid}/items"
        post_response = requests.post(
            endpoint,
            headers=client.header,
            cookies=client.cookies,
            json={"metadata": attr.asdict(item)["metadata"]},
        ).json()
        item_uuid = post_response["uuid"]
        item_handle = post_response["handle"]
        return item_uuid, item_handle


@attr.s
class Bitstream(BaseRecord):
    name = Field()
    file_path = Field()

    def delete(self, client):
        """Delete bitstream."""
        endpoint = f"{client.url}/bitstreams/{self.uuid}"
        response = requests.delete(
            endpoint, headers=client.header, cookies=client.cookies
        )
        return response.status_code

    def post_bitstream(self, client, item_uuid, bitstream):
        """Post a bitstream to a specified item and return the bitstream
        ID."""
        endpoint = (
            f"{client.url}/items/{item_uuid}" f"/bitstreams?name={bitstream.name}"
        )
        header_upload = {"accept": "application/json"}
        data = open(bitstream.file_path, "rb")
        response = requests.post(
            endpoint, headers=header_upload, cookies=client.cookies, data=data
        ).json()
        bitstream.uuid = response["uuid"]
        return bitstream.uuid


@attr.s
class MetadataEntry:
    key = Field()
    value = Field()
    language = Field()
