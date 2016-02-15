import numpy as np
import gensim.models
from abc import ABCMeta, abstractmethod,abstractproperty

class VectorGenerator(object):
    __metaclass__=ABCMeta
    @abstractmethod
    def get_vector():
        return None
    @abstractproperty
    def model():
        return None
    @abstractproperty
    def dimensionality():
        return None
        
class RaspberryGenerator(VectorGenerator):
    model = {}
    dimensionality=0
    
    def __init__(self,model):
        self.model=model
        self.dimensionality=model.vector_size
        
    def get_vector(self,doc,weights=None):
        acc=np.zeros(self.dimensionality)
        divisor = 0
        for w in doc['title'].split():
            try:
                divisor+=1
                acc+=self.model[w]
            except:
                pass
        for se in s['abstract']:
            for w in se.split():
                try:
		    acc+=self.model[w]
                    divisor+=1
                except:
		     pass
        if divisor==0:
	    divisor=1 #stop division by zero
        return acc/divisor

class BlueberryGenerator(VectorGenerator):
    model = {}
    dimensionality=0
    
    def __init__(self,model):
        self.model=model
        self.dimensionality=model.vector_size
        
    def get_vector(self,doc,weights=None):
        acc=np.zeros(self.dimensionality)
        divisor = 0
        doc = filter(lambda x: x != [], doc)
        if weights==None:
            weights = [[1. for w in s] for s in doc]
        sent_no = len(doc)
        for i in range(sent_no):
            sent = doc[i]
            weight= weights[i]
            for j in range(len(sent)):
                try:
                    acc+=weight[j]*(self.model[sent[j]])
                    divisor+=weight[j]
                except:
                    pass
        if divisor==0:
            divisor=1. #stop division by zero
        return acc/divisor
    
class RhubarbGenerator(VectorGenerator):
    model = {}
    dimensionality=0
     
    def __init__(self,model):
        self.model=model
        self.dimensionality=model.vector_size
     
    def get_vector(self,doc,weights=None):
        divisor = 0
        acc=np.zeros(self.dimensionality)
        for w in doc.split():
            try:
                divisor+=1
                acc+=self.model[w]
            except:
	        pass
	if divisor==0:
            divisor=1 #stop division by zero
        return acc/divisor

     
  

        
        
        
