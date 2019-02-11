# dspace-api

This repository was created from the merger of https://github.com/ehanson8/dspace-editing and https://github.com/ehanson8/dspace-data-collection, both of which have been archived. All further development will occur in this repository.

**Note**: Upgraded to Python 3 in 02/2019.

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

If you are using both a development server and a production server, you can create a separate secrets.py file with a different name (e.g. secretsProd.py) and containing the production server information. When running each of these scripts, you will be prompted to enter the file name (e.g 'secretsProd' without '.py') of an alternate secrets file. If you skip the prompt or incorrectly type the file name, the scripts will default to the information in the secrets.py file. This ensures that you will only edit the production server if you really intend to.

#### [addKeyValuePairOnHandleCSV.py](addKeyValuePairOnHandleCSV.py)
Based on user input, adds key-value pairs from a specified CSV file of DSpace item handles and the value to be added to that item using the specified key. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [addKeyValuePairToCollection.py](addKeyValuePairToCollection.py)
Based on user input, adds a specified key-value pair with a specified language value to every item in the collection with the specified handle.

#### [addKeyValuePairToCommunity.py](addKeyValuePairToCommunity.py)
Based on user input, adds a specified key-value pair with a specified language value to every item in every collection in the community with the specified handle.

#### [addNewItemsToCollection.py](addNewItemsToCollection.py)
Based on user input, adds new items to the specified collection. In the specified directory, the script creates items and associated metadata based on a 'metadataNewFiles.json' file in the directory. The script then posts files for the appropriate items, which is determined by having the file name (minus the file extension) in a 'dc.identifier.other' field in the item metadata record.

#### [compareTwoKeysInCommunity.py](compareTwoKeysInCommunity.py)
Based on user input, extracts the values of two specified keys from a specified community to a CSV file for comparison.

#### [countInitialedNamesByCollection.py](countInitialedNamesByCollection.py)
Based on [mjanowiecki's](https://github.com/mjanowiecki) [findInitialedNamesByCollection.py](https://github.com/mjanowiecki/dspace-data-collection/blob/master/findInitialedNamesByCollection.py), find values in name fields that appear to have first initials that could be expanded to full names and provides a count for each collection when the count is more than zero.

#### [createItemMetadataFromCSV.py](createItemMetadataFromCSV.py)
Based on user input, creates a JSON file of metadata that can be added to a DSpace item from the specified CSV file or from values directly specified in the script. The 'createMetadataElementCSV' function in the script is used to create a metadata element from the specified CSV file and has three variables:

- 'key' - The Dublin Core property to be used for the element.
- 'value' - The column in the specified CSV file that contains the data for the element.
- 'language' - The desired language value for the element

The 'createMetadataElementDirect' function in the script is used to create a metadata element without a CSV file (intended for metadata elements that will be constant across all items in a collection) and has three variables:

- 'key' - The Dublin Core property to be used for the element.
- 'value' - The actual value of the element.
- 'language' - The desired language value for the element.

#### [deleteBitstreamsFromItem.py](deleteBitstreamsFromItem.py)
Based on user input, removes all bitstreams associated with an item with the specified handle.

#### [deleteKeyFromCollection.py](deleteKeyFromCollection.py)
Based on user input, removes all key-value pairs with the specified key for every item in the collection with the specified handle.

#### [deleteKeyFromCommunity.py](deleteKeyFromCommunity.py)
Based on user input, removes all key-value pairs with the specified key for every item in every collection in the community with the specified handle.

#### [deleteKeyValuePairFromCollection.py](deleteKeyValuePairFromCollection.py)
Based on user input, removes all key-value pairs with the specified key and value for every item in the collection with the specified handle.

#### [editBitstreamsNames.py](editBitstreamsNames.py)
Based on a specified CSV file of DSpace item handles and replacement file names, replaces the name of bitstreams attached to the specified items.

#### [exportSelectedRecordMetadataToCSV.py](exportSelectedRecordMetadataToCSV.py)
Based a CSV of item handles, extracts all metadata (except 'dc.description.provenance' values) from the selected items to a CSV file.

#### [findBogusUris.py](findBogusUris.py)
Extracts the item ID and the value of the key 'dc.identifier.uri' to a CSV file when the value does not begin with the handlePrefix specified in the secrets.py file.

#### [findDuplicateKeys.py](findDuplicateKeys.py)
Based on user input, extracts item IDs to a CSV file where there are multiple instances of the specified key in the item metadata.

#### [generateCollectionLevelAbstract.py](generateCollectionLevelAbstract.py)
Based on user input, creates an HTML collection-level abstract that contains hyperlinks to all of the items in each series, as found in the metadata CSV. This assumes that the series title is recorded in 'dc.relation.ispartof' or a similar property in the DSpace item records. The abstract is then posted to the collection in DSpace.

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

#### [overwriteExistingMetadata.py](overwriteExistingMetadata.py)
Based on a specified CSV file of DSpace item handles and file identifiers, replaces the metadata of the items with specified handles with the set of metadata elements associated with the corresponding file identifier in a JSON file of metadata entries named 'metadataOverwrite.json.'

#### [postCollection.py](postCollection.py)
Based on user input, creates a collection with a specified name within the specified community. In the specified directory, the script creates items and associated metadata based on a 'collectionMetadata.json' file in the directory. Based on the specified file extension, the script then posts each file in the directory  with that extension as a bitstream for the appropriate item, which is determined by having the file name (minus the file extension) in a 'dc.identifier.other' field in the item metadata record.

#### [removeDuplicateKeyValuePairsFromItems.py](removeDuplicateKeyValuePairsFromItems.py)
Finds all items with duplicate key-value pairs and removes the duplicates. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceKey.py](replaceKey.py)
Based on user input, replaces one specified key with another specified key in all item metadata across the repository. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceKeyForCollection.py](replaceKeyForCollection.py)
Based on user input, replaces one specified key with another specified key in all item metadata across the specified collection. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceKeyForCommunity.py](replaceKeyForCommunity.py)
Based on user input, replaces one specified key with another specified key in all item metadata across the specified community. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceKeyValuePairOnItemIdCSV.py](replaceKeyValuePairOnItemIdCSV.py)
Based on user input, updates key-value pairs on the specified items from the specified CSV file with the columns: 'replacedKey,' 'replacementKey,' 'replacedValue,' 'replacementValue,' and 'itemID.' A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceKeyValuePairsFromCSV.py](replaceKeyValuePairsFromCSV.py)
Based on user input, updates key-value pairs from the specified CSV file with the columns: 'replacedKey,' 'replacementKey,' 'replacedValue,' and 'replacementValue.' A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceUnnecessarySpaces.py](replaceUnnecessarySpaces.py)
Based on user input, removes double spaces, triple spaces, and spaces before commas in the values from the specified key in the specified community.

#### [replaceValueInCollection.py](replaceValueInCollection.py)
Based on user input, replaces a specified value with another specified value in all item metadata across the specified collection. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceValueInCommunityFromCSV.py](replaceValueInCommunityFromCSV.py)
Based on a user specified CSV, replaces specified values in the specified community with specified replacement values. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [repositoryMetadataBackup.py](repositoryMetadataBackup.py)
Creates a folder with a timestamp in the folder name and creates a JSON file for every collection in the repository with the metadata for all of the items in that collection.

#### [repositoryMetadataRestore.py](repositoryMetadataRestore.py)
Based on user input, restores the metadata from a specified backup folder that was created by the repositoryMetadataBackup.py script.

#### [splitFieldIntoMultipleFields.py](splitFieldIntoMultipleFields.py)
Based on a user specified CSV, replaces a single field with multiple values into multiple fields which each contain a single value.

#### [updateLanguageTagsForKey.py](updateLanguageTagsForKey.py)
Based on user input, updates the language value for the specified key to 'en_us' for all items with that key in the repository. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [updateLanguageTagsForKeyInCollection.py](updateLanguageTagsForKeyInCollection.py)
Based on user input, updates the language value for the specified key to 'en_us' for all items with that key in the specified collection. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.
