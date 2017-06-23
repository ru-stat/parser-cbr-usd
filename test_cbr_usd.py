import datetime
import pytest
from cbr_usd import Filters, Source, Downloader, Ruble


class TestFilters(object):

    def test_to_float_valid_input(self):
        assert Filters.to_float("2{}153,0000".format(chr(160))) == 2153

    def test_to_float_on_invalid_input(self):
        with pytest.raises(ValueError):
            Filters.to_float("2,000,000.00")

    def test_as_date_on_valid_input(self):
        assert Filters.as_date("30.01.2001") == datetime.date(2001, 1, 30)

    def test_as_date_on_invalid_input(self):
        with pytest.raises(ValueError):
            Filters.as_date("30/01/2001")


class TestSource(object):
    DATE_1 = "2001-03-15"
    DATE_2 = "2001-03-30"

    BASE_URL = "http://www.cbr.ru/scripts/XML_dynamic.asp"

    def test_get_url(self):
        assert Source().get_url().startswith(self.BASE_URL)

    def test_get_start(self):
        assert Source.get_start(self.DATE_1) == datetime.date(2001, 3, 15)
        assert Source.get_start(self.DATE_2) == datetime.date(2001, 3, 30)

    def test_source_url(self):
        url = self.BASE_URL + "?date_req1={}&date_req2={}&VAL_NM_RQ=R01235"
        url = url.format("/".join(reversed(self.DATE_1.split("-"))),
                         "/".join(reversed(self.DATE_2.split("-"))))
        assert Source(self.DATE_1, self.DATE_2).url == url


class TestDownloader(object):

    def test_get_xml_catched(self):
        file_start = '<?xml version="1.0" encoding="windows-1251"'
        assert Downloader().get_xml_cached().startswith(file_start)


class TestParser(object):
    pass


class TestLocalData(object):
    pass


class TestRuble():
    DATE_1 = '2017-06-10'
    DATE_2 = '1997-12-27'

    def test_get_on_old_date(self):
        assert Ruble().get()[self.DATE_1] == 57.0020

    def test_get_on_new_date(self):
        assert Ruble().get()[self.DATE_2] == 5.95800
