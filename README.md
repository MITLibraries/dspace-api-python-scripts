# dspace-data-collection

**Note**: Upgraded to Python 3 in 02/2019. The Python 2.x version can be downloaded [here](https://github.com/ehanson8/dspace-data-collection/releases)

**Note**: These scripts were updated in 05/2018 for the new authentication method used by DSpace 6.x

All of these scripts require a secrets.py file in the same directory that must contain the following text:
```
        baseURL='https://dspace.myuni.edu'
        email='dspace_user@.myuni.edu'
        password='my_dspace_password'    
        filePath = '/Users/dspace_user/dspace-data-collection/data/'
        handlePrefix = 'http://dspace.myuni.edu/handle/'
        verify = True or False (no quotes). Use False if using an SSH tunnel to connect to the DSpace API
        skippedCollections = A list of the 'uuid' of any collections that you wish the script to skip. (e.g. ['45794375-6640-4efe-848e-082e60bae375'])
```
The 'filePath' is directory into which output files will be written and 'handlePrefix' may or may not vary from your DSpace URL depending on your configuration. This secrets.py file will be ignored according to the repository's .gitignore file so that DSpace login details will not be inadvertently exposed through GitHub.

If you are using both a development server and a production server, you can create a separate secrets.py file with a different name (e.g. secretsProd.py) and containing the production server information. When running each of these scripts, you will be prompted to enter the file name (e.g 'secretsProd' without '.py') of an alternate secrets file. If you skip the prompt or incorrectly type the file name, the scripts will default to the information in the secrets.py file. This ensures that you will only access the production server if you really intend to.

#### [compareTwoKeysInCommunity.py](compareTwoKeysInCommunity.py)
Based on user input, extracts the values of two specified keys from a specified community to a CSV file for comparison.

#### [countInitialedNamesByCollection.py](countInitialedNamesByCollection.py)
Based on [mjanowiecki's](https://github.com/mjanowiecki) [findInitialedNamesByCollection.py](https://github.com/mjanowiecki/dspace-data-collection/blob/master/findInitialedNamesByCollection.py), find values in name fields that appear to have first initials that could be expanded to full names and provides a count for each collection when the count is more than zero.

#### [exportSelectedRecordMetadataToCSV.py](exportSelectedRecordMetadataToCSV.py)
Based a CSV of item handles, extracts all metadata (except 'dc.description.provenance' values) from the selected items to a CSV file.

#### [findBogusUris.py](findBogusUris.py)
Extracts the item ID and the value of the key 'dc.identifier.uri' to a CSV file when the value does not begin with the handlePrefix specified in the secrets.py file.

#### [findDuplicateKeys.py](findDuplicateKeys.py)
Based on user input, extracts item IDs to a CSV file where there are multiple instances of the specified key in the item metadata.

#### [getCollectionMetadataJson.py](getCollectionMetadataJson.py)
Based on user input, extracts all of the item metadata from the specified collection to a JSON file.

#### [getCompleteAndUniqueValuesForAllKeys.py](getCompleteAndUniqueValuesForAllKeys.py)
Creates a 'completeValueLists' folder and for all keys used in the repository, extracts all values for a particular key to a CSV with item IDs.  It also creates a 'uniqueValueLists' folder, that writes a CSV file for each key with all unique values and a count of how many times the value appears.

#### [getCompleteAndUniqueValuesForAllKeysInCommunity.py](getCompleteAndUniqueValuesForAllKeysInCommunity.py)
Creates a 'completeValueLists' folder and for all keys used in the specified community, extracts all values for a particular key to a CSV with item IDs.  It also creates a 'uniqueValueLists' folder, that writes a CSV file for each key with all unique values and a count of how many times the value appears.

#### [getFacultyNamesFromETDs.py](getFacultyNamesFromETDs.py)
Based on user input, extracts all values from 'dc.contributor.advisor' and 'dc.contributor.committeeMember' fields from items in collections in the specified community.

#### [getGlobalLanguageValues.py](getGlobalLanguageValues.py)
Extracts all unique language values used by metadata entries in the repository to a CSV file.

#### [getHandlesAndBitstreamsFromCollection.py](getHandlesAndBitstreamsFromCollection.py)
Based on user input, extracts all the handles and bitstreams associated with the items in the specified collection to a CSV file.

#### [getLanguageValuesForKeys.py](getLanguageValuesForKeys.py)
Extracts all unique pairs of keys and language values used by metadata entries in the repository to a CSV file.

#### [getRecordsAndValuesForKey.py](getRecordsAndValuesForKey.py)
Based on user input, extracts the ID and URI for all items in the repository with the specified key, as well as the value of the specified key, to a CSV file.

#### [getRecordsAndValuesForKeyInCollection.py](getRecordsAndValuesForKeyInCollection.py)
Based on user input, extracts the ID and URI for all items in the specified collection with the specified key, as well as the value of the specified key, to a CSV file.

#### [getRecordsWithKeyAndValue.py](getRecordsWithKeyAndValue.py)
Based on user input, extracts the ID and URI for all items in the repository with the specified key-value pair to a CSV file.

#### [identifyItemsMissingKeyInCommunity.py](identifyItemsMissingKeyInCommunity.py)
Based on user input, extracts the IDs of items from a specified community that do not have the specified key.

#### [metadataCollectionsKeysMatrix.py](metadataCollectionsKeysMatrix.py)
Creates a matrix containing a count of each time a key appears in each collection in the repository.

#### [metadataOverview.py](metadataOverview.py)
Produces several CSV files containing different information about the structure and metadata of the repository:

|File Name |Description|
|--------------------------|--------------------------------------------------------------------------|
|collectionMetadataKeys.csv | A list of all keys used in each collection with collection name, ID, and handle.|
|dspaceIDs.csv | A list of every item ID along with the IDs of the collection and community that contains that item.|
|dspaceTypes.csv | A list of all unique values for the key 'dc.type.'|
|keyCount.csv | A list of all unique keys used in the repository, as well as a count of how many times it appear.|
|collectionStats.csv | A list of all collections in the repository with the collection name, ID, handle, and number of items.|
