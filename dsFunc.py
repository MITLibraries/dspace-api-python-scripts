import datetime
import time


def elapsedTime(startTime, label):
    """Generate elapsed time."""
    td = datetime.timedelta(seconds=time.time() - startTime)
    print(label + ': {}'.format(td))
