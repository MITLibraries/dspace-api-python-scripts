# DSpace API Python Scripts

DSpace API Python Scripts (DSAPS) is a Python CLI application for managing uploads to DSpace. DSAPS has only been used on instances running DSpace 6.3 and has not been tested on other versions.

Note: Previously, the repository comprised of self-contained scripts that could be run independently. Those scripts can be found as a [release](https://github.com/MITLibraries/dspace-api-python-scripts/releases/tag/v1.0).

## Development

- To preview a list of available Makefile commands: `make help`
- To install with dev dependencies: `make install`
- To update dependencies: `make update`
- To run unit tests: `make test`
- To lint the repo: `make lint`
- To run the app: `pipenv run dsaps --help`

### Reconciling files with metadata CSV

```bash
pipenv run dsaps --url $DSPACE_URL -e $DSPACE_EMAIL -p $DSPACE_PASSWORD reconcile -m <metadata-csv> -o /output -d <content-directory> -t <file-type>
```

### Creating a new collection within a DSpace community

```bash
pipenv run dsaps --url $DSPACE_URL -e $DSPACE_EMAIL -p $DSPACE_PASSWORD newcollection -c <community-handle> -n <collection-name>
```

### Adding items to a DSpace collection

The command below shows `newcollection` and `additems` being run in conjunction with each other. Note that the invocation must call `newcollection` first. In practice, this is the command that is usually run:

```bash
pipenv run dsaps --url $DSPACE_URL -e $DSPACE_EMAIL -p $DSPACE_PASSWORD newcollection -c <community-handle> -n <collection-name> additems -m <metadata-csv> -f config/<field-mapping>.json -d <s3-bucket-name> -t <file-type> 
``` 

## Environment 

### Required

```shell
# The url for the DSpace REST API
DSPACE_URL=

# The email associated with the DSpace user account used for authentication
DSPACE_EMAIL=

# The password associated with the DSpace user account used for authentication
DSPACE_PASSWORD=
```

## CLI commands

All CLI commands can be run with `pipenv run <COMMAND>`.

### `dsaps`

```
Usage: -c [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  --url TEXT           The url for the DSpace REST API. Defaults to env var
                       DSPACE_URL if not set.  [required]
  -e, --email TEXT     The email associated with the DSpace user account used
                       for authentication. Defaults to env var DSPACE_EMAIL if
                       not set.  [required]
  -p, --password TEXT  The password associated with the DSpace user account
                       used for authentication. Defaults to env var
                       DSPACE_PASSWORD if not set.  [required]
  --help               Show this message and exit.

Commands:
  additems       Add items to a DSpace collection.
  newcollection  Create a new DSpace collection within a community.
  reconcile      Match files in the content directory with entries in the metadata CSV file.
```

### `dsaps reconcile`

```
Usage: -c reconcile [OPTIONS]

  Match files in the content directory with entries in the metadata CSV file.

  Running this method creates the following CSV files:

      * metadata_matches.csv: File identifiers for entries in metadata CSV
      file with a corresponding file in the content directory.

      * no_files.csv: File identifiers for entries in metadata CSV file
      without a corresponding file in the content directory.

      * no_metadata.csv: File identifiers for files in the content directory
      without a corresponding entry in the metadata CSV file.

      * updated-<metadata-csv>.csv: Entries from the metadata CSV file with a
      corresponding file in the content directory.

Options:
  -m, --metadata-csv FILE       The filepath to a CSV file containing metadata
                                for Dspace uploads.  [required]
  -o, --output-directory TEXT   The filepath where output files are written.
  -d, --content-directory TEXT  The name of the S3 bucket containing files for
                                DSpace uploads.  [required]
  -t, --file-type TEXT          The file type for DSpace uploads (i.e., the
                                file extension, excluding the dot).
  --help                        Show this message and exit.
```

### `dsaps newcollection`
```
Usage: -c newcollection [OPTIONS]

  Create a new DSpace collection within a community.

Options:
  -c, --community-handle TEXT  The handle identifying a DSpace community in
                               which a new collection is created.  [required]
  -n, --collection-name TEXT   The name assigned to the DSpace collection
                               being created.  [required]
  --help                       Show this message and exit.
```

### `dsaps additems`

```
Usage: -c additems [OPTIONS]

  Add items to a DSpace collection.

  The method relies on a CSV file with metadata for uploads, a JSON document
  that maps metadata to a DSpace schema, and a directory containing the files
  to be uploaded.

Options:
  -m, --metadata-csv FILE       The filepath to a CSV file containing metadata
                                for Dspace uploads.  [required]
  -f, --field-map FILE          The filepath to a JSON document that maps
                                columns in the metadata CSV file to a DSpace
                                schema.  [required]
  -d, --content-directory TEXT  The name of the S3 bucket containing files for
                                DSpace uploads.  [required]
  -t, --file-type TEXT          The file type for DSpace uploads (i.e., the
                                file extension, excluding the dot).
  -r, --ingest-report           Create ingest report for updating other
                                systems.
  -c, --collection-handle TEXT  The handle identifying a DSpace collection
                                into which uploads are deposited.
  --help                        Show this message and exit.
```

