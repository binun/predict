from predictors import Predictor
import numpy
from Configuration import Configuration
import traceback
import pandas
from stocker.stocker import Stocker
# https://www.quantstart.com/articles/Autoregressive-Moving-Average-ARMA-p-q-Models-for-Time-Series-Analysis-Part-3

class prophetPredictor(Predictor.Predictor):
    def __init__(self, dataManager,hist=-1,context=None):
        super().__init__("prophet",dataManager,hist)
    
    def runAll(self):
        self.preprocess()
    
    def predict(self,sticker,timestamp,context):
        
        try:
            stock = Stocker(sticker,context)
            #model, model_data = stock.create_prophet_model()
            tomorrow = stock.predict_future(days=1)
            prediction = int(numpy.sign(tomorrow))
            return (prediction,1,False)
        except:
            traceback.print_exc()
            return (0,1,False)
            
    
        