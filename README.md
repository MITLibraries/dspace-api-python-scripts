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

#### [checkCommunityForKey.py](checkCommunityForKey.py)

#### [createItemMetadataFromCSV.py](createItemMetadataFromCSV.py)

#### [postItem.py](postItem.py)

#### [removeDuplicateKeyValuePairsFromItems.py](removeDuplicateKeyValuePairsFromItems.py)

#### [replaceKey.py](replaceKey.py)

#### [replaceKeyValuePairsFromCSV.py](replaceKeyValuePairsFromCSV.py)

#### [replaceUnnecessarySpaces.py](replaceUnnecessarySpaces.py)

#### [repositoryMetadataBackup.py](repositoryMetadataBackup.py)

#### [repositoryMetadataRestore.py](repositoryMetadataRestore.py)

#### [updateLanguageTagsForKey.py](updateLanguageTagsForKey.py)

#### [uppercaseCheck.py](uppercaseCheck.py)
