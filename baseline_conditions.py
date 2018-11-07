# Using NetworkX package and conllu package
# This is baseline conditions module; more conditions can be added as functions
import os
from io import open
import networkx as nx
from operator import itemgetter
from random import shuffle
from Measures_rand import *
import treegen as gen

class Random_base(object):
    def __init__(self, tree):                   # tree has an abstract node=0 and real nodes =1,2,... 
        self.tree=tree                          # tree encodes the nodes and edges content in dictionary format. It uses directed graph (DiGraph) feature of networkX package. For example, nodes are encoded like this - tree.nodes={1:{form:'this',POS:'PRN'},2:{...}}   
    def is_same_tree(self,random_tree):              # tree has an abstract node=1000 and real nodes =0,1,2,... 
        flag=False
        dummy1 = nx.DiGraph()                                   # Draws dummy trees to compare the configuration of random and real language tree
        for edgex in random_tree.edges:
            if not edgex[0]==1000:
                dummy1.add_edge(edgex[0]+1,edgex[1]+1)    # this tree has nodenames similar to real tree i.e., 1,2,3...
                
        dummy2 = nx.DiGraph()
        for edgex in self.tree.edges:
            if not edgex[0]==0:
                dummy2.add_edge(edgex[0],edgex[1])        # real langauge tree with nodes i.e., 1,2,3....

        if set(dummy1.edges)==set(dummy2.edges):
            flag=True
        else:
            flag=flag
        return flag

    def is_equal_num_crossings(self,randtree,abs_root,num_cross_real):
        flag=False
        find = Compute_measures_rand(randtree,abs_root)
        num_cross_rand=0
        for edgex in randtree.edges:
            if not find.is_projective(edgex):                   # checks if edge is projective or not
                num_cross_rand += 1
        if num_cross_real==num_cross_rand:
            flag=True
        return flag

    def gen_random(self,num_cross_real):
        ls_rand_trees=[]
        n = len(self.tree)-1
        rand_num=0
        while rand_num==0:
            code=gen.random_pruefer_code(n)
            all_rand_trees = gen.directed_trees(gen.tree_from_pruefer_code(code))
            for treex in all_rand_trees:
                real_root=next(nx.topological_sort(treex))
                abstract_root=1000
                treex.add_edge(abstract_root,real_root)
                for edgex in treex.edges:
                    treex.nodes[edgex[1]]['head']=edgex[0]
                if not self.is_same_tree(treex):
                    if self.is_equal_num_crossings(treex,abstract_root,num_cross_real):
                        ls_rand_trees.append(treex)
            rand_num=len(ls_rand_trees)
        return ls_rand_trees
