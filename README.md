# dspace-data-collection

All of these scripts require a secrets.py file in the same directory that must contain the following text:
```
        baseURL='https://dspace.myuni.edu'
        email='dspace_user@.myuni.edu'
        password='my_dspace_password'    
        filePath = '/Users/dspace_user/dspace-data-collection/data/' # directory into which to store output files
        handlePrefix = 'http://dspace.myuni.edu/handle/' # handlePrefix may vary from your dspace url (or may not)
```
This secrets.py file will be ignored according to the repository's .gitignore file so that DSpace login details will not be inadvertently exposed through Github

*Note that all of these scripts skip collection '24' for local reasons. To change this, edit the following portion of the script (typically between line 27-39)

Skips collection 24 

        for j in range (0, len (collections)):
          collectionID = collections[j]['id']
          if collectionID != 24:
            offset = 0
            
No collections skipped:

        for j in range (0, len (collections)):
          collectionID = collections[j]['id']
          if collectionID != 0:
            offset = 0
            
#### [compareTwoKeysInCommunity.py](compareTwoKeysInCommunity.py)
Based on user input, this script extracts the values of two specified keys from a specified community to a CSV file for comparison.

#### [findBogusUris.py](findBogusUris.py)
This script extracts the item ID and the value of the key 'dc.identifier.uri' to a CSV file when the value does not begin with the handlePrefix specified in the secrets.py file. 

#### [findDuplicateKeys.py](findDuplicateKeys.py)
Based on user input, this script extracts item IDs to a CSV file where there are multiple instances of the specified key in the item metadata.

#### [getCollectionMetadataJson.py](getCollectionMetadataJson.py)
Based on user input, this script extracts all of the item metadata from the specified collection to a JSON file.

#### [getCompleteAndUniqueValuesForAllKeys.py](getCompleteAndUniqueValuesForAllKeys.py)
This script creates a 'completeValueLists' folder and for all keys used in the repository, extracts all values for a particular key to a CSV with item IDs.  It also creates a 'uniqueValueLists' folder, that writes a CSV file for each key with all unique values and a count of how many times the value appears.

#### [getGlobalLanguageValues.py](getGlobalLanguageValues.py)
This script extracts all unique language values used by metadata entries in the repository to a CSV file.

#### [getLanguageValuesForKeys.py](getLanguageValuesForKeys.py)
This script extracts all unique pairs of keys and language values used by metadata entries in the repository to a CSV file.

#### [getRecordsAndValuesForKey.py](getRecordsAndValuesForKey.py)
Based on user input, this script extracts the ID and URI for all items in the repository with the specified key, as well as the value of the specified key, to a CSV file.

#### [getRecordsWithKeyAndValue.py](getRecordsWithKeyAndValue.py)
Based on user input, this script extracts the ID and URI for all items in the repository with the specified key-value pair to a CSV file.

#### [metadataOverview.py](metadataOverview.py)
This script produces several CSV files containing different information about the structure and metadata of the repository:

        collectionMetadataKeys.csv - A list of all keys used in each collection with collection name, ID, and handle.   
        dspaceIDs.csv - A list of every item ID along with the IDs of the collection and community that contains that item.
        dspaceTypes.csv - A list of all unique values for the key 'dc.type'
        keyCount.csv - A list of all unique keys used in the repository, as well as a count of how many times it appear.
        collectionStats.csv - A list of all collections in the repository with the collection name, ID, handle, and number of items.
