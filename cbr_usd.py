""" Download USD RUR official exchange rate from Bank of Russia web site."""

import pandas as pd
import datetime
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# TODO: separate scapper job and parser job or document.

# FIXME: use Cookiecutter file structure with 'data/processed'
#        CSV_FILENAME = Path(__file__).parent / "data" / "cbr_er.txt"
    
# TODO: save as json from pandas

CSV_FILENAME = "cbr_er.txt"
ER_VARNAME = "FX_USDRUR_rub"
  
class Filters:
    """Functions to transform dirty values."""
    
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

# TODO - move asserts to tests           
assert Filters.to_float("2{}153,0000".format(chr(160))) == 2153            
assert Filters.as_date("30.01.2001") == datetime.date(2001, 1, 30)  

               
class Downloader:        
    def __init__(self, start=None, end=None):
        s, e = self.make_date_range(start, end)
        template = 'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={0}&date_req2={1}&VAL_NM_RQ=R01235'
        self.url = template.format(s, e)
        
    @staticmethod 
    def make_date_range(start, end):
        """Return data range from 01/07/1992 to today or shorter"""
        DATE_FORMAT = '%d/%m/%Y'
        if not start:        
           start = datetime.date(1992, 7, 1)
        if not end:    
            end = datetime.datetime.today()     
        return start.strftime(DATE_FORMAT), end.strftime(DATE_FORMAT)
    
    def get_xml_as_text(self):
        return requests.get(self.url).text
    
    def iter(self):
        r = requests.get(self.url)
        root = ET.fromstring(r.text)
        for child in root:
            date = Filters.as_date(child.attrib['Date'])
            value = Filters.to_float(child[1].text)
            yield date, value          


assert Downloader.make_date_range(None, None)[0] == '01/07/1992'



# TODO - move asserts to tests   

# def test_make_url():    
#    start = datetime.date(2001,3,2)
#    end = datetime.date(2001,3,14)   
#    target_url = 'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=02/03/2001&date_req2=14/03/2001&VAL_NM_RQ=R01235'
#    assert target_url ==  make_url(start, end)
   
def download_er():
    gen = Downloader().iter()
    d = {pd.to_datetime(date): price for date, price in gen}
    ts = pd.Series(d, name = ER_VARNAME)
    #divide values before 1997-12-30 by 1000
    ix = ts.index <= "1997-12-30"
    ts.loc[ix] = ts[ix] / 1000
    return ts.round(4)

def save_to_csv(ts):
    ts.to_csv(CSV_FILENAME, header = True)

def get_saved_er(path = CSV_FILENAME):
    df = pd.read_csv(path, index_col = 0) 
    df.index = pd.to_datetime(df.index)
    return df[df.columns[0]].round(4)
    

# TODO - move asserts to tests   
   
#def update():
#    er = download_er()
#    assert er['1997-12-27'] == 5.95800 
#    save_to_csv(er)    
#    df = get_saved_er()
#    ts = df[df.columns[0]]
#    # note: had problems with rounding, er and ts are at this point rounded to 4 digits   
#    assert er.equals(ts)
#    return ts   
    

class Ruble():    
    
    def __init__(self):                
        try:
            self.ts = get_saved_er()
        except FileNotFoundError:
            print("Cannot load from local file")
            self.update()
      
    def update(self):
        print("Updating from web...")
        self.ts = download_er()
        save_to_csv(self.ts)    
        return self
        
    def get(self):
        return self.ts    
    
# may also cache xml to local fiel, if necessary to debug XML parser ----------

# FIXME: is cache necessary?
XML_CACHE_FILE = "er_xml.txt"

def save_xml_as_local_file(path = XML_CACHE_FILE):    
    text = Downloader().get_xml_as_text()
    Path(path).write_text(text)
    return path    
    
if __name__ == "__main__":
    er = Ruble().get()
    assert er['2017-06-10'] == 57.0020
    assert er['1997-12-27'] == 5.95800
    print(er.tail())
    Ruble().update()
