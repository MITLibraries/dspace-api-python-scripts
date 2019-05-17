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


if __name__ == '__main__':
    unittest.main(warnings='ignore')
