from datetime import time

from sport_parser.khl.data_analysis.formatter import Formatter
from sport_parser.khl.config import Config


class TestFormatter:
    f = Formatter(config=Config)

    def test_time_to_sec(self):
        time1 = time(1, 30, 0)
        assert self.f.time_to_sec(time1) == 5400

    def test_sec_to_time(self):
        time1 = time(1, 30, 0)
        time2 = 5400
        assert self.f.sec_to_time(time1) == '90:00'
        assert self.f.sec_to_time(time2) == '90:00'

    def test_chart_stat_format(self):
        stat1 = 10
        stat2 = time(1, 30, 0)
        assert self.f.chart_stat_format(stat1) == 10
        assert self.f.chart_stat_format(stat2) == 5400

    def test_table_stat_format(self):
        stat_names = {
            'sh': ('Sh', 'int'),
            'sh__e': ('Sh%', 'percent'),
            'time_a': ('TimeA', 'time'),
        }
        stats = {
            'sh': 10,
            'sh__e': 50,
            'time_a': 5400,
        }

        assert self.f.table_stat_format(stats, stat_names) == {
            'sh': '10.0',
            'sh__e': '50.00%',
            'time_a': '90:00',
        }

    def test_date_format(self):
        date1 = '2 декабря 2021, чт'
        date2 = '22 декабря 2021, чт'
        assert self.f.date_format(date1) == '2021-12-02'
        assert self.f.date_format(date2) == '2021-12-22'
