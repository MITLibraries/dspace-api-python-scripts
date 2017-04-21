# dspace-editing

All of these scripts require a secrets.py file in the same directory that must contain the following text:
```
        baseURL='https://dspace.myuni.edu'
        email='dspace_user@.myuni.edu'
        password='my_dspace_password'    
        filePath = '/Users/dspace_user/dspace-data-collection/data/'
        handlePrefix = 'http://dspace.myuni.edu/handle/'
```
The 'filePath' is directory into which output files will be written and 'handlePrefix' may or may not vary from your DSpace URL depending on your configuration. This secrets.py file will be ignored according to the repository's .gitignore file so that DSpace login details will not be inadvertently exposed through Github

**Note**: All of these scripts skip collection '24' for local reasons. To change this, edit the following portion of the script (typically between line 27-39)


Skips collection 24: 

                for j in range (0, len (collections)):
                        collectionID = collections[j]['id']
                        if collectionID != 24:
                        offset = 0
            
            
No collections skipped:

                for j in range (0, len (collections)):
                        collectionID = collections[j]['id']
                        if collectionID != 0:
                        offset = 0

#### [addKeyValuePairOnHandleCSV.py](addKeyValuePairOnHandleCSV.py)

#### [createItemMetadataFromCSV.py](createItemMetadataFromCSV.py)

#### [postItem.py](postItem.py)
Based on user input, this script creates a community with a specified name and collection with a specified name within that community.  In the specified directory (within the filePath set by the secrets.py file), the script creates items and associated metadata based on a 'collectionMetadata.json' file in the directory. Based on the specified file extension, the script then posts each file in the directory  with that extension as a bitstream for the appropriate item, which is determined by having the file name (minus the file extension) in a 'dc.identifier.other' field in the item metadata record.

#### [removeDuplicateKeyValuePairsFromItems.py](removeDuplicateKeyValuePairsFromItems.py)
This script finds all items with duplicate key-value pairs and removes the duplicates. A CSV log is written with all of the items that were edited and a 'dc.description.provenance' note describing the change is added to the item metadata.

#### [replaceKey.py](replaceKey.py)
Based on user input, this script replaces one specified key with another specified key in all item metadata across the repository. A CSV log is written with all of the changes made and a 'dc.description.provenance' note describing the change is added to the item metadata. 

#### [replaceKeyValuePairsFromCSV.py](replaceKeyValuePairsFromCSV.py)

#### [replaceUnnecessarySpaces.py](replaceUnnecessarySpaces.py)

#### [repositoryMetadataBackup.py](repositoryMetadataBackup.py)

#### [repositoryMetadataRestore.py](repositoryMetadataRestore.py)

#### [updateLanguageTagsForKey.py](updateLanguageTagsForKey.py)
