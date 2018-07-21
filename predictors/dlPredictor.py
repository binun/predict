from Configuration import Configuration
from predictors import Predictor
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.layers.recurrent import LSTM
from sklearn.preprocessing import StandardScaler
from Service.Utilities import Tools
import numpy
import pandas
import traceback
from sklearn.preprocessing import MinMaxScaler
import test
#https://www.datacamp.com/community/tutorials/deep-learning-python#predict
# pip install tensorflow keras

class dlPredictor(Predictor.Predictor):
        
    def __init__(self, dataManager,hist=-1,context=None):
        super().__init__("dl",dataManager,hist)
        self.model = None
        self.features = 7
        
        self.scaler = MinMaxScaler(feature_range=(-1, 1))
        
        
    @staticmethod
    def timeseries_to_supervised(data, lag=1):
        df = pandas.DataFrame(data)
        columns = [df.shift(i) for i in range(1, lag+1)]
        columns.append(df)
        df = pandas.concat(columns, axis=1)
        df.fillna(0, inplace=True)
        return df
    
    @staticmethod
    def difference(dataset, interval=1):
        diff = list()
        for i in range(interval, len(dataset)):
            value = dataset[i] - dataset[i - interval]
            diff.append(value)
        return pandas.Series(diff)
    
    @staticmethod
    def inverse_difference(history, yhat, interval=1):
        return yhat + history[-interval]
    
    def scale(self,train, test):
    
        self.scaler = self.scaler.fit(train)
    
        train = train.reshape(train.shape[0], train.shape[1])
        train_scaled = self.scaler.transform(train)
    
        test = test.reshape(test.shape[0], test.shape[1])
        test_scaled = self.scaler.transform(test)
        return train_scaled, test_scaled
    
    def invert_scale(self,X, value):
        new_row = [x for x in X] + [value]
        array = numpy.array(new_row)
        array = array.reshape(1, len(array))
        inverted = self.scaler.inverse_transform(array)
        return inverted[0, -1]
    
    def fit_lstm(self,train, batch_size, nb_epoch, neurons):
        X, y = train[:, 0:-1], train[:, -1]
        X = X.reshape(X.shape[0], 1, X.shape[1])
        if self.model is None:
            
            self.model = Sequential()
            self.model.add(LSTM(neurons, batch_input_shape=(batch_size, X.shape[1], X.shape[2]), stateful=True))
            self.model.add(Dense(1))
            self.model.compile(loss='mean_squared_error', optimizer='adam')
        
        for i in range(nb_epoch):
            self.model.fit(X, y, epochs=1, batch_size=batch_size, verbose=0, shuffle=False)
            self.model.reset_states()
    
    def forecast_lstm(self,batch_size, X):
        X = X.reshape(1, 1, len(X))
        yhat = self.model.predict(X, batch_size=batch_size)
        return yhat[0,0]
    
    def runAll(self):
        self.preprocess()
    
    def predict(self,sticker,timestamp,context):
        highhist = context[0]
        lowhist = context[1]
        closehist = context[2]
        volumehist = context[3]
        openhist = context[4]
        
        raw_values = closehist
        diff_values = dlPredictor.difference(raw_values, 1)
        supervised = dlPredictor.timeseries_to_supervised(diff_values, 1)
        supervised_values = supervised.values
        train, test = supervised_values[0:-1], supervised_values[-1:]
        train_scaled, test_scaled = self.scale(train, test)
        self.fit_lstm(train_scaled, 1, 50, 5)
        
        train_reshaped = train_scaled[:, 0].reshape(len(train_scaled), 1, 1)
        self.model.predict(train_reshaped, batch_size=1)
        
        X, y = test_scaled[0, 0:-1], test_scaled[0, -1]
        yhat = self.forecast_lstm(1, X)
        
        yhat = self.invert_scale(X, yhat)
    
        yhat = self.inverse_difference(raw_values, yhat, len(test_scaled)+1)
        
        prediction = int(numpy.sign(yhat))
        
        confidence=1.0
        skip = False # if True, then not confident
        
        del X
        del y
        del diff_values
        del train
        del test
        del train_scaled
        del test_scaled
        
        del highhist
        del lowhist
        del closehist
        del volumehist
        del openhist
            
        
        return (prediction,confidence,skip)