import sys
from datetime import datetime
sys.path.append('/Users/shangyeshen/Sites/timesheet')
import unittest
from timesheet.models import Entry

class EntryTestCase(unittest.TestCase):
    """Tests for Entry"""

    def test_is_instance(self):
        current_time = datetime.now()
        self.assertIsInstance(Entry(current_time), Entry)

if __name__ == '__main__':
    unittest.main()
