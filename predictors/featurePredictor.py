from Configuration import Configuration
from predictors import Predictor
# from keras.models import Sequential
# from keras.layers import Dense, Dropout, Activation
# from keras.layers.recurrent import LSTM
from sklearn.preprocessing import MinMaxScaler
from Service.Utilities import Tools
from sklearn.metrics import mean_squared_error
import numpy
import pandas

#https://www.datacamp.com/community/tutorials/deep-learning-python#predict
# pip install tensorflow keras

class featurePredictor(Predictor.Predictor):
    
    def __init__(self, dataManager,name,engine,hist=-1,context=None):
        super().__init__(name,dataManager,hist,context)
            
        self.engine = engine
        self.scaler = MinMaxScaler()
    
    def runAll(self):
        self.preprocess()
    
    def predict(self,sticker,timestamp,context):
        highhist = context[0]
        lowhist = context[1]
        closehist = context[2]
        volumehist = context[3]
        openhist = context[4]
         
        dataset = pandas.DataFrame()
        dataset['Open'] = openhist
        dataset['High'] = highhist
        dataset['Low'] = lowhist
        dataset['Close'] = closehist
         
        if self.context is not None:
            rg = self.context.recentGains(timestamp,sticker,len(closehist))
            if len(rg)<len(closehist):
                pad = [0]*(len(closehist)-len(rg))
                rg = numpy.append(pad,rg)
            dataset['Performance'] = rg
        
        dataset['Volume'] = volumehist
        dataset = dataset.dropna()
         
        dataset['H-L'] = dataset['High'] - dataset['Low']
        dataset['O-C'] = dataset['Close'] - dataset['Open']
        
#         dataset['3day MA'] = dataset['Close'].shift(1).rolling(window = 3).mean()
#         dataset['10day MA'] = dataset['Close'].shift(1).rolling(window = 10).mean()
#         dataset['30day MA'] = dataset['Close'].shift(1).rolling(window = 30).mean()
#         dataset['Std_dev']= dataset['Close'].rolling(5).std()
#         dataset['RSI'] = Tools.RSI(dataset['Close'].values, 9)
        
        dataset['Price_Rise'] = numpy.append(closehist[1:],[self.dataManager.getAt(sticker,'close',timestamp)])
         
        #dataset['Price_Rise'] = numpy.where(dataset['Close'].shift(-1) > 0, 1, 0)
        #dataset = dataset.dropna()
         
        X = dataset.iloc[:, 4:-1]
        y = dataset.iloc[:, -1]
         
        split = len(dataset)-1
        X_train, X_test, y_train,y_test = X[:split], X[split:], y[:split],y[split:]
         
#         X_train = self.scaler.fit_transform(X_train)
#         X_test = self.scaler.transform(X_test)
         
        self.engine.fit(X_train,y_train)
        
        try:
            sticker_index = self.stickers.index(sticker)
            timestamp_index = self.timestamps.index(timestamp)
            self.slopes[sticker_index][timestamp_index] = self.engine.coef_[0]
        except:
            pass
            
            
        
        delta = self.engine.predict(X_test)
        if y_test.iloc[0]!=0.0:
            confidence = numpy.fabs(delta[0]-y_test.iloc[0])
        else:
            confidence=0
         
        prediction = int(numpy.sign(delta[0]))
        skip=False

         
        del X
        del y
        del dataset
         
        del highhist
        del lowhist
        del closehist
        del volumehist
        del openhist
      
        return (prediction,confidence,skip)