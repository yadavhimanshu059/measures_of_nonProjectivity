# Using NetworkX package and conllu package
# This is baseline conditions module for ARITY BASELINE; more conditions can be added as functions
import os
from io import open
import networkx as nx
from operator import itemgetter
import random
from Measures_rand import *
import treegen as gen
import depgraph as dep
import threading

class Random_base(object):
    def __init__(self, tree):                   # tree has an abstract node=0 and real nodes =1,2,... 
        self.tree=tree                          # tree encodes the nodes and edges content in dictionary format. It uses directed graph (DiGraph) feature of networkX package. For example, nodes are encoded like this - tree.nodes={1:{form:'this',POS:'PRN'},2:{...}}   
        self.ls_rand=[]                         # Inititates a list variable for storing randomly generated trees

    def num_cross_rand(self,randtree,abs_root):               # takes a random tree and its abstract root=1000 as arguments
        comput=Compute_measures_rand(randtree,abs_root)
        ncross_random=0
        for edgex in randtree.edges:
            if comput.is_projective(edgex):                   # checks if edge is projective or not
                ncross_random += 0
            else:
                ncross_random += 1
        return ncross_random                                  # returns the number of crossing arcs in the random tree  

    def is_equal_num_crossings(self,randtree,abs_root,num_cross_real):  # takes random tree, its abstract root and no. of crossing in real tree as argument  
        flag=False
        num_cross_random=self.num_cross_rand(randtree,abs_root)
        if num_cross_random==num_cross_real:                            # checks if number of crossing are equal in real and random tree 
            flag=True
        return flag

    def rand_tree(self,n,num_cross_real,in_arity_seq,out_arity_seq):       # takes length, numCrossings and degree sequence of real tree 
        treex=nx.directed_havel_hakimi_graph(in_arity_seq, out_arity_seq)  # generates random directed graph with Havel-Hakimi algorithm 
        real_root=next(nx.topological_sort(treex))                         # finds the real root of random tree   
        abstract_root=1000                                                  
        treex.add_edge(abstract_root,real_root)                            # Adds an abstract root to random tree   
        for edgex in treex.edges:
            treex.nodes[edgex[1]]['head']=edgex[0]
        flag_PE=False
        for edgew in treex.edges:
            if treex.has_edge(edgew[1],edgew[0]):                          # Removes the trees with parllel edges 
                flag_PE=True
        if flag_PE==False:
            if self.is_equal_num_crossings(treex,abstract_root,num_cross_real):   # Checks for equal number of crossings in real and random tree
                self.ls_rand.append(treex)                                        # Adds a validated random tree to the list  

    def gen_random(self,num_cross_real,in_arity_seq,out_arity_seq):            # Takes the degree sequence and number of crossings of real tree
        n = len(self.tree.edges)
        rand_out=[]
        if n<12:                                                                    
            x=0
            while (len(self.ls_rand)==0) and x<100000:                         # Checks if list of random trees is empty and limits the attempts of generating trees     
                x=x+1
                self.rand_tree(n,num_cross_real,in_arity_seq,out_arity_seq)
                rand_out=self.ls_rand
        else:
            x=0
            flag=False
            while flag==False and x<30000:
                threadz=[]
                for i in range(x,x+50):
                    thread=threading.Thread(target=self.rand_tree,args=(n,num_cross_real,in_arity_seq,out_arity_seq), daemon=True)
                    threadz.append(thread)
                for t in threadz:
                    t.start()
                for t in threadz:
                    t.join()
                if not len(self.ls_rand)==0:
                    flag=True
                    rand_out=self.ls_rand
                else:
                    flag=False
                    x=x+50
        return rand_out                                                       # returns the list of random generated trees   
