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
        instArray = ['secretsProd', '', 'secrets', '#$%#%##@']
        for inst in instArray:
            if inst == 'secretsProd':
                secrets = dsFunc.instSelect(inst)
                self.assertTrue(secrets.__name__ == inst)
            elif inst == 'secrets':
                secrets = dsFunc.instSelect(inst)
                self.assertTrue(secrets.__name__ == inst)
            else:
                secrets = dsFunc.instSelect(inst)
                self.assertTrue(secrets.__name__ == 'secrets')

    def testAuth(self):
        """Return email to confirm acceptance of credentials."""
        instArray = ['secretsProd', '', 'secrets', '#$%#%##@']
        for inst in instArray:
            secrets = dsFunc.instSelect(inst)
            email = secrets.email
            baseURL = secrets.baseURL
            password = secrets.password
            verify = secrets.verify
            cookies, header = dsFunc.auth(email, password, baseURL, verify)

            uName, authEmail = dsFunc.authConfirm(cookies, baseURL, header,
                                                  verify)
            self.assertIn(email, authEmail)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
