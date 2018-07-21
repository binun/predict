import os
import pandas
from dataman import DataManager
import numpy
from Configuration import Configuration
import datetime


class OnlineDataManager(DataManager.DataManager):
    
    onlineStickerLists = {'dow': 'https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/Indicies/dowjonesIA.csv', 
                          'nasdaq': 'https://www.stockmarketeye.com/csv/watchlists/NASDAQ-100.csv',
                          'sandp': 'https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/Indicies/SP500.csv'
                        }
    #monnames=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    
    def __init__(self, dsource,nmonths):
        
        super().__init__(dsource)
        
        self.nmonths = nmonths
        
        # quandl.ApiConfig.api_key = '-nddzywDFm_KPNH5v4uK'
        
    def fetchAllData(self):
        
        if not os.path.exists("{0}_stickers.csv".format(self.datasource)):
            online_list=OnlineDataManager.onlineStickerLists[self.datasource]
            df=pandas.read_csv(online_list,parse_dates=True)
        else:
            df=pandas.read_csv("{0}_stickers.csv".format(self.datasource),header=None,parse_dates=True)
        
        fetched_stickers = []
            
        for val in df.values:
            fetched_stickers.append(val[0])
#         for val in ['WMT','XOM']:
#             self.stickers.append(val)
                
        for sticker in fetched_stickers:
            
            r = self.fetchStickerData(sticker)
            if r is None:
                continue
            
            (m,locdates) = r
            self.stickers.append(sticker)
            print("Data collected: {0} records, {1} timestamps".format(len(m),len(locdates)))
            self.rawData.append(m)
            for ld in locdates:
                if not ld in self.datesList:
                    self.datesList.append(ld)
        
        
    def fetchStickerData(self,sticker):
        print("Downloading sticker {0} ".format(sticker))
       
        df = None
        enddate=datetime.datetime.today().strftime('%b+%d+%Y')
        startdate=(datetime.datetime.today()-datetime.timedelta(days=30*self.nmonths)).strftime('%b+%d+%Y')
        try:
            url = "https://finance.google.com/finance/historical?q={0}&startdate={1}&enddate={2}&output=csv".format(sticker,startdate,enddate)

#             if df is not None:
#                 del df
#                 gc.collect()
            
            df = pandas.read_csv(url)
            #sleep(1)

        except:
            print('{0} - No history'.format(sticker))
            return None
        
        if len(df.values)<=Configuration.maxhistlen+1:
            print('History for {0} is too short: {1} records'.format(sticker,str(len(df.values))))
            return None
            
        histdata=df.values
        np={}
    
        for record in reversed(histdata):
            
            date = str(record[0])
            components = date.split('-')
            d=''
            if len(components[0])==1:
                d = '0'+components[0]
            else:
                d = components[0]
                
            fancydate = '20{0}-{1}-{2}'.format(components[2],components[1],d)       
            values=[0]*5
            for i in range(0,5):
                
                if isinstance(record[i+1], str):
                    if record[i+1]=='-':           
                        values[i] = 0
                    else:
                        values[i] = float(record[i+1])
                else:
                    values[i] = record[i+1]
            np[fancydate]=values
                        
        return np
            
        
        
        
            
            
        