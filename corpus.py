from gensim import corpora
import corpus_stats
import codecs
import docIterators
import sanitisers
import gensim

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
            self.dictionary = corpora.Dictionary(doc_iter)
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
            self.doc_iter.iter_type='DOC'
            for doc in self.doc_iter:
                weights=[]
                for sent in doc:
                    if sent!=[]:
                        tfidf=self.get_tfidf_doc(sent)
                        weights.append(map( lambda w: tfidf[zip(*tfidf)[0].index(self.inv_dict[w])][1],sent))
                ex = json.dumps([doc,weights])
                f.write(ex+'\n')
        print('EXPORT COMPLETE')
        
def load_corpus(source,name='UNTITLED',dictionary_file=None,tfidf_file=None):
    san = sanitisers.NullSanitiser()
    dcit = docIterators.JsonDiskIter(source,san)
    if dictionary_file:
        dictionary=corpora.Dictionary.load(dictionary_file)
    else:
        dictionary=None
    if tfidf_file:
        tfidf = models.TfidfModel.load(tfidf_file)
    else:
        tfidf=None
    return Corpus(name,dcit,dictionary=dictionary,tfidf_model=tfidf)