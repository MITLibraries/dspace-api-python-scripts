# dspace-editing

**Note**: These scripts were updated in 05/2018 for the new authentication method used by DSpace 6.x

All of these scripts require a secrets.py file in the same directory that must contain the following text:
```
        baseURL='https://dspace.myuni.edu'
        email='dspace_user@.myuni.edu'
        password='my_dspace_password'    
        filePath = '/Users/dspace_user/dspace-data-collection/data/'
        handlePrefix = 'http://dspace.myuni.edu/handle/'
        verify = True or False (no quotes). Use False if using an SSH tunnel to connect to the DSpace API
```
The 'filePath' is directory into which output files will be written and 'handlePrefix' may or may not vary from your DSpace URL depending on your configuration. This secrets.py file will be ignored according to the repository's .gitignore file so that DSpace login details will not be inadvertently exposed through Github.

If you are using both a development server and a production server, you can create a separate secrets.py file with a different name (e.g. secretsProd.py) and containing the production server information. When running each of these scripts, you will be prompted to enter the file name (e.g 'secretsProd' without '.py') of an alternate secrets file. If you skip the prompt or incorrectly type the file name, the scripts will default to the information in the secrets.py file. This ensures that you will only edit the production server if you really intend to.

**Note**: All of these scripts skip collection '45794375-6640-4efe-848e-082e60bae375' for local reasons. To change this, edit the following portion of the script (typically between line 27-39)


Skips collection 45794375-6640-4efe-848e-082e60bae375:

                for j in range (0, len (collections)):
                        collectionID = collections[j]['uuid']
                        if collectionID != '45794375-6640-4efe-848e-082e60bae375':
                                offset = 0


No collections skipped:

                for j in range (0, len (collections)):
                        collectionID = collections[j]['uuid']
                        if collectionID != 0:
                                offset = 0

#### [addKeyValuePairOnHandleCSV.py](addKeyValuePairOnHandleCSV.py)
Based on user input, adds key-value pairs from a specified CSV file of DSpace item handles and the value to be added to that item using the specified key. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [addKeyValuePairToCollection.py](addKeyValuePairToCollection.py)
Based on user input, adds a specified key-value pair with a specified language value to every item in the collection with the specified handle.

#### [addKeyValuePairToCommunity.py](addKeyValuePairToCommunity.py)

#### [addNewItemsToCollection.py](addNewItemsToCollection.py)

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

#### [deleteKeyValuePairFromCollection.py](deleteKeyValuePairFromCollection.py)

#### [editBitstreamsNames.py](editBitstreamsNames.py)

#### [overwriteExistingMetadata.py](overwriteExistingMetadata.py)

#### [postCollection.py](postCollection.py)
Based on user input, creates a collection with a specified name within the specified community.  In the specified directory (within the filePath set by the secrets.py file), the script creates items and associated metadata based on a 'collectionMetadata.json' file in the directory. Based on the specified file extension, the script then posts each file in the directory  with that extension as a bitstream for the appropriate item, which is determined by having the file name (minus the file extension) in a 'dc.identifier.other' field in the item metadata record.

#### [removeDuplicateKeyValuePairsFromItems.py](removeDuplicateKeyValuePairsFromItems.py)
Finds all items with duplicate key-value pairs and removes the duplicates. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceKey.py](replaceKey.py)
Based on user input, replaces one specified key with another specified key in all item metadata across the repository. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceKeyForCollection.py](replaceKeyForCollection.py)
Based on user input, replaces one specified key with another specified key in all item metadata across the specified collection. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceKeyForCommunity.py](replaceKeyForCommunity.py)
Based on user input, replaces one specified key with another specified key in all item metadata across the specified community. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceKeyValuePairOnItemIdCSV.py](replaceKeyValuePairOnItemIdCSV.py)

#### [replaceKeyValuePairsFromCSV.py](replaceKeyValuePairsFromCSV.py)
Based on user input, updates key-value pairs from the specified CSV file with the columns: 'replacedKey,' 'replacementKey,'replacedValue,' and 'replacementValue.' A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [replaceUnnecessarySpaces.py](replaceUnnecessarySpaces.py)
Based on user input, removes double spaces, triple spaces, and spaces before commas in the values from the specified key in the specified community.

#### [replaceValueInCollection.py](replaceValueInCollection.py)

#### [replaceValueInCommunityFromCSV.py](replaceValueInCommunityFromCSV.py)

#### [repositoryMetadataBackup.py](repositoryMetadataBackup.py)
Creates a folder with a timestamp in the folder name and creates a JSON file for every collection in the repository with the metadata for all of the items in that collection.

#### [repositoryMetadataRestore.py](repositoryMetadataRestore.py)
Based on user input, restores the metadata from a specified backup folder that was created by the repositoryMetadataBackup.py script.

#### [splitFieldIntoMultipleFields.py](splitFieldIntoMultipleFields.py)

#### [updateLanguageTagsForKey.py](updateLanguageTagsForKey.py)
Based on user input, updates the language value for the specified key to 'en_us' for all items with that key in the repository. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the metadata of each item that is updated.

#### [updateLanguageTagsForKeyInCollection.py](updateLanguageTagsForKeyInCollection.py)
