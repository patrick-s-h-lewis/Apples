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
    sim_mat=cosine_mat(a,b)
    while n_maxes>0:
        n_maxes-=1
        s,a_ind,b_ind=get_max(sim_mat)
        print('sim: '+str(s) + ' a_ind '+str(a_ind) + ' b_ind ' + str(b_ind))
        sim_mat[b_ind,a_ind]=0.

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
    reduced_vecs = t.fit_transform(list(vecs)+list(cluster_centres))
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
