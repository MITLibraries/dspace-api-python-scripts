import dsFunc
import time
import unittest


class dsFuncTests(unittest.TestCase):
    """Test dsFunc.py functions."""

    def testElapsedTime(self):
        """Test elapsed time function."""
        startTime = time.time()
        sleepTime = 5
        time.sleep(sleepTime)
        td = dsFunc.elapsedTime(startTime, 'Elapsed run time')
        self.assertTrue(sleepTime <= int(td.seconds) <= sleepTime + 1)

    def testInstaSelect(self):
        """Test instance select function."""
        (baseURL, email, password, filePath, verify,
         skipColl, sec) = dsFunc.instSelect()
        secrets = __import__(sec)
        self.assertTrue(baseURL == secrets.baseURL)
        self.assertTrue(email == secrets.email)
        self.assertTrue(password == secrets.password)
        self.assertTrue(filePath == secrets.filePath)
        self.assertTrue(verify == secrets.verify)
        self.assertTrue(skipColl == secrets.skipColl)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
