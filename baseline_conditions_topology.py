# Using NetworkX package and conllu package
# This is baseline conditions module; more conditions can be added as functions
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
        self.ls_rand=[]

##    def crossings_in(self,tree):
##        for edge in tree.edges():
##            n1, n2 = sorted(edge)
##            for edge_ in tree.edges():
##                n1_, n2_ = sorted(edge_)
##                if not (n2_ <= n1 or n2 <= n1_ or (n1 <= n1_ and n2_ <= n2) or (n1_ <= n1 and n2 <= n2_)):
##                    yield frozenset({edge, edge_})

    def num_cross_rand(self,randtree,abs_root):              # requires random tree graph and its abstract root=1000
        comput=Compute_measures_rand(randtree,abs_root)
        ncross_random=0
        for edgex in randtree.edges:
            if comput.is_projective(edgex):                   # checks if edge is projective or not
                ncross_random += 0
            else:
                ncross_random += 1
        return ncross_random                              # returns no. of crossings in the random tree

    def is_equal_num_crossings(self,randtree,abs_root,num_cross_real):   # requires random tree, its abstract root and numCrossings in real tree  
        flag=False
        num_cross_random=self.num_cross_rand(randtree,abs_root)       
        if num_cross_random==num_cross_real:                      # checks if number of crossings are equal in real and random tree
            flag=True
        return flag

    def rand_tree(self,num_cross_real):                 # requires number of crossings from the real tree
        real_tree = nx.DiGraph()
        for edgez in self.tree.edges:
            if not edgez[0]==0:
                real_tree.add_edge(edgez[0],edgez[1])   # regenrates a dummy real tree by removing its abstract root
        edge_list=list(real_tree.edges())               
        random.shuffle(edge_list)                      # shuffles the ordering of edges of the dummy real tree 

        treex=nx.DiGraph()                              # generates an empty random tree 
        treex.add_edges_from(edge_list)                 # adds the shuffled edges to the random tree 
        real_root=next(nx.topological_sort(treex))      # finds the root of the randomly generated tree  
        abstract_root=1000
        treex.add_edge(abstract_root,real_root)         # adds an abstract root to the random tree 
        for edgex in treex.edges:
            treex.nodes[edgex[1]]['head']=edgex[0]
                
        if self.is_equal_num_crossings(treex,abstract_root,num_cross_real):  # matches the no. of crossings in the real and random tree
            self.ls_rand.append(treex)                  # adds the random tree to the list

    def gen_random(self,num_cross_real):              # requires numbr of crossings from the real tree
        n = len(self.tree.edges)
        rand_out=[]
        if n<12:
            x=0
            while (len(self.ls_rand)==0) and x<60000:     # checks if list of random trees is ampty and limits the generating attempts 
                x=x+1
                self.rand_tree(num_cross_real)
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
        return rand_out                           # returns the list of random trees
