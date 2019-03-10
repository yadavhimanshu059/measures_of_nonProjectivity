# Using NetworkX package and conllu package
import os
from io import open
from conllu import parse
import networkx as nx
from operator import itemgetter
from Measures import *
from Measures_rand import *
import random
import treegen as gen
from baseline_conditions_topology import *

directory = "F:\leebanks\pile"                   # directory containing the UD scheme tree files in CONLLU format
ud_files = []
for root, dirs, files in os.walk(directory):     
    for file in files:
        if file.endswith('train.conllu'):
            fullpath = os.path.join(root, file)
            ud_files.append(fullpath)            # creates a list of path of all files (file of each language) from the directory

for i in ud_files:                                       # reads file of each language one by one
    if 'ar' in str(i):                                   # selects a language
        lang = str(i).replace("F:\leebanks\pile", "")        
        lang=lang.replace("-ud-train.conllu", "")            # lang variable stores the language code 
        data_file = open(str(i),'r',encoding='utf-8').read()
        sentences = []
        sentences = parse(data_file)                         # parses the CONLLU format           
        sent_id=0
        print(lang)
        num_sent=0
        num_edge=0
        for sentence in sentences[0:]:
            sent_id+=1
            print(sent_id)
            if sent_id>1:
                num_sent += 1
                tree = nx.DiGraph()                              # An empty directed graph (i.e., edges are uni-directional)  
                for nodeinfo in sentence[0:]:                    # retrieves information of each node from dependency tree in UD format     
                    entry=list(nodeinfo.items())
                    if not entry[7][1]=='punct':
                        tree.add_node(entry[0][1], form=entry[1][1], lemma=entry[2][1], upostag=entry[3][1], xpostag=entry[4][1], feats=entry[5][1], head=entry[6][1], deprel=entry[7][1], deps=entry[8][1], misc=entry[9][1])                #adds node to the directed graph 
                ROOT=0
                tree.add_node(ROOT)                            # adds an abstract root node to the directed graph
                 
                for nodex in tree.nodes:
                    if not nodex==0:
                        if tree.has_node(tree.nodes[nodex]['head']):                                         # to handle disjoint trees
                            tree.add_edge(tree.nodes[nodex]['head'],nodex,drel=tree.nodes[nodex]['deprel'])       # adds edges as relation between nodes
                        if tree.nodes[nodex]['head']==0:
                            real_root=nodex
                
                n=len(tree.edges)
                if n<12 and n>1:
                    get = Compute_measures(tree)
                    num_cross_real=0
                    for edgex in tree.edges:                        
                        if get.is_projective(edgex):                   # checks if edge is projective or not
                            num_cross_real += 0
                        else:
                            num_cross_real += 1
                
                    generate = Random_base(tree)                       # initiates object for computing measures for the real tree
                    ls_random = generate.gen_random(num_cross_real)    # stores the list of random generated trees 
                    
                    if ls_random:
                        treex=ls_random[0]
                        print(ls_random)
                        print(tree.edges)
                        print(treex.edges)
                        root=1000
                        find=Compute_measures_rand(treex,root)          # initiates object for computing measures for the random tree 
                        max_arity_rand=find.arity()[0]                               # gives maximum arity present in the tree
                        avg_arity_rand=find.arity()[1]
                        projection_degree_rand=find.projection_degree(root)          # gives the projection degree of the tree i.e., size of longest projection chain in the tree
                        gap_degree_rand=find.gap_degree(root)                        # gives gap_degree of the tree
                        sent_len=0
                        for edgex in treex.edges:
                            direction_rand = find.dependency_direction(edgex)    # direction of the edge in terms of relative linear order of head and its dependent
                            dep_distance_rand=find.dependency_distance(edgex)    # gives the distance between nodes connected by an edge 
                            if find.is_projective(edgex):                   # checks if edge is projective or not
                                projectivity_rand=1
                            else:
                                projectivity_rand=0
                            edge_degree_rand=find.edge_degree(edgex)             # gives the no. of edges crossing an edge
                            endpoint_cross_rand=find.endpoint_crossing(edgex)    # no. of heads which immediately dominates the nodes which causes non-projectivity in an edge span
                            HDD_rand=find.hdd(edgex)
                            results1 = open('all_measures_real_random_shorts_ar_topology.csv','a')
                            results1.write(str(lang)+"\t"+"random"+"\t"+str(sent_id)+"\t"+str(n)+"\t"+str(max_arity_rand)+"\t"+str(avg_arity_rand)+"\t"+str(projection_degree_rand)+"\t"+str(gap_degree_rand)+"\t"+str(edgex)+"\t"+str(direction_rand)+"\t"+str(dep_distance_rand)+"\t"+str(projectivity_rand)+"\t"+str(edge_degree_rand)+"\t"+str(endpoint_cross_rand)+"\t"+str(HDD_rand)+"\n")
                            results1.close()
                        #Computes the measures for the real tree
                        max_arity_real=get.arity()[0]                               # gives maximum arity present in the tree
                        avg_arity_real=get.arity()[1]
                        projection_degree_real=get.projection_degree(0)          # gives the projection degree of the tree i.e., size of longest projection chain in the tree
                        gap_degree_real=get.gap_degree(0)                        # gives gap_degree of the tree
                        sent_len=0
                        for edgey in tree.edges:
                            direction_real = get.dependency_direction(edgey)    # direction of the edge in terms of relative linear order of head and its dependent
                            dep_distance_real=get.dependency_distance(edgey)    # gives the distance between nodes connected by an edge 
                            if get.is_projective(edgey):                   # checks if edge is projective or not
                                projectivity_real=1
                            else:
                                projectivity_real=0
                            edge_degree_real=get.edge_degree(edgey)             # gives the no. of edges crossing an edge
                            endpoint_cross_real=get.endpoint_crossing(edgey)    # no. of heads which immediately dominates the nodes which causes non-projectivity in an edge span
                            HDD_real=get.hdd(edgey)
                            results2 = open('all_measures_real_random_shorts_ar_topology.csv','a')
                            results2.write(str(lang)+"\t"+"real"+"\t"+str(sent_id)+"\t"+str(n)+"\t"+str(max_arity_real)+"\t"+str(avg_arity_real)+"\t"+str(projection_degree_real)+"\t"+str(gap_degree_real)+"\t"+str(edgey)+"\t"+str(direction_real)+"\t"+str(dep_distance_real)+"\t"+str(projectivity_real)+"\t"+str(edge_degree_real)+"\t"+str(endpoint_cross_real)+"\t"+str(HDD_real)+"\n")
                            results2.close()
                        print("\n-----------------\n"+str(tree.edges))
                        if gap_degree_real>=2:
                            results3 = open('Interesting_examples_German.csv','a')
                            results3.write('Sentence ID : '+str(sent_id)+'\n-------'+str(sentence)+"\n------------------------------------------------------\n\n")
                            results3.close()