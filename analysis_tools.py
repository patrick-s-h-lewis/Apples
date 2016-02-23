import numpy as np
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE, MDS
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def cosine_mat(a,b):
    dots= np.dot(np.transpose(a),b)
    inter=dots/np.linalg.norm(b,axis=0)
    result=np.transpose(inter)/np.linalg.norm(a,axis=0)
    return result

def get_max(sim_mat):
    dim_b,dim_a = sim_mat.shape
    sim_max = np.argmax(sim_mat)
    a_ind=sim_max%dim_a
    b_ind=sim_max/dim_a
    return sim_mat[sim_max/dim_a,sim_max%dim_a],a_ind,b_ind

def get_maxes(a,b,n_maxes=1):
    total_maxes=n_maxes
    sim_export={}
    sim_mat=cosine_mat(a,b)
    if np.array_equal(a,b): #remove self similiarity 
        for i in range(a.shape[1]):
            sim_mat[i,i]=0
    while n_maxes>0:
        n_maxes-=1
        s,a_ind,b_ind=get_max(sim_mat)
        sim_export[total_maxes-n_maxes]={'similarity':s,'a_ind':a_ind,'b_ind':b_ind}
        sim_mat[b_ind,a_ind]=0.
    return sim_export

def get_vectors(dcit,vector_type='d2v-d'):
    dcit.iter_type='VECTORS'
    dois=[]
    vecs=[]
    for rec in dcit:
        dois.append(rec['doi'])
        vecs.append(np.array(rec['vectors'][vector_type]))
    return np.transpose(np.array(vecs)), dois

def get_doi_sims(a_vecs,a_dois,b_vecs,b_dois,n_maxes=5):
    if len(a_vecs.shape)==1:
        single_flag=True
        a_vecs=a_vecs.reshape(a_vecs.shape[0],1)
    else:
        single_flag=False
    sims=get_maxes(a_vecs,b_vecs,n_maxes=n_maxes)
    export={}
    for ind,entry in sims.items():
        if single_flag:
            export[ind]={
                'doi':b_dois[entry['b_ind']],
                'similarity':entry['similarity']
            }
        else:
            export[ind]={
                'a_doi':a_dois[entry['a_ind']],
                'b_doi':b_dois[entry['b_ind']],
                'similarity':entry['similarity']
            }
    return export

def get_ave_sim(a,b=None):
    if b is None:
        sim_mat=cosine_mat(a,a)
        raw_sum=np.sum(sim_mat)-np.sum(sim_mat.diagonal())
        divisor=sim_mat.shape[0]**2-sim_mat.shape[0]
        return raw_sum/divisor
    else:
        sim_mat=cosine_mat(a,b)
        raw_sum = np.sum(sim_mat)
        divisor = sim_mat.shape[0]*sim_mat.shape[1]
        return raw_sum/divisor

def get_sim(v1,v2):
    return np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v1))

def get_means_and_plot(vecs,n_clusters=10,dimension=2):
    kmeans = KMeans(
        n_clusters=n_clusters,
        init='k-means++',
        max_iter=50000,
        verbose=0,
        tol=0.00000000001)
    cluster_centres =kmeans.fit(vecs).cluster_centers_
    preds=kmeans.predict(vecs)
    t = TSNE(init='pca',n_components=dimension)
    reduced_vecs = t.fit_transform(vecs+list(cluster_centres))
    colors=iter(plt.cm.rainbow(np.linspace(0,1,n_clusters)))
    fig = plt.figure()
    if dimension==3:
        ax = fig.gca(projection='3d')
    else:
        ax = fig.gca()
    for centre in range(n_clusters):
        color=next(colors)
        cluster=[]
        for dim in range(dimension):
            cluster.append([reduced_vecs[i][dim] for i in range(sample_size) if preds[i]==centre])
        if dimension==3:
            ax.scatter(cluster[0],
                cluster[1],
                cluster[2],
                 'o',
                 c=color)
            ax.scatter(reduced_vecs[sample_size+centre][0],
                 reduced_vecs[sample_size+centre][1],
                 reduced_vecs[sample_size+centre][2],
                 '*',
                 c=color)
        else:
            ax.plot(cluster[0],
                cluster[1],
                 'o',
                 c=color,
                 markersize=3)
            ax.plot(reduced_vecs[sample_size+centre][0],
                 reduced_vecs[sample_size+centre][1],
                 '*',
                 c=color,
                 markersize=10)
    plt.show()

def csv_gephi_exporter(dois,mat,filename='cam_connect.csv',thresh=0.35):
    with open(filename,'w') as f:
        masked=mat*(mat>thresh)
        f.write(';'+';'.join(dois)+'\n')
        for i in range(mat.shape[0]):
            masked[i,i]=0.
            ex=(';'.join([str(j) for j in masked[i] if j>thresh]))
            ex=dois[i]+';'+ex+'\n'
            f.write(ex)

def gexf_gephi_exporter(dois,mat,filename='cam_connect.gexf',thresh=.35):
    node_count=len(dois)
    edge_count=(np.sum(mat>thresh)-mat.shape[0])/2
    header='''<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns:viz="http:///www.gexf.net/1.1draft/viz" version="1.1" xmlns="http://www.gexf.net/1.1draft">
<meta lastmodifieddate="2010-03-03+23:44">
<creator>Gephi 0.7</creator>
</meta>
<graph defaultedgetype="undirected" idtype="string" type="static">
<nodes count="'''
    header=header+str(node_count)+'">'
    footer='''\n</edges>\n</graph>\n</gexf>'''
    with open(filename,'w') as f:
        f.write(header)
        for i in range(node_count):
            node='\n<node id="'+str(float(i))+'" label="'+dois[i]+'"/>'
            f.write(node)
        f.write('\n</nodes>\n<edges count="'+str(edge_count)+'">')
        edge_no=0
        for i in range(node_count):
            for j in range(i+1,node_count):
                if mat[i,j]>thresh:
                    f.write(
                        '\n<edge id="'+
                        str(float(edge_no))+
                        '" source="'+str(float(i))
                        +'" target="'+str(float(j))+
                        '" weight="'+str(mat[i,j])+'"/>')
                    edge_no+=1
        f.write(footer)

