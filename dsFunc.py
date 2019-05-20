import datetime
import time
import requests


def auth(email, password, baseURL, verify):
    """Authenticate the user to the DSpace API."""
    data = {'email': email, 'password': password}
    header = {'content-type': 'application/json',
              'accept': 'application/json'}
    session = requests.post(baseURL + '/rest/login', headers=header,
                            verify=verify,
                            params=data).cookies['JSESSIONID']
    cookies = {'JSESSIONID': session}
    return(cookies, header)


def authConfirm(cookies, baseURL, header, verify):
    """Confirm user was successfully authenticated to the DSpace API."""
    status = requests.get(baseURL + '/rest/status', headers=header,
                          cookies=cookies, verify=verify).json()
    uName = status['fullname']
    authEmail = status['email']
    print('authenticated', uName, authEmail)
    return(uName, authEmail)


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
