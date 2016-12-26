import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import cairo
import igraph
from igraph import *
from scipy import stats as sci


# params
filepath = "C:/Python27_64/Scripts/archive_pickle_projects"
is_directed = False
is_projects = True

do_degree_analysis = False
do_strength_analysis = False
do_diameter_analysis = False
do_analytical_analysis = False
do_corrolation_analysis = False
do_box_plot_analysis = True
do_graph_cluster_analysis = True
do_page_rank_analysis = False

use_reverse = True
look_at_languages = True

# utility

common_words = ["the","of","and","a","to","in","is","you","that","it","he","was","for","on","are","as","with","his","they","I","at","be","this","have","from","or","one","had","by","word","but","not","what","all","were","we","when","your","can","said","there","use","an","each","which","she","do","how","their","if","will","up","other","about","out","many","then","them","these","so","some","her","would","make","like","him","into","time","has","look","two","more","write","go","see","number","no","way","could","people","my","than","first","water","been","call","who","oil","its","now","find","long","down","day","did","get","come","made","may","part"]


# read and initialize graph
print("0...initialize and read:")
g1 = Graph()
g1 = g1.Read_Pickle(filepath)


#pre-process graph

count = 0
if(is_projects):    
    for edge in g1.es:
        v_src = edge.source
        v_tgt = edge.target
        e_oldw = edge["weight"]
        edge["weight"]=(e_oldw/float(g1.vs[v_src]["size"]) + e_oldw/float(g1.vs[v_tgt]["size"]))/2
        count+=1

g1.vs["degree"] = g1.degree()
g1.vs["strength"] = g1.strength(weights=g1.es["weight"])
g1.vs["pagerank"] = g1.pagerank(vertices=None, directed=False, damping=0.85, weights=g1.es["weight"])


if(do_analytical_analysis):
    print("                                    ")
    print("                                    ")
    print("1A...degree analytical analysis (top 5 or bottom):")
    degrees = []
    for degree in g1.degree():
        degrees.append(degree)
    degrees.sort(cmp=None, key=None, reverse=use_reverse)
    count = 0
    for degree in degrees[:5]:
        vertex = g1.vs.select(_degree = degree)
        name = vertex["name"]
        if(is_projects):
            language = vertex["language"]
            watchers = vertex["watchers"]
            forks = vertex["forks"]
            size = vertex["size"]
            strength = vertex["strength"]
            pagerank = vertex["pagerank"]

            print("-------"+str(count)+"--------")
            print(degree)
            print(name)
            print(language)
            print(watchers)
            print(forks)
            print(size)
            print(strength)
            print(pagerank)
            count+=1
        else:
            followers = vertex["followers"]
            following = vertex["following"]
            strength = vertex["strength"]
            pagerank = vertex["pagerank"]
            print("-------"+str(count)+"--------")
            print(degree)
            print(name)
            print(followers)
            print(following)
            print(strength)
            print(pagerank)
            count+=1
            
    print("                                    ")
    print("                                    ")
    print("1B... strength analytical analysis (top 5 or bottom):")
    strengths = []
    for strength in g1.strength(weights=g1.es["weight"]):
        strengths.append(strength)
    strengths.sort(cmp=None, key=None, reverse=use_reverse)
    count = 0
    for strength in strengths[:5]:
        vertex = g1.vs.select(strength = strength)
        name = vertex["name"]
        if(is_projects):
            language = vertex["language"]
            watchers = vertex["watchers"]
            forks = vertex["forks"]
            size = vertex["size"]
            degree = vertex["degree"]
            pagerank = vertex["pagerank"]

            print("-------"+str(count)+"--------")
            print(strength)
            print(name)
            print(language)
            print(watchers)
            print(forks)
            print(size)
            print(degree)
            print(pagerank)
            count+=1
        else:
            followers = vertex["followers"]
            following = vertex["following"]
            degree = vertex["degree"]
            pagerank = vertex["pagerank"]
            print("-------"+str(count)+"--------")
            print(strength)
            print(name)
            print(followers)
            print(following)
            print(degree)
            count+=1

    print("                                    ")
    print("                                    ")
    print("1C... pagerank analytical analysis (top 5 or bottom):")
    pageranks = []
    for pagerank in g1.pagerank(vertices=None, directed=False, damping=0.85, weights=g1.es["weight"]):
        pageranks.append(pagerank)
    pageranks.sort(cmp=None, key=None, reverse=use_reverse)
    count = 0
    for pagerank in pageranks[:5]:
        vertex = g1.vs.select(pagerank = pagerank)
        name = vertex["name"]
        if(is_projects):
            language = vertex["language"]
            watchers = vertex["watchers"]
            forks = vertex["forks"]
            size = vertex["size"]
            strength = vertex["strength"]

            print("-------"+str(count)+"--------")
            print(pagerank)
            print(name)
            print(language)
            print(watchers)
            print(forks)
            print(size)
            print(degree)
            print(strength)
            count+=1
        else:
            followers = vertex["followers"]
            following = vertex["following"]
            degree = vertex["degree"]
            strength = vertex["strength"]
            print("-------"+str(count)+"--------")
            print(pagerank)
            print(name)
            print(followers)
            print(following)
            print(degree)
            print(strength)
            count+=1            
    
        
if(do_degree_analysis):
    print("                                    ")
    print("                                    ")
    print("2...degree distribution analysis:")
    plt.figure()
    plt.hist(g1.degree(),bins=50)
    plt.show()


if(do_strength_analysis):
    print("                                    ")
    print("                                    ")
    print("3...strength distribution analysis:")
    plt.figure()
    plt.hist(g1.strength(weights=g1.es["weight"]),bins=50)
    plt.show()

if(do_page_rank_analysis):
    print("                                    ")
    print("                                    ")
    print("7...page rank analysis:")
    plt.figure()
    plt.hist(g1.pagerank(vertices=None, directed=False, damping=0.85, weights=g1.es["weight"]),bins=50)
    plt.show()
          
if(do_corrolation_analysis):
    print("                                    ")
    print("                                    ")
    print("5A...correlation analysis (degree vs strength):")
    result = np.correlate(g1.degree(), g1.strength())
    print(result)
    if(is_projects):
        print("5B...correlation analysis (strength vs size):")
        result = np.corrcoef(g1.strength(), g1.vs["size"])
        print(result)
        print("5C...correlation analysis (strength vs watchers):")
        result = np.corrcoef(g1.strength(), g1.vs["watchers"])
        print(result)
        print("5D...correlation analysis (strength vs forks):")
        result = np.corrcoef(g1.strength(), g1.vs["forks"])
        print(result)
    else:
        print("5B...correlation analysis (strength vs followers):")
        result = np.corrcoef(g1.strength(), g1.vs["followers"])
        print(result)
        print("5C...correlation analysis (strength vs following):")
        result = np.corrcoef(g1.strength(), g1.vs["following"])
        print(result)

if(do_box_plot_analysis and is_projects):
    print("                                    ")
    print("                                    ")
    print("6...boxplot analysis (categorical correlation):")
    count = {}
    for vertex in g1.vs.select():
        if(vertex["language"] in count and count[vertex["language"]] is not None):
            count[vertex["language"]].append(float(vertex["strength"]))
        elif(vertex["language"] not in count):
            count[vertex["language"]] = [float(vertex["strength"])]

    c = 0
    for key,val in count.items():
        if(len(val) > 3):
            w, p_val = sci.shapiro(val)
            print(c)
            print("pvalue:"+str(p_val))
            print("mean:"+str(np.mean(val)))
            print("langage:"+key)
            print("# of points:"+str(len(val)))
            print("-------")
        c+=1

    x = count.keys()
    y = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]   
    plt.figure()
    plt.boxplot(count.values())
    plt.xticks(y,x)
    plt.show()
        
    f_val, p_val = sci.f_oneway(count.values()[0],count.values()[2],
                                count.values()[3],count.values()[4],count.values()[5],
                                count.values()[6],count.values()[7],
                                count.values()[9],count.values()[11],
                                count.values()[12])
    print("For ANOVA All: "+ str(p_val))

    f_val, p_val = sci.f_oneway(count.values()[5],count.values()[11])
    print("For ANOVA javascript,C++: "+ str(p_val))

    f_val, p_val = sci.ranksums(count.values()[5],count.values()[11])
    print("For Ranksum javascript,C++: "+ str(p_val))
    
if(do_graph_cluster_analysis):
    print("                                    ")
    print("                                    ")
    print("7...graph cluster analysis:")
    use_cim = True
    use_cle = False
    use_clp = False
    use_cml = False
    
    if(use_cim):
        clust = g1.community_infomap(edge_weights=g1.es["weight"])
    if(use_cle):
        clust = g1.community_leading_eigenvector(clusters=90,weights=g1.es["weight"])
    if(use_clp):
        clust = g1.community_label_propagation(weights=g1.es["weight"])
    if(use_cml):
        clust = g1.community_multilevel(weights=g1.es["weight"], return_levels=False)

    modularity_score = g1.modularity(membership=clust,weights=g1.es["weight"])
    cont_graph = clust.cluster_graph(combine_vertices=True,combine_edges=True)
    sub_graphs = clust.subgraphs()
    '''
    count = 0
    for graph in sub_graphs:
        visual_style = {}
        visual_style["vertex_size"] = 2
        visual_style["vertex_label"] = graph.vs["name"]
        visual_style["vertex_color"] = "red"
        visual_style["edge_label"] = graph.es["weight"]
        visual_style["edge_width"] = 1 
        visual_style["layout"] = g1.layout("kk")
        visual_style["bbox"] = (1000, 1000)
        visual_style["margin"] = 100
        filepath = "visual_group_"+str(count)+".pdf"
        igraph.plot( graph, filepath, **visual_style )

        if(is_projects and look_at_languages):
            dist_count = {}
            for vertex in graph.vs.select():
                if(vertex["language"] in  dist_count and dist_count[vertex["language"]] is not None):
                    dist_count[vertex["language"]] += 1
                elif(vertex["language"] not in dist_count):
                    dist_count[vertex["language"]] = 1             
        elif(is_projects):
            dist_count = {}
            for vertex in graph.vs.select():
                words = vertex["description"].split()
                for word in words:
                    word = word.lower()
                    if(word in dist_count and word not in common_words and dist_count[word] is not None):
                        dist_count[word] += 1
                    elif(vertex["language"] not in dist_count and word not in common_words):
                        dist_count[word] = 1

            for k,v in dist_count.items():
                if(v < np.median(dist_count.values())):
                    dist_count.pop(k, None)
        else:
            dist_count = {}
            for vertex in graph.vs.select():
                if(vertex["location"] in dist_count and dist_count[vertex["location"]] is not None):
                    dist_count[vertex["location"]] += 1
                elif(vertex["location"] not in dist_count):
                    dist_count[vertex["location"]] = 1

            for k,v in dist_count.items():
                if(v <= np.median(dist_count.values())):
                    dist_count.pop(k, None)
        
        pos = np.arange(len(dist_count.keys()))
        freq = dist_count.values()
        width = 1.0
        ax = plt.axes()
        ax.set_xticks(pos + (width / 2))
        ax.set_xticklabels(dist_count.keys())
        plt.bar(pos,freq,width,color='r')
        filepath = "dist_users_"+str(count)+".pdf"
        plt.show()
        
        count+=1
    '''
    visual_style = {}
    visual_style["vertex_size"] = 10
    visual_style["vertex_color"] = "red"
    visual_style["edge_width"] = 1 
    visual_style["layout"] = cont_graph.layout("kk")
    visual_style["bbox"] = (1000, 1000)
    visual_style["margin"] = 100

    igraph.plot( cont_graph, "visual_contracted.pdf", **visual_style )
    print(modularity_score)
    
if(do_diameter_analysis):
    print("                                    ")
    print("                                    ")
    print("8A...diameter analysis (weighted):")
    farthest_points = g1.farthest_points(directed=False,unconn=True,weights=g1.es["weight"])
    diameter = g1.get_diameter(directed=is_directed,unconn=True,weights=g1.es["weight"])
    print(farthest_points)
    print(diameter)

    print("8B...diameter analysis (un-weighted):")
    farthest_points = g1.farthest_points(directed=False,unconn=True,weights=None)
    diameter = g1.get_diameter(directed=is_directed,unconn=True,weights=None)
    print(farthest_points)
    print(diameter)
