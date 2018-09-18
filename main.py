# Using NetworkX package and conllu package
import os
from io import open
from conllu import parse
import networkx as nx
from operator import itemgetter
import matplotlib.pyplot as plt
from Measures import *


results1=open('Hindi_all_measures.csv','a')               

directory = "F:\leebanks\pile"                   # directory containing the UD scheme tree files in CONLLU format
ud_files = []
for root, dirs, files in os.walk(directory):     
    for file in files:
        if file.endswith('train.conllu'):
            fullpath = os.path.join(root, file)
            ud_files.append(fullpath)            # creates a list of path of all files (file of each language) from the directory

for i in ud_files:                                       # reads file of each language one by one 
    lang = str(i).replace("F:\leebanks\pile", "")        
    lang=lang.replace("-ud-train.conllu", "")            # lang variable stores the language code 
    data_file = open(str(i),'r',encoding='utf-8').read()
    sentences = parse(data_file)                         # parses the CONLLU format           
    sent_id=0
    for sentence in sentences[0:]:
        sent_id+=1
        tree = nx.DiGraph()                              # An empty directed graph (i.e., edges are uni-directional)  
        for nodeinfo in sentence[0:]:                    # retrieves information of each node from dependency tree in UD format     
            entry=list(nodeinfo.items())
            tree.add_node(entry[0][1], form=entry[1][1], lemma=entry[2][1], upostag=entry[3][1], xpostag=entry[4][1], feats=entry[5][1], head=entry[6][1], deprel=entry[7][1], deps=entry[8][1], misc=entry[9][1])                #adds node to the directed graph 
        ROOT=0
        tree.add_node(ROOT)                            # adds an abstract root node to the directed graph
        for nodex in tree.nodes:
            if not nodex==0:
                tree.add_edge(tree.nodes[nodex]['head'],nodex,drel=tree.nodes[nodex]['deprel'])       # adds edges as relation between nodes 
        
        get = Compute_measures(tree)                           # creates a instance of 'Compute_measure' class which takes directed acyclic graph as input and returns several formal measures  
        max_arity=get.arity()[0]                               # gives maximum arity present in the tree
        projection_degree=get.projection_degree(ROOT)          # gives the projection degree of the tree i.e., size of longest projection chain in the tree
        gap_degree=get.gap_degree(ROOT)                        # gives gap_degree of the tree
        for edgex in tree.edges:
            if not (tree.edges[edgex]['drel']=='root' or tree.edges[edgex]['drel']=='punct'):
                direction = get.dependency_direction(edgex)    # direction of the edge in terms of relative linear order of head and its dependent
                dep_distance=get.dependency_distance(edgex)    # gives the distance between nodes connected by an edge 
                if get.is_projective(edgex):                   # checks if edge is projective or not
                    projectivity=1
                else:
                    projectivity=0
                edge_degree=get.edge_degree(edgex)             # gives the no. of edges crossing an edge
                endpoint_cross=get.endpoint_crossing(edgex)    # no. of heads which immediately dominates the nodes which causes non-projectivity in an edge span  

                results1.write(str(lang)+"\t"+str(sent_id)+"\t"+str(max_arity)+"\t"+str(projection_degree)+"\t"+str(gap_degree)+"\t"+str(edgex)+"\t"+str(direction)+"\t"+str(dep_distance)+"\t"+str(projectivity)+"\t"+str(endpoint_cross)+"\n")
results1.close()
