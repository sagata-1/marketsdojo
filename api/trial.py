import tradermade as tm
# set api key
tm.set_rest_api_key("XZas9_pK9fByyYTKXbUa")

#get data
tm.live(currency='EURUSD,GBPUSD',fields=["bid", "mid", "ask"]) # returns live data - fields is optional
    
tm.historical(currency='EURUSD,GBPUSD', date="2021-04-22",interval="daily", fields=["open", "high", "low","close"]) # returns historical data for the currency requested interval is daily, hourly, minute - fields is optional
    
tm.timeseries(currency='EURUSD', start="2023-12-15-00:00",end="2023-12-18-09:15",interval="hourly",fields=["open", "high", "low","close"]) # returns timeseries data for the currency requested interval is daily, hourly, minute - fields is optional
    
print(tm.cfd_list()) # gets list of all cfds available
    
print(tm.currency_list()) # gets list of all currency codes available add two codes to get code for currencypair ex EUR + USD gets EURUSD