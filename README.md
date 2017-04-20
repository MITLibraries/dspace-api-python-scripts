# dspace-data-collection

All of these scripts require a secrets.py file in the same directory that must contain the following text:
```
        baseURL='https://dspace.myuni.edu'
        email='dspace_user@.myuni.edu'
        password='my_dspace_password'    
        filePath = '/Users/dspace_user/dspace-data-collection/data/' # full path to a directory into which to store output files
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

#### [findBogusUris.py](findBogusUris.py)

#### [findDuplicateKeys.py](findDuplicateKeys.py)

#### [getCollectionMetadataJson.py](getCollectionMetadataJson.py)

#### [getCompleteAndUniqueValuesForAllKeys.py](getCompleteAndUniqueValuesForAllKeys.py)

#### [getGlobalLanguageValues.py](getGlobalLanguageValues.py)

#### [getLanguageValuesForKeys.py](getLanguageValuesForKeys.py)

#### [getRecordsAndValuesForKey.py](getRecordsAndValuesForKey.py)

#### [getRecordsWithKeyAndValue.py](getRecordsWithKeyAndValue.py)

#### [metadataOverview.py](metadataOverview.py)

