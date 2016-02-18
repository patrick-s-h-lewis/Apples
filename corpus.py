from gensim import corpora
import corpus_stats
import codecs
import docIterators
import sanitisers
import gensim
import random
import json

class Corpus(object):
    doc_iter=None
    dictionary=None
    inv_dict=None
    name='UNNAMED_CORPUS'
    statistics =None
    tfidf_model=None
    
    def __init__(self,name,doc_iter,dictionary=None,tfidf_model=None):
        self.doc_iter = doc_iter
        print('Building Dictionary')
        if dictionary:
            self.dictionary=dictionary
        else:
            iter_type=doc_iter.iter_type
            self.doc_iter.iter_type='SIMPLE'
            self.dictionary = corpora.Dictionary(doc_iter)
            self.doc_iter.iter_type=iter_type
        self.inv_dict = {v:k for k,v in self.dictionary.iteritems()}
        self.name=name
        if tfidf_model:
            self.tfidf_model=tfidf_model
    
    def get_cbow_doc(self,sent):
        return self.dictionary.doc2bow(sent)
    
    def generate_stats(self,filename):
        self.statistics = corpus_stats(self.doc_iter,self.name)
    
    def get_tfidf_model(self):
        print('Creating TF-IDF Model')
        return gensim.models.TfidfModel(dictionary=self.dictionary)
    
    def get_tfidf_doc(self,sent):
        return self.tfidf_model[self.get_cbow_doc(sent)]
        
    def export2jsonfile(self,filename):
        if self.tfidf_model==None:
            self.tfidf_model=self.get_tfidf_model()
        with codecs.open(self.name+filename,'w',encoding='utf8') as f:
            self.doc_iter.iter_type='DOI'
            for doc in self.doc_iter:
                doc_weights=[]
                sent_weights=[]
                sents=doc['doc']
                words=[word for sent in sents for word in sent]
                #get doc tfidf weights
                doc_tfidf=self.get_tfidf_doc(words)
                doc_tfdict={k[0]:k[1] for k in doc_tfidf}
                for i in range(len(doc['doc'])):
                    doc_weights.append([doc_tfdict[self.inv_dict[j]] for j in doc['doc'][i]])
                #get sent tfidf weights
                for sent in sents:
                    sent_tfidf=self.get_tfidf_doc(sent)
                    sent_tfdict={k[0]:k[1] for k in sent_tfidf}
                    weight=[sent_tfdict[self.inv_dict[word]] for word in sent]
                    sent_weights.append(weight)
                ex = json.dumps({'doi':doc['doi'],'tfidf-doc-weights':doc_weights,'tfidf-sent-weights':sent_weights})
                f.write(ex+'\n')
        print('EXPORT COMPLETE')
    
    def get_sample(self,sample_size,return_type='DOI',doc_iter=None):
        print('Sampling '+str(sample_size)+' random documents')
        randoms = [random.randint(0,self.doc_iter.size) for i in range(sample_size)]
        randoms=list(set(randoms))#remove duplicates
        while len(randoms)<sample_size:#top up random sample to required size
            top_up = random.randint(0,self.doc_iter.size)
            if not(top_up in randoms):randoms.append(top_up)
        sample=[]
        ind=0
        if doc_iter==None:
           self.doc_iter.iter_type=return_type
           doc_iter=self.doc_iter
        for record in doc_iter:
            if ind in randoms:
                sample.append(record)
            ind+=1
        return sample
