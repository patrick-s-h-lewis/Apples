from abc import ABCMeta, abstractmethod,abstractproperty
import json
import re
import codecs
import nltk.stem

class Sanitiser(object):
    __metaclass__=ABCMeta
    @abstractmethod
    def sanitise():
        return None
    
    def remove_unicode_punct(self,sentence, chars):
        return re.sub(u'(?u)[' + re.escape(''.join(chars)) + ']', ' ', sentence)
        
class NullSanitiser(Sanitiser):
        
    def sanitise(self,sentence):
        return sentence
    
class StopWordSanitiser(Sanitiser):
    def __init__(self,stopwords_file,punct_file):
        with codecs.open(stopwords_file,'r',encoding='utf8') as f:
            self.stopwords = json.load(f)
        with codecs.open(punct_file,'r',encoding='utf8') as f:
            self.punct_filter = json.load(f)
    
    def sanitise(self,sentence):
        lt = sentence.lower()
        slt = lt.strip()
        tslt = self.remove_unicode_punct(slt,self.punct_filter)
        stop_filtered = [i for i in tslt.split() if i not in self.stopwords]
        export = u' '.join(stop_filtered)
        return export

class MinimalSanitiser(Sanitiser):
    def __init__(self,punct_file):
        with codecs.open(punct_file,'r',encoding='utf8') as f:
            self.punct_filter = json.load(f)
    
    def sanitise(self,sentence):
        lt = sentence.lower()
        slt = lt.strip()
        tslt = self.remove_unicode_punct(slt,self.punct_filter)
        export = u' '.join(tslt.strip().split())
        return export

class StemmingSanitise(Sanitiser):
    def __init__(self,stopwords_file,punct_file,stem_type):
        with codecs.open(stopwords_file,'r',encoding='utf8') as f:
            self.stopwords = json.load(f)
        with codecs.open(punct_file,'r',encoding='utf8') as f:
            self.punct_filter = json.load(f)
        self.stem_type=stem_type
        if stem_type=='SNOWBALL':
            self.stemmer = nltk.stem.snowball.EnglishStemmer()
        elif stem_type=='PORTER':
            self.stemmer = nltk.stem.PorterStemmer() 
        elif stem_type=='LANCASTER':
            self.stemmer = nltk.stem.LancasterStemmer()
        elif stem_type=='WORDNET':
            self.stemmer = nltk.stem.WordNetLemmatizer()
    
    def sanitise(self,title):
        lt = title.lower()
        slt = lt.strip()
        tslt = self.remove_unicode_punct(slt,self.punct_filter)
        stop_filtered = [i for i in tslt.split() if i not in self.stopwords]
        if self.stem_type=='WORDNET':
            stem_filtered = [self.stemmer.lemmatize(i) for i in stop_filtered]
        else:
            stem_filtered = [self.stemmer.stem(i) for i in stop_filtered]
        export = u' '.join(stem_filtered)
        return export
    