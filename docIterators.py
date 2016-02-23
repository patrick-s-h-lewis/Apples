from abc import ABCMeta, abstractmethod,abstractproperty
import codecs
import json
import sys
import pymongo
from pymongo import MongoClient
import sanitisers
import gensim

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

    def __init__(self,txf,sanit=None):
        self.source=txf
        if sanit:
            self.sanitiser=sanit
        else: 
            self.sanitiser=sanitisers.NullSanitiser()
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
    
    def __init__(self,txf,sanit=None,iter_type='SIMPLE'):
        self.source=txf
        if sanit:
            self.sanitiser=sanit
        else: 
            self.sanitiser=sanitisers.NullSanitiser()
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
            abstract_sents = record['abstract'].split('. ')
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
            elif self.iter_type=='SENTENCES':
                for sent in doc:
                    yield sent
            elif self.iter_type=='DOI':
                yield {'doi':record['doi'],'document':doc}
            elif self.iter_type=='EVERYTHING':
                record['doc']=doc
                yield record
            else:
                pass
        print('\n')
        
class MongoIter(DocumentIter):
    size=0
    source=''
    sanitiser=None
    iter_type='SIMPLE'
    
    def __init__(self,db_conn,query,sanit=None,iter_type='SIMPLE'):
        if sanit:
            self.sanitiser=sanit
        else: 
            self.sanitiser=sanitisers.NullSanitiser()
        self.source=MongoClient(db_conn[0])[db_conn[1]][db_conn[2]]
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
            for sent in abstract_sents.split('u. '):
                doc.append(self.sanitiser.sanitise(sent).split())
            if self.iter_type=='DOC':
                yield doc
            elif self.iter_type=='SIMPLE': 
                yield [word for sent in doc for word in sent]
            elif self.iter_type=='SENTENCES':
                for sent in doc:
                    yield sent
            elif self.iter_type=='DOI':
                yield {'doi':record['doi'],'document':doc}
            else:
                pass
        print('\n')
            
class SimpleMemorySentIter(DocumentIter):
    size =0
    source=[]
    sanitiser=None
    iter_type="SIMPLE"
    
    def __init__(self,source,sanit=None):
        self.size = len(source)
        self.source=source
        if sanit:
            self.sanitiser=sanit
        else: 
            self.sanitiser=sanitisers.NullSanitiser()
        
    def __iter(self):
        ind=0
        for record in self.source:
            ind+=1
            if ind%1000==0:
                progress(ind,self.size)
            yield [self.sanitiser(record).split()]
        print('\n')

class BlueBerryIter(DocumentIter):
    size=0
    source=''
    sanitiser=None
    iter_type='SIMPLE'

class BlueberryIter(DocumentIter):
    size=0
    source=''
    sanitiser=None
    iter_type='SIMPLE'
    
    def __init__(self,db_conn,query=None,sanit=None,iter_type='SIMPLE',from_list=None):
        if sanit:
            self.sanitiser=sanit
        else:
            self.sanitiser=sanitisers.NullSanitiser()
        self.source=MongoClient(db_conn[0])[db_conn[1]][db_conn[2]]
        self.query=query
        self.size=self.source.find(query).count()
        self.iter_type=iter_type
        self.from_list=from_list
    
    def __iter__(self):
        ind=0
        if self.from_list==None:
            for record in self.source.find(self.query):
                doc = record['doc']
                doi = record['doi']
                ind+=1
                if ind%1000==0:
                    progress(ind,self.size)
                if self.iter_type=='DOC':
                    yield doc
                elif self.iter_type=='SIMPLE': 
                    yield [word for sent in doc for word in sent]
                elif self.iter_type=='SENTENCES':
                    for sent in doc:
                        yield sent
                elif self.iter_type=='DOI':
                    yield {'doi':record['doi'],'doc':doc}
                elif self.iter_type=='LABELED_SENTENCES':
                    for sent in doc:
                        yield gensim.models.doc2vec.LabeledSentence(sent,tags=[doi])
                else:
                    pass
        else:
            for doi in self.from_list:
                doc=self.source.find_one({'doi':doi})['doc']
                ind+=1
                if ind%1000==0:
                    progress(ind,self.size)
                if self.iter_type=='DOC':
                    yield doc
                elif self.iter_type=='SIMPLE': 
                    yield [word for sent in doc for word in sent]
                elif self.iter_type=='SENTENCES':
                    for sent in doc:
                        yield sent
                elif self.iter_type=='DOI':
                    yield {'doi':record['doi'],'doc':doc}
                elif self.iter_type=='LABELED_SENTENCES':
                    for sent in doc:
                        yield gensim.models.doc2vec.LabeledSentence(sent,tags=[doi])
                else:
                    pass
        print('\n')

    def get_record(self,doi):
        return self.source.find_one({'doi':doi})  

class JsonBlueberryIter(DocumentIter):
    size=0
    source=''
    sanitiser=None
    iter_type='SIMPLE'
    
    def __init__(self,filename,sanit=None,iter_type='SIMPLE'):
        if sanit:
            self.sanitiser=sanit
        else:
            self.sanitiser=sanitisers.NullSanitiser()
        self.source=filename
        ind=0
        for line in codecs.open(filename,'r',encoding='utf8'):
            ind+=1
        self.size=ind
        self.iter_type=iter_type
        
    def __iter__(self):
        ind=0
        for line in codecs.open(self.source,'r',encoding='utf8'):
            record = json.loads(line)
            doi = record['doi']
            doc = record['doc']
            ind+=1
            if ind%1000==0:
                progress(ind,self.size)
            if self.iter_type=='DOC':
                yield doc
            elif self.iter_type=='SIMPLE': 
                yield [word for sent in doc for word in sent]
            elif self.iter_type=='SENTENCES':
                for sent in doc:
                    yield sent
            elif self.iter_type=='DOI':
                yield {'doi':record['doi'],'doc':doc}
            elif self.iter_type=='EVERYTHING':
                yield record
            elif self.iter_type=='LABELED_SENTENCES':
                for sent in doc:
                    yield gensim.models.doc2vec.LabeledSentence(sent,tags=[doi])
            else:
                pass
        print('\n')
        
class StrawberryIter(DocumentIter):
    size=0
    source=''
    sanitiser=None
    iter_type='SIMPLE'
    
    def __init__(self,db_conn,query=None,sanit=None,iter_type='SIMPLE',from_list=None):
        if sanit:
            self.sanitiser=sanit
        else:
            self.sanitiser=sanitisers.NullSanitiser()
        self.source=MongoClient(db_conn[0])[db_conn[1]][db_conn[2]]
        self.query=query
        self.size=self.source.find(query).count()
        self.iter_type=iter_type
        self.from_list=from_list
    
    def __iter__(self):
        ind=0
        if self.from_list==None:
            for record in self.source.find(self.query):
                doc = record['doc']
                doi = record['doi']
                ind+=1
                if ind%1000==0:
                    progress(ind,self.size)
                if self.iter_type=='DOC':
                    yield doc
                elif self.iter_type=='SIMPLE': 
                    yield [word for sent in doc for word in sent]
                elif self.iter_type=='SENTENCES':
                    for sent in doc:
                        yield sent
                elif self.iter_type=='DOI':
                    yield {'doi':record['doi'],'doc':doc}
                elif self.iter_type=='LABELED_SENTENCES':
                    for sent in doc:
                        yield gensim.models.doc2vec.LabeledSentence(sent,tags=[doi])
                elif self.iter_type=='VECTORS':
                    yield {'doi':doi,'vectors':record['vectors']}
                else:
                    pass
        else:
            for doi in self.from_list:
                doc=self.source.find_one({'doi':doi})['doc']
                ind+=1
                if ind%1000==0:
                    progress(ind,self.size)
                if self.iter_type=='DOC':
                    yield doc
                elif self.iter_type=='SIMPLE': 
                    yield [word for sent in doc for word in sent]
                elif self.iter_type=='SENTENCES':
                    for sent in doc:
                        yield sent
                elif self.iter_type=='DOI':
                    yield {'doi':record['doi'],'doc':doc}
                elif self.iter_type=='LABELED_SENTENCES':
                    for sent in doc:
                        yield gensim.models.doc2vec.LabeledSentence(sent,tags=[doi])
                else:
                    pass
        print('\n')

    def get_record(self,doi):
        return self.source.find_one({'doi':doi})  

    
