from math import exp
import sys
from utils import write_octave_matrix
    
def compute_top_baseline(drgs):
    list_id = 0
    top_dict = dict()
    for drg in drgs:
        update_top_dict(drg, top_dict)

    return top_dict

def update_top_dict(drg, top_dict):  
    du_list = drg.discourse_units()
    for du in du_list:
        for e in du.neighbors_out():
            '''
            if e.type=="event":
                ref = e.neighbors_out(edge_type="arg")[0]
            elif e.type=="concept":
                ref = e.neighbors_out(edge_type="instance")[0]
            else:
                break
'''
            # denominator for top one probability
            top_one_denominator =  0.0  
            for edge in e.in_edges:
                top_one_denominator += exp(edge.token_index)
            
            # edge features
            for edge in e.in_edges:
                if edge.token_index > 0:
                    # top one probability (target)
                    top_one = exp(edge.token_index)/top_one_denominator
                    
                    if edge.edge_type in top_dict:
                        top_dict[edge.edge_type].append(top_one)
                    else:
                        top_dict[edge.edge_type] = [top_one]
                        
def extract_top(list_id, drg, top_dict, classifier):
    data = []
    n_edges = 0
    
    du_list = drg.discourse_units()
    for du in du_list:
        if classifier == "disler":
            for edge in du.in_edges:
               if edge.token_index > 0:
                   data.append([sum(top_dict[edge.edge_type])/len(top_dict[edge.edge_type])])
            n_edges += 1
        else:        
            for e in du.neighbors_out():
                if classifier == "eveler":
                    if (e.type=="event"):
                        ref = e.neighbors_out(edge_type="instance")[0]
                        for edge in ref.in_edges:
                           if edge.token_index > 0:
                               data.append([sum(top_dict[edge.edge_type])/len(top_dict[edge.edge_type])])
                        n_edges += 1

                elif classifier == "entler":
                    if (e.type == "concept"):
                        ref = e.neighbors_out(edge_type="instance")[0]                
                        for edge in ref.in_edges:
                           if edge.token_index > 0:
                               data.append([sum(top_dict[edge.edge_type])/len(top_dict[edge.edge_type])])
                        n_edges += 1
                        

                    
                        
    return data, n_edges

