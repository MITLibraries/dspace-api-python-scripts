# dsaps

This command line application provides several ways of interacting with the [DSpace](https://github.com/DSpace/DSpace) API. This application was written for DSpace 6.3, it has not been tested against other DSpace versions. Previously, this branch of the repository was a set of self-contained scripts that could be run independently, those scripts can be found as a [release](https://github.com/MITLibraries/dspace-api-python-scripts/releases/tag/v1.0).

## Installation
Clone the repository and install using [pipenv](https://github.com/pypa/pipenv):
```
pipenv install
```
After installation, run the application with:
```
pipenv run dsaps
```

## Authentication

To authenticate, use the following parameters

Option (short) | Option (long)     | Description
------ | ------ | -----------
N/A | --url | The DSpace API URL (e.g. https://dspace.mit.edu/rest), defaults to the DSPACE_URL environmental variable if nothing is specified
-e | --email | The email of the user for authentication.
-p | --password | The password for authentication.

## Commands

### additems
Adds items to a specified collection from a metadata CSV, a field mapping file, and a directory of files. May be run in conjunction with the newcollection CLI command.

Option (short) | Option (long)             | Description
------ | ------ | -------
-m | --metadata-csv | The path to the CSV file of metadata for the items.
-f | --field-map | The path to JSON field mapping file.
-d | --content-directory | The full path to the content, either a directory of files or a URL for the storage location.
-t | --file-type | The file type to be uploaded, if limited to one file type.
-r | --ingest-report| Create ingest report for updating other systems.
-o | --output-directory | The path of the output files, include / at the end of the path.
-c | --collection-handle | The handle of the collection to which items are being added.


#### Example Usage
```
pipenv run dsaps --url https://dspace.com/rest -e abc@def.com -p ******** additems -m coll_metadata.csv -f config/aspace_mapping.json -d /files/pdfs -t pdf -r -c 111.1/111111
```

### newcollection
Posts a new collection to a specified community. Used in conjunction with the additems CLI command to populate the new collection with items.

Option (short) | Option (long)            | Description
------ | ------ | -------
-c | --community-handle | The handle of the community in which to create the collection.
-n | --collection-name | The name of the collection to be created.

#### Example Usage
```
pipenv run dsaps --url https://dspace.com/rest -e abc@def.com -p ******** newcollection -c 222.2/222222 -n Test\ Collection additems -m coll_metadata.csv -f config/aspace_mapping.json -d /files/pdfs -t pdf -r
```

### reconcile
Runs a reconciliation of the specified files and metadata that produces reports of files with no metadata, metadata with no files, metadata matched to files, and an updated version of the metadata CSV with only the records that have matching files.


Option (short) | Option (long)             | Description
------ | ------ | -------
-m | --metadata-csv | The path of the CSV file of metadata.
-o | --output-directory | The path of the output files, include / at the end of the path.
-d | --content-directory | The full path to the content, either a directory of files or a URL for the storage location.
-t | --file-type | The file type to be uploaded.

#### Example Usage
```
pipenv run dsaps --url https://dspace.com/rest -e abc@def.com -p ******** reconcile -m coll_metadata.csv -o /output -d /files/pdfs -t pdf
```
