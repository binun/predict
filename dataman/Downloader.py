import os
import pandas

from Configuration import Configuration
import datetime
import quandl
from time import sleep
import quandl


class Downloader():
    
    onlineStickerLists = {'dow': 'https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/Indicies/dowjonesIA.csv', 
                          'nasdaq': 'https://www.stockmarketeye.com/csv/watchlists/NASDAQ-100.csv',
                          'sandp': 'https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/Indicies/SP500.csv'
                        }
    monnames=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    range=['2000','2017']
    def __init__(self, dsource):
        
        self.datasource = dsource
        self.dir=dsource+"_csv"
        
        if os.path.exists(Configuration.predfile):
            os.remove(Configuration.predfile)
        
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        else:
            filelist = [ f for f in os.listdir(self.dir) if f.endswith(".csv") ]
            for f in filelist:
                os.remove(os.path.join(self.dir, f))
        self.download()
        if Configuration.twsactive:
            os.system('java -jar mailer.jar {0}'.format(self.dir))
            
        
    def download(self):
        
        if not os.path.exists("{0}_stickers.csv".format(self.datasource)):
            online_list=Downloader.onlineStickerLists[self.datasource]
            df=pandas.read_csv(online_list,parse_dates=True)
        else:
            df=pandas.read_csv("{0}_stickers.csv".format(self.datasource),header=None,parse_dates=True)
            
        
        for val in df.values:
            self.downloadSticker(val[0])
        
    def downloadSticker(self,sticker):
        print("Downloading sticker {0} ".format(sticker))
        sticker= sticker.upper()
        sd='{0}-01-01'.format(Configuration.simyear)
        ed='{0}-12-31'.format(Configuration.simyear)
        param='WIKI'
            
        df = None
        
        try:
            ds = param+'/'+sticker
            df = quandl.get(ds,startdate=sd,enddate=ed)

        except:
            print('{0} - No history'.format(sticker))
            return
        df = df.reset_index()
        if len(df.values)<=Configuration.maxhistlen+1:
            print('History for {0} is too short: {1} records'.format(sticker,str(len(df.values))))
            return
        log = os.path.join(self.dir, "{0}.TXT".format(sticker))
        
        
        dates = df['Date']
        opens = df['Adj. Open']
        highs = df['Adj. High']
        lows = df['Adj. Low']
        closes = df['Adj. Close']
        volumes = df['Adj. Volume']
        f = open(log, 'w')
        for i in range(0,len(dates)):
            date = dates[i]
            y = '{:0>4}'.format(date.year)
            m = '{:0>2}'.format(date.month)
            d = '{:0>2}'.format(date.day)
            
            
            dn = y+m+d
            message='{0} {1} {2} {3} {4} {5}\n'.format(dn,str(opens[i]),str(highs[i]),str(lows[i]),str(closes[i]),str(volumes[i]))
            f.write(message)
        
        f.close()
        sleep(1)
        del df
            
            
                
            
        
        
        
            
            
        