from predictors import Predictor
import numpy
from scipy.interpolate import UnivariateSpline,lagrange,Rbf
from Configuration import Configuration

class polyPredictor(Predictor.Predictor):
    
    def __init__(self, dataManager,engine,hist=-1,context=None):
        super().__init__("poly",dataManager,hist,context)
   
    def runAll(self):
        self.preprocess()
        
    
    @staticmethod
    def forecast(y,degree=3):
        
        x = [i for i in range(0,len(y))]
        
        p = UnivariateSpline( a, sequence, k=3)
        #p = numpy.poly1d(numpy.polyfit(x, y, degree))
        
        res = p(len(y))
        if numpy.isinf(res) or numpy.isnan(res):
            return 0
        
        return res
    
    def predict(self,sticker,timestamp,context):
        closehist = context[2]
        tomorrow = polyPredictor.forecast(closehist,3)
        return (int(numpy.sign(tomorrow)),1,False)
    
        