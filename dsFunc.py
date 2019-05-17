import datetime
import time


def elapsedTime(startTime, label):
    """Generate elapsed time."""
    td = datetime.timedelta(seconds=time.time() - startTime)
    print(label + ': {}'.format(td))
    return td


def instSelect(instance):
    """Select secrets.py file for the appropriate DSpace instance."""
    if instance != '':
        try:
            secrets = __import__(instance)
            print('Editing ' + secrets.baseURL)
        except ImportError:
            secrets = __import__('secrets')
            print('Editing ' + secrets.baseURL)
    else:
        secrets = __import__('secrets')
        print('Editing ' + secrets.baseURL)

    return secrets
