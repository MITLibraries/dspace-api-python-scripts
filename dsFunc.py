import datetime
import time


def elapsedTime(startTime, label):
    """Generate elapsed time."""
    td = datetime.timedelta(seconds=time.time() - startTime)
    print(label + ': {}'.format(td))
    return td


def instSelect():
    """Select secrets.py file for the appropriate DSpace instance."""
    sec = input('To edit production server, enter the name of the secrets '
                'file: ')
    if sec != '':
        try:
            secrets = __import__(sec)
            print('Editing Production')
        except ImportError:
            secrets = __import__('secrets')
            print('Editing Development')
    else:
        secrets = __import__('secrets')
        print('Editing Development')

    baseURL = secrets.baseURL
    email = secrets.email
    password = secrets.password
    filePath = secrets.filePath
    verify = secrets.verify
    skipColl = secrets.skipColl
    return(baseURL, email, password, filePath, verify, skipColl, sec)
