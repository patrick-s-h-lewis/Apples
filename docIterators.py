from abc import ABCMeta, abstractmethod,abstractproperty
import codecs
import json
import sys
import pymongo
from pymongo import MongoClient

def progress(ind,size):
    percent = int(100*float(ind)/size)
    sys.stdout.write('\r[{0}{1}] {2}% {3}'.format('#'*(percent/10),' '*(10-percent/10), percent, ind))
    sys.stdout.flush()
    
class DocumentIter(object):
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def source():
        return None
    
    @abstractproperty
    def size():
        return None
    
    @abstractmethod
    def __iter__():
        yield None
    
    @abstractproperty   
    def sanitiser():
        return None
    
    @abstractproperty
    def iter_type():
        return 'SIMPLE'
    
class SimpleDiskIter(DocumentIter):
    size=0
    source=''
    sanitiser=None
    iter_type='SIMPLE'

    def __init__(self,txf,sanit):
        self.source=txf
        self.sanitiser=sanit
        ind=0
        for line in codecs.open(txf,'r',encoding='utf8'):
            ind+=1
        self.size=ind

    def __iter__(self):
        for line in codecs.open(self.source,'r',encoding='utf8'):
            if ind%1000==0:
                progress(ind,self.size)
            doc = self.sanitiser.sanitise(line).split()
            yield doc
            
class JsonDiskIter(DocumentIter):
    size=0
    source=''
    sanitiser=None
    iter_type='SIMPLE'
    
    def __init__(self,txf,sanit,iter_type='SIMPLE'):
        self.source=txf
        self.sanitiser=sanit
        ind=0
        for line in codecs.open(txf,'r',encoding='utf8'):
            ind+=1
        self.size=ind
        self.iter_type=iter_type
        
    def __iter__(self):
        ind=0
        for line in codecs.open(self.source,'r',encoding='utf8'):
            record = json.loads(line)
            title = record['title']
            abstract_sents = record['abstract']
            ind+=1
            doc =[]
            if ind%1000==0:
                progress(ind,self.size)
            doc.append(self.sanitiser.sanitise(title).split())
            san_abs=[]
            for sent in abstract_sents:
                doc.append(self.sanitiser.sanitise(sent).split())
            if self.iter_type=='DOC':
                yield doc
            elif self.iter_type=='SIMPLE': 
                yield [word for sent in doc for word in sent]
            else:
                for sent in doc:
                    yield sent
        print('\n')
        
class MongoIter(DocumentIter):
    size=0
    source=''
    sanitiser=None
    iter_type='SIMPLE'
    
    def __init__(self,db_conn,query,sanit,iter_type='SIMPLE'):
        self.sanitiser=sanit
        self.source=MongoClient(db_conn)
        self.query=query
        self.size=self.source.find(query).count()
        self.iter_type=iter_type
    
    def __iter__(self):
        ind=0
        for record in self.source.find(self.query):
            title = record['title']
            abstract_sents = record['abstract']
            ind+=1
            doc=[]
            if ind%1000==0:
                progress(ind,self.size)
            doc.append(self.sanitiser.sanitise(title).split())
            for sent in abstract_sents:
                doc.append(self.sanitise.sanitise(sent).split())
            if self.iter_type=='DOC':
                yield doc
            elif self.iter_type=='SIMPLE': 
                yield [word for sent in doc for word in sent]
            else:
                for sent in doc:
                    yield sent
        print('\n')
            
class SimpleMemorySentIter(DocumentIter):
    size =0
    source=[]
    sanitiser=None
    iter_type="SIMPLE"
    
    def __init__(self,source,sanit):
        self.size = len(source)
        self.source=source
        self.sanitser=sanit
        
    def __iter(self):
        ind=0
        for record in self.source:
            ind+=1
            if ind%1000==0:
                progress(ind,self.size)
            yield [self.sanitiser(record).split()]
        print('\n')