# Using NetworkX package and conllu package
import os
from io import open
from conllu import parse
import networkx as nx
from operator import itemgetter
import matplotlib.pyplot as plt
from Measures import *
from Measures_rand import *
import random
import treegen as gen
from baseline_conditions import *

results1=open('all_measures_random_v3.0_7thnov_hi.csv','a')               
results2=open('range_measures__random_v3.0_7thnov_hi.csv','a')
results3=open('arity_hist_random_v3.0_7thnov_hi.csv','a')
results4=open('projdegree_hist_random_v3.0_7thnov_hi.csv','a')
results5=open('gapdegree_hist_random_v3.0_7thnov_hi.csv','a')

directory = "F:\leebanks\pile"                   # directory containing the UD scheme tree files in CONLLU format
ud_files = []
for root, dirs, files in os.walk(directory):     
    for file in files:
        if file.endswith('train.conllu'):
            fullpath = os.path.join(root, file)
            ud_files.append(fullpath)            # creates a list of path of all files (file of each language) from the directory

for i in ud_files:                                       # reads file of each language one by one
    if 'hi' in str(i):
        lang = str(i).replace("F:\leebanks\pile", "")        
        lang=lang.replace("-ud-train.conllu", "")            # lang variable stores the language code 
        data_file = open(str(i),'r',encoding='utf-8').read()
        sentences = []
        sentences = parse(data_file)                         # parses the CONLLU format           
        sent_id=0
        print(lang)
        gapD_0=0
        gapD_1=0
        gapD_2=0
        gapD_3=0
        gapD_4=0
        gapD_4p=0
        edgeD_0=0
        edgeD_1=0
        edgeD_2=0
        edgeD_3=0
        edgeD_4=0
        edgeD_4p=0
        endp_0=0
        endp_1=0
        endp_2=0
        endp_3=0
        endp_3p=0
        proj=0
        nonproj=0
        num_sent=0
        num_edge=0
        for sentence in sentences[0:]:
            sent_id+=1
            print(sent_id)
            num_sent += 1
            tree = nx.DiGraph()                              # An empty directed graph (i.e., edges are uni-directional)  
            for nodeinfo in sentence[0:]:                    # retrieves information of each node from dependency tree in UD format     
                entry=list(nodeinfo.items())
                tree.add_node(entry[0][1], form=entry[1][1], lemma=entry[2][1], upostag=entry[3][1], xpostag=entry[4][1], feats=entry[5][1], head=entry[6][1], deprel=entry[7][1], deps=entry[8][1], misc=entry[9][1])                #adds node to the directed graph 
            ROOT=0
            tree.add_node(ROOT)                            # adds an abstract root node to the directed graph
             
            for nodex in tree.nodes:
                if not nodex==0:
                    if tree.has_node(tree.nodes[nodex]['head']):                                         # to handle disjoint trees
                        tree.add_edge(tree.nodes[nodex]['head'],nodex,drel=tree.nodes[nodex]['deprel'])       # adds edges as relation between nodes
            n=len(tree)-1            
            get = Compute_measures(tree)
            num_cross_real=0
            for edgex in tree.edges:
                if not (tree.edges[edgex]['drel']=='root' or tree.edges[edgex]['drel']=='punct'):
                    if get.is_projective(edgex):                   # checks if edge is projective or not
                        num_cross_real += 0
                    else:
                        num_cross_real += 1
            
            generate = Random_base(tree)
            ls_random = generate.gen_random(num_cross_real)
            if ls_random:
                random.shuffle(ls_random)
                treex=ls_random[0]
                root=1000
                find=Compute_measures_rand(treex,root)
                print(str(tree.edges)+"\n--------------\nProjective: "+str(treex.edges)+"\n\n##############################\n\n")
                max_arity=find.arity()[0]                               # gives maximum arity present in the tree
                avg_arity=find.arity()[1]
                projection_degree=find.projection_degree(root)          # gives the projection degree of the tree i.e., size of longest projection chain in the tree
                #print(projection_degree)
                gap_degree=find.gap_degree(root)                        # gives gap_degree of the tree
                sent_len=0
                
                for edgex in treex.edges:
                    #if not (tree.edges[edgex]['drel']=='root' or tree.edges[edgex]['drel']=='punct'):
                    direction = find.dependency_direction(edgex)    # direction of the edge in terms of relative linear order of head and its dependent
                    dep_distance=find.dependency_distance(edgex)    # gives the distance between nodes connected by an edge 
                    if find.is_projective(edgex):                   # checks if edge is projective or not
                        projectivity=1
                    else:
                        projectivity=0
                    edge_degree=find.edge_degree(edgex)             # gives the no. of edges crossing an edge
                    endpoint_cross=find.endpoint_crossing(edgex)    # no. of heads which immediately dominates the nodes which causes non-projectivity in an edge span
                    HDD=find.hdd(edgex)
                    results1.write(str(lang)+"\t"+str(sent_id)+"\t"+str(n)+"\t"+str(max_arity)+"\t"+str(avg_arity)+"\t"+str(projection_degree)+"\t"+str(gap_degree)+"\t"+str(edgex)+"\t"+str(direction)+"\t"+str(dep_distance)+"\t"+str(projectivity)+"\t"+str(edge_degree)+"\t"+str(endpoint_cross)+"\t"+str(HDD)+"\n")

                    num_edge += 1
                    if edge_degree==0:
                        edgeD_0 += 1
                    elif edge_degree==1:
                        edgeD_1 += 1
                    elif edge_degree==2:
                        edgeD_2 += 1
                    elif edge_degree==3:
                        edgeD_3 += 1
                    elif edge_degree==4:
                        edgeD_4 += 1
                    else:
                        edgeD_4p += 1

                    if endpoint_cross==0:
                        endp_0 += 1
                    elif endpoint_cross==1:
                        endp_1 += 1
                    elif endpoint_cross==2:
                        endp_2 += 1
                    elif endpoint_cross==3:
                        endp_3 += 1
                    else:
                        endp_3p += 1

                    if projectivity==0:
                        nonproj += 1
                    else:
                        proj += 1

                if gap_degree==0:
                    gapD_0 += 1
                elif gap_degree==1:
                    gapD_1 += 1
                elif gap_degree==2:
                    gapD_2 += 1
                elif gap_degree==3:
                    gapD_3 += 1
                elif gap_degree==4:
                    gapD_4 += 1
                else:
                    gapD_4p += 1


                arity_hist=find.arity()[3]
                projdegree_hist=find.projD_hist()
                gap_hist=find.gapD_hist()
                
                for ar_val in arity_hist.keys():
                    results3.write(str(lang)+"\t"+str(sent_id)+"\t"+str(ar_val)+"\t"+str(arity_hist[ar_val])+"\n")
                for proj_val in projdegree_hist.keys():
                    results4.write(str(lang)+"\t"+str(sent_id)+"\t"+str(proj_val)+"\t"+str(projdegree_hist[proj_val])+"\n")
                for gap_val in gap_hist.keys():
                    results5.write(str(lang)+"\t"+str(sent_id)+"\t"+str(gap_val)+"\t"+str(gap_hist[gap_val])+"\n")

        results2.write(str(lang)+"\t"+str((edgeD_0/num_edge)*100)+"\t"+str((edgeD_1/num_edge)*100)+"\t"+str((edgeD_2/num_edge)*100)+"\t"+str((edgeD_3/num_edge)*100)+"\t"+str((edgeD_4/num_edge)*100)+"\t"+str((edgeD_4p/num_edge)*100)+"\t"+str((gapD_0/num_sent)*100)+"\t"+str((gapD_1/num_sent)*100)+"\t"+str((gapD_2/num_sent)*100)+"\t"+str((gapD_3/num_sent)*100)+"\t"+str((gapD_4/num_sent)*100)+"\t"+str((gapD_4p/num_sent)*100)+"\t"+str((endp_0/num_edge)*100)+"\t"+str((endp_1/num_edge)*100)+"\t"+str((endp_2/num_edge)*100)+"\t"+str((endp_3/num_edge)*100)+"\t"+str((endp_3p/num_edge)*100)+"\t"+str((proj/num_edge)*100)+"\t"+str((nonproj/num_edge)*100)+"\n")
                        
results1.close()
results2.close()
results3.close()
results4.close()
results5.close()
