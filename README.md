# dspace-editing

expects a secrets.py file something like the following:
```
        baseURL='https://dspace.myuni.edu'
        # credentials for an authorized dspace user
        email='dspace_user@.myuni.edu'
        password='my_dspace_password'
        # full path to a directory into which to store output
        filePath = '/Users/dspace_user/dspace-data-collection/data/'
        # handlePrefix may vary from your dspace url (or may not)
        handlePrefix = 'http://dspace.myuni.edu/handle/'
```
this file will be gitignored.

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

#### [addKeyValuePairOnHandleCSV.py](addKeyValuePairOnHandleCSV.py)

#### [checkCommunityForKey.py](checkCommunityForKey.py)

#### [createItemMetadataFromCSV.py](createItemMetadataFromCSV.py)

####[postItem.py](postItem.py)

#### [removeDuplicateKeyValuePairsFromItems.py](removeDuplicateKeyValuePairsFromItems.py)

#### [replaceKey.py](replaceKey.py)

#### [replaceKeyValuePairsFromCSV.py](replaceKeyValuePairsFromCSV.py)

#### [replaceUnnecessarySpaces.py](replaceUnnecessarySpaces.py)

#### [repositoryMetadataBackup.py](repositoryMetadataBackup.py)

#### [repositoryMetadataRestore.py](repositoryMetadataRestore.py)

#### [updateLanguageTagsForKey.py](updateLanguageTagsForKey.py)

#### [uppercaseCheck.py](uppercaseCheck.py)
