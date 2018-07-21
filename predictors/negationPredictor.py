
from predictors import Predictor

class negationPredictor(Predictor.Predictor):

    def __init__(self, origpred):
        nm="neg({0})".format(origpred.name[8:])
        dm=origpred.dataManager
        hist = origpred.histlen
        super().__init__(nm,dm,hist)
        self.predictor_=origpred
        self.stickers = origpred.stickers
        self.predictorList = origpred.predictorList
    
    def runAll(self,since=None,until=None):
        self.preprocess(since,until)
        self.bestpredictors = self.predictor_.bestpredictors
    
    def predict(self,sticker,timestamp,context):
        if self.predictor_.preprocessed:
            
            prediction=self.predictor_.getPrediction(timestamp,sticker)
            conf=self.predictor_.getConfidence(timestamp,sticker)
            negconf=self.predictor_.getnegConfidence(timestamp,sticker)
            skip=self.predictor_.getSkip(timestamp,sticker)
        else:
            (prediction,(conf,negconf),skip) = self.predictor_.predict(sticker,timestamp,context)
            
        return (-prediction,(negconf,conf),skip)
        