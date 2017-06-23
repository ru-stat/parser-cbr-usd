""" Download USD RUR official exchange rate from Bank of Russia web site."""

import pandas as pd
import datetime
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# FIXME: use Cookiecutter file structure with 'data/processed'
#        CSV_FILENAME = Path(__file__).parent / "data" / "cbr_er.txt"
    
# TODO: save csv with daily frequency "dfd.csv"
                            
# TODO: save as json from pandas

CSV_FILENAME = "cbr_er.txt"
ER_VARNAME = "FX_USDRUR_rub"
  
class Filters:
    """Functions to transform dirty values to text and float."""
    
    def as_date(string):
        try:
            return datetime.datetime.strptime(string,"%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Error parsing date <{}>".format(string))
    
    
    def to_float(string):
        # starting 02.06.1993 there are values like "2 153,0000"
        s = string.replace(",",".") \
                  .replace(chr(160),"")
        try:
            return float(s)
        except ValueError:
            raise ValueError("Error parsing value <{}>".format(string))


class Source:
    """URL definition for datasource"""
    
    DATE_FORMAT = '%d/%m/%Y'
    TEMPLATE = 'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={0}&date_req2={1}&VAL_NM_RQ=R01235'
    
    def __init__(self, start=None, end=None):
        start = self.get_start(start)
        end = self.get_end(end)        
        self.url = self.make_url(start, end)
    
    def make_url(self, start, end):
        assert isinstance(start, datetime.date)
        assert isinstance(end, datetime.date)
        s = start.strftime(self.DATE_FORMAT)
        e = end.strftime(self.DATE_FORMAT)
        return self.TEMPLATE.format(s, e)
    
    def get_url(self):
        return self.url 
        
    @staticmethod 
    def get_start(start: str):
        if not start:        
           start = datetime.date(1992, 7, 1)
        else:
           start = pd.to_datetime(start).date()
        return start
    
    @staticmethod
    def get_end(end: str):
        if not end:    
            end = datetime.datetime.today()     
        else:
            end = pd.to_datetime(end).date()
        return end        

             
class Downloader:   

    # FIXME: file locations 
    XML_CACHE_FILE = "er_xml.txt"
    
    def __init__(self, start=None, end=None):
        self.url = Source(start, end).get_url()     
    
    def get_xml(self):
        r = requests.get(self.url)
        return r.text
    
    def save_xml(self):    
        text = self.get_xml()
        Path(self.XML_CACHE_FILE).write_text(text)

    def get_xml_cached(self):    
        return Path(self.XML_CACHE_FILE).read_text()
    
    
class Parser:
    
    def __init__(self, xml_text):
        """Accept xml_text and create pd.Series"""
        gen = self.xml_text_to_stream(xml_text)
        d = {pd.to_datetime(date): price for date, price in gen}
        ts = pd.Series(d, name = ER_VARNAME)
        self.ts = self.transform(ts)

    @staticmethod
    def xml_text_to_stream(text):        
        root = ET.fromstring(text)
        for child in root:
            date = Filters.as_date(child.attrib['Date'])
            value = Filters.to_float(child[1].text)
            yield date, value   
        
    @staticmethod    
    def transform(ts):
        #divide values before 1997-12-30 by 1000
        ix = ts.index <= "1997-12-30"
        ts.loc[ix] = ts[ix] / 1000
        return ts.round(4)        
        
    def get(self):
        return self.ts    
    

class LocalData:     
    # FIXME: convert to data/processed reader/dumper
    
    def dump(ts):
        ts.to_csv(CSV_FILENAME, header = True)
        print ("Saved to", CSV_FILENAME)
    
    def read(path = CSV_FILENAME):
        df = pd.read_csv(path, index_col = 0) 
        df.index = pd.to_datetime(df.index)
        return df[df.columns[0]].round(4)
        
    
class Ruble():    
    
    def __init__(self):                
        """Read from local data copy or update from web"""
        try:
            self.ts = LocalData.read()
        except FileNotFoundError:
            print("Local data file not found")
            self.update()
      
    def update(self):
        print("Updating from web...")
        # FIXME: always updates full dataset, its expensive 
        #        may read latest values and concat
        Downloader().save_xml()
        xml_text = Downloader().get_xml_cached()
        self.ts = Parser(xml_text).get()
        LocalData.dump(self.ts)          
        return self
        
    def get(self):
        return self.ts

    def save_df(self):
        # FIXME: write to data/processed
        # TODO: write in json        
        pass
    
   
if __name__ == "__main__":
    er = Ruble().get()
    print(er.tail())
    Ruble().update()
