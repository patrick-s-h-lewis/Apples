from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

def plot_ziphian(zt,filename):
    sample = []
    log_ranks = list(zip(*zt)[2])
    log_freqs = list(zip(*zt)[4])
    for s in np.arange(log_ranks[0],log_ranks[-1],log_ranks[1]):   
        sample.append(log_ranks.index(min(log_ranks,key=lambda x:abs(x-s))))
    z_grad,z_c = np.polyfit([log_ranks[s] for s in sample],[log_freqs[s]for s in sample],1)
    line_freq = map(lambda x: z_grad*x+z_c,log_ranks)
    plt.close()
    plt.plot(log_ranks,log_freqs,'r')
    plt.plot(log_ranks,line_freq,'b')
    plt.savefig(filename)
    print('Saved Ziphian Plot')
    plt.close()
    
def plot_doc_length_distro(counter, filename):
    plt.plot(counter.keys(),counter.values(),'o')
    plt.savefig(filename)
    plt.close()
    print('Saved Document Length Distribution Plot')

def get_corpus_stats(doc_iter,outfile_name):
    word_freq = Counter()
    word_count = 0
    document_count = 0
    unique_word_count=0
    document_lengths = Counter()
    for doc in doc_iter:
        word_count+=len(doc)
        document_count+=1
        document_lengths.update([len(doc)])
        upd = []
        word_freq.update(doc)
    unique_word_count=len(word_freq)
    mean_doc_length = float(word_count)/float(document_count)
    mode_doc_length = document_lengths.most_common(1)[0]
    print('Generated Counting Stats')
    ranked_word_freq = word_freq.most_common()
    ziphian_table = []
    for rank in range(unique_word_count):
        w = ranked_word_freq[rank][0]
        f = ranked_word_freq[rank][1]
        log_r = math.log(rank+1,10)
        log_f = math.log(f,10)
        ziphian_table.append((w,r,log_r,f,log_f))
    print('Generated Ziphian Data')
    plot_ziphian(ziphian_table,outfile+'_ziphian_plot.png')
    plot_doc_lenth_distro(document_lengths,outfile_name+'_document_word_lengths.png')
    with open(outfile_name+'_ziphian_data.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['word','rank','log rank','freqency','log_frequncy'])
        writer.writerows(ziphian_table)
    print('Writen Ziphian Data To file')
    with open(outfile_name+'_document_lengths.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['words per document','number of documents'])
        writer.writerows(zip(document_lengths.keys(),document_lengths.values()))
    print('Writen Document Length Distribution data to file')
    with open(outfile_name+'stats.txt','wb') as f:
        f.write('Word count : '+str(word_count)+'\n')
        f.write('Unique words : ' + str(unique_word_count)+'\n')
        f.write('Mean document word count : ' + str(mean_doc_length)+'\n')
        f.write('Mode document word count : '+ str(mode_doc_length[0])+'\n')
        f.write('Document count : ' + str(document_count)+'\n')
        f.write('Ziphian gradient : '+str(z_grad)+'\n')
        f.write('Ziphian intercept : '+str(z_c)+'\n')
        f.write('most_frequent 10 words : '+'\n')
        for w in ziphian_table[0:10]:
            f.write('"'+w[0]+'" : '+str(w[3])+' occurances\n')
    print('Written stats report to file')
    return {'word_count':word_count,
        'unique_word_count':unique_word_count,
        'document_count':document_count,
        'mean_doc_length':mean_doc_length,
        'mode_doc_length':mode_doc_length[0],
        '10_most_common_words':list(zip(*ziphian_table[:10])[0])}
        
        
        
    