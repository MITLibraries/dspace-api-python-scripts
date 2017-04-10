# dspace-data-collection

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
