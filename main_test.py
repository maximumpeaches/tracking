import unittest
import main
import datetime

class TestMain(unittest.TestCase):
    def test_bedtime_start_date_same_day(self):
        bsd = main.get_bedtime_start_date('2024-08-23 21:58:34')
        self.assertEqual(bsd, datetime.datetime(2024, 8, 23))

    def test_bedtime_start_date_previous_day(self):
        """Tests that if I went to bed past midnight, the date for when I went to bed is adjusted back by one."""
        bsd = main.get_bedtime_start_date('2024-08-23 3:03:34')
        self.assertEqual(bsd, datetime.datetime(2024, 8, 22))

    def test_convert_to_hours_a(self):
        hours = main.convert_to_hours(516.0)
        self.assertEqual(hours, 8.6)


if __name__ == "__main__":
    unittest.main()