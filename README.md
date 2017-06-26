
Scrapper            |  cbr-usd 
--------------------|----------------------------------------
Job                 |  Parse XML from Bank of Russia to get official USD/RUR exchange rate
Source  URL         |  *FIXME*: add source
Source type         |  XML/API  <!-- Word, Excel, CSV, HTML, XML, API, other -->
Frequency           |  Daily
When released       |  After 11.30am 
Scrapper code       | <https://github.com/ru-stat/parser-cbr-usd/blob/master/cbr_usd.py>
Test health         | *FIXME*: add TRAVIS-CI
Test coverage       | *FIXME*: can add some more
Controller          | [cbr_usd.Ruble().update()](https://github.com/ru-stat/parser-cbr-usd/blob/master/cbr_usd.py#L148-L156)
CSV endpoint        | *FIXME*: add endpoint
List of variables   | ```USDRUR_CBR_rub```
Frontpage data      | *TODO*
Validation          | *TODO*

All historic raw data available on internet? 
- [x] Yes
- [ ] No  

Is scrapper automated (can download required information from internet  without manual operations)? 
- [x] Yes
- [ ] No 

Is raw data source well structured?
- [x] Yes
- [ ] No 

TODO:
- [ ] make ```data/interim``` and ```data/processed```folders
- [ ] save XML cache to ```data/interim``` + save final data to ```data/processed```
- [ ] make dataframe CSV
