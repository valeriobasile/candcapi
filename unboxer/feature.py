# feature extraction

import sys
from utils import *
import math
from random import random, shuffle
from utils import accepted_relations
from itertools import permutations

__dir__ = os.path.dirname(os.path.abspath(__file__))

sys.stderr.write('loading baseline frequencies... ')
baseline_ent = dict()
fd_freq = open('baseline_dict_ent.txt')
for line in fd_freq:
    key = tuple(line[:-1].split("\t")[0].split(' '))
    freq = eval(line[:-1].split("\t")[1])
    if not len(key) in baseline_ent:
        baseline_ent[len(key)] = dict()
    baseline_ent[len(key)][key]=freq
fd_freq.close()

baseline_eve = dict()
fd_freq = open('baseline_dict_eve.txt')
for line in fd_freq:
    key = tuple(line[:-1].split("\t")[0].split(' '))
    freq = eval(line[:-1].split("\t")[1])
    if not len(key) in baseline_eve:
        baseline_eve[len(key)] = dict()
    baseline_eve[len(key)][key]=freq
fd_freq.close()
sys.stderr.write('done\n')
            

# read bigram language model
def read_bigrams(ngrams):
    sys.stderr.write("reading bigram language model...\n")
    bigrams = dict()

    fd = open(ngrams)

    tot_freq = 0
    for line in fd:
        fields = line[:-1].split("\t")
        freq = eval(fields[0])
        tot_freq += freq
        if fields[1] == "{ARG}":
            first = ""
        else:
            first = fields[1]
        if fields[2] == "{ARG}":
            second = ""
        else:
            second = fields[2]
        bigrams[(first,second)]=freq
    for k,v in bigrams.iteritems():
        bigrams[k] = float(v)/float(tot_freq)
    fd.close()
    return bigrams

def extract(c, list_id, drg, lists, features, affix_file=None):
    if c == 'eve':
        return extract_eve(list_id, drg, lists, features, affix_file)
    if c == 'ent':
        return extract_ent(list_id, drg, lists, features, affix_file)
    if c == 'dis':
        return extract_dis(list_id, drg, lists, features, affix_file)
                
def extract_eve(list_id, drg, lists, features, affix_file=None):
    structure = ("structure" in features)
    semantics = ("semantics" in features)
    tense = ("tense" in features)
    
    if affix_file !=None:
        drg.add_affixes(affix_file)
        
    data_bin = []
    data_ler = []
    data_aff = []
    n_events = 0

    # extract features for EVE-* classifiers
    for e in drg.edges:
        if (e.edge_type=="event"):
            data_bin.append([])
            data_ler.append([])
            data_aff.append([])
            event_ref = e.to_node.neighbors_out(edge_type="instance")[0]     
            
            in_edge_number = 0
            for ie in event_ref.in_edges:
                if ie.token_index > 0:
                    in_edge_number += 1
                    
            node_features_bin = []
            node_features_ler = [list_id+n_events, in_edge_number]
            node_features_aff = []

            # node features
            if semantics:
                event_symbol_hypernyms = extract_event_symbol_hypernyms(event_ref, lists)
                named_type = extract_named_type(event_ref, lists)
                node_features_bin += event_symbol_hypernyms + named_type
                node_features_ler += event_symbol_hypernyms + named_type
                node_features_aff += event_symbol_hypernyms + named_type
            if tense:
                event_tense = extract_event_tense(event_ref, lists)
                node_features_bin += event_tense
                node_features_ler += event_tense
                node_features_aff += event_tense
				
            # baseline features
            baseline = extract_baseline(event_ref, baseline_eve)
            
            # edge features
            for edge in event_ref.in_edges:
                edge_features_bin = []
                edge_features_ler = []
                edge_features_aff = []
                
                # baseline features
                if edge.token_index > 0:
                    baseline_feature = baseline.pop()
                else:
                    baseline_feature = 0
                edge_features_ler += [baseline_feature]
                
                if structure:  
                    punctuation = extract_punctuation(edge, lists)
                    surface = extract_surface(edge, lists)
                    node_type = extract_node_type(edge, lists)
                    binary_relations = extract_binary_relations(edge, lists)
                    discourse_unit_types = extract_discourse_unit_types(edge, lists)
                    operator = extract_operator(edge, lists)
                    related_ref_type = extract_related_ref_type(edge, lists)
                    edge_type = extract_edge_type(edge, lists)
                    
                    edge_features_bin += edge_type + punctuation + surface + node_type + binary_relations + discourse_unit_types + related_ref_type + operator
                    edge_features_ler += edge_type + punctuation + surface + node_type + binary_relations + discourse_unit_types + related_ref_type + operator
                    edge_features_aff += edge_type + punctuation + surface + node_type + binary_relations + discourse_unit_types + related_ref_type + operator

                if semantics:
                    related_concept_hypernyms = extract_related_concept_hypernyms(edge, lists)
                    edge_features_bin += related_concept_hypernyms
                    edge_features_ler += related_concept_hypernyms
                    edge_features_aff += related_concept_hypernyms
                    
                if edge.token_index > 0:
                    edge_features_bin += [1]
                    edge_features_ler += [edge.token_index]
                    edge_features_aff += [edge.affix]
                    data_ler[-1].append(node_features_ler + edge_features_ler)
                    data_aff[-1].append(node_features_aff + edge_features_aff)
                else:
                    edge_features_bin += [-1]
                data_bin[-1].append(node_features_bin + edge_features_bin)
            n_events += 1           
    return data_bin, data_ler, data_aff, n_events

def extract_ent(list_id, drg, lists, features, affix_file=None):
    structure = ("structure" in features)
    semantics = ("semantics" in features)
    cardinality = ("cardinality" in features)
    
    data_ler = []
    data_bin = []
    data_aff = []
    n_entities = 0
    
    if affix_file !=None:
        drg.add_affixes(affix_file)

    # extract features for ENT-* classifiers
    for e in drg.edges:
        if (e.edge_type=="concept"):
            data_ler.append([])
            data_bin.append([])
            data_aff.append([])
            try:
                entity_ref = e.to_node.neighbors_out(edge_type="instance")[0] 
            except:
                continue
            
            in_edge_number = 0
            for ie in entity_ref.in_edges:
                if ie.token_index > 0:
                    in_edge_number += 1
            node_features_bin = []
            node_features_ler = [list_id+n_entities, in_edge_number]
            node_features_aff = []
            
            # node features
            if semantics:
                entity_symbol_hypernyms = extract_entity_symbol_hypernyms(entity_ref, lists)
                named_type = extract_named_type(entity_ref, lists)
                node_features_bin += entity_symbol_hypernyms + named_type
                node_features_ler += entity_symbol_hypernyms + named_type
            	node_features_aff += entity_symbol_hypernyms + named_type

            if cardinality:
                entity_cardinality = extract_cardinality(entity_ref, lists)
                node_features_bin += entity_cardinality
                node_features_ler += entity_cardinality
            	node_features_aff += entity_cardinality

            # baseline features
            baseline = extract_baseline(entity_ref, baseline_ent)
                                	
            # edge features
            for edge in entity_ref.in_edges:
                edge_features_bin = []
                edge_features_ler = []
                edge_features_aff = []
                
                # baseline features
                if edge.token_index > 0:
                    baseline_feature = baseline.pop()
                else:
                    baseline_feature = 0
                edge_features_ler += [baseline_feature]
                
                if structure:
                    punctuation = extract_punctuation(edge, lists)
                    surface = extract_surface(edge, lists)
                    node_type = extract_node_type(edge, lists)
                    binary_relations = extract_binary_relations(edge, lists)
                    discourse_unit_types = extract_discourse_unit_types(edge, lists)
                    operator = extract_operator(edge, lists)
                    related_ref_type = extract_related_ref_type(edge, lists)
                    edge_type = extract_edge_type(edge, lists)
                    
                    edge_features_bin += edge_type + punctuation + surface + node_type + binary_relations + discourse_unit_types + related_ref_type + operator
                    edge_features_ler += edge_type + punctuation + surface + node_type + binary_relations + discourse_unit_types + related_ref_type + operator
                    edge_features_aff += edge_type + punctuation + surface + node_type + binary_relations + discourse_unit_types + related_ref_type + operator

                if semantics:
                    related_concept_hypernyms = extract_related_concept_hypernyms(edge, lists)
                    edge_features_bin += related_concept_hypernyms
                    edge_features_ler += related_concept_hypernyms
                    edge_features_aff += related_concept_hypernyms 

                if edge.token_index > 0:
                    edge_features_bin += [1]
                    edge_features_ler += [edge.token_index]
                    edge_features_aff += [edge.affix]
                    data_ler[-1].append(node_features_ler + edge_features_ler)
                    data_aff[-1].append(node_features_aff + edge_features_aff)
                else:
                    edge_features_bin += [-1]
                data_bin[-1].append(node_features_bin + edge_features_bin)
            n_entities += 1
                    
    return data_bin, data_ler, data_aff, n_entities

def extract_dis(list_id, drg, lists, features):
    structure = ("structure" in features)
    semantics = ("semantics" in features)
     
    data_ler = []
    data_bin = []
    data_aff = []
    n_du = 0
    
    # extract features for DIS-* classifiers
    for e in drg.edges:
        if (e.edge_type=="referent"):
            data_ler.append([])
            data_bin.append([])
            du = e.from_node
            node_features_bin = []
            node_features_ler = [list_id+n_du]
            
            # edge features
            for edge in du.in_edges:
                edge_features_bin = []
                edge_features_ler = []
                punctuation = extract_punctuation(edge, lists)
                surface = extract_surface(edge, lists)
                du_type = binary_vector([edge.edge_type], lists["du_types"])
                edge_features_bin += punctuation + surface + du_type
                edge_features_ler += punctuation + surface + du_type

                if edge.token_index > 0:
                    edge_features_bin += [1]
                    edge_features_ler += [edge.token_index]
                    data_ler[-1].append(node_features_ler + edge_features_ler)
                else:
                    edge_features_bin += [-1]
                data_bin[-1].append(node_features_bin + edge_features_bin)
            n_du += 1
    return data_bin, data_ler, data_aff, n_du
    
def extract_baseline(ref, baseline_dict):
    baseline = []
    nonzero_edges = []
    for ie in ref.in_edges:
        if ie.token_index > 0:
            nonzero_edges.append(ie)
    
    l = len(nonzero_edges)
    if l > 0:
        d = baseline_dict[l]
        
        edge_types = tuple(map(lambda e: e.edge_type, nonzero_edges))
            
        top_f = 0
        top_p = None

        if len(edge_types) <= 7:
            for p in permutations(edge_types):
                if p in d:
                    if d[p] > top_f:
                        top_p = p
                        top_f = d[p]
                
        # fallback: random
        if top_p == None:
            top_p = [x for x in edge_types]
            shuffle(top_p)

        consumed = []
        l = list(range(len(ref.in_edges)))
        shuffle(l)
        for j in l:
            if ref.in_edges[j].token_index > 0:
                for i in range(len(top_p)):
                    if ref.in_edges[j].edge_type == top_p[i] and (not (i+1 in consumed)):
                        baseline.append(i+1)
                        consumed.append(i+1)
                        break
    baseline.reverse()

    return baseline

def extract_ngram(edge, bigrams):
    prob_first = [0.0]
    prob_last = [0.0]
    if len(edge.tokens)>0:
        for e in edge.to_node.in_edges:
            if e != edge:
                key_first = tuple([" ".join(edge.tokens)," ".join(e.tokens)])
                if key_first in bigrams:
                    prob_first.append(bigrams[key_first])
                key_last = tuple([" ".join(e.tokens)," ".join(edge.tokens)])
                if key_last in bigrams:
                    prob_last.append(bigrams[key_last])
    sum_first = reduce(lambda x,y: x+y, prob_first)
    if sum_first > 0:
        sum_first = -math.log(sum_first)
    sum_last = reduce(lambda x,y: x+y, prob_last)
    if sum_last > 0:
        sum_last = -math.log(sum_last)
    return [sum_first, sum_last]

def extract_binary_relations(edge, lists):
    binary_relations = ""
    if edge.edge_type == "int":
        if edge.from_node.short() in accepted_relations:
            br = edge.from_node.short()
        else:
            br = "other"
        binary_relations += br+"-"
    if binary_relations == "":
        binary_relations = "none"
#    return binary_relations[:-1]
    return binary_vector([binary_relations[:-1]], lists["binary_relations"])                            

def extract_discourse_unit_types(edge, lists):
    du_to = edge.to_node.neighbors_in(edge_type="referent")[0]
    du_from_list = edge.from_node.neighbors_in(edge_type="referent")
    if len(du_from_list) > 0:
        du_from = du_from_list[0]
        return binary_vector([du_to.type], lists["du_types"]) + binary_vector([du_from.type], lists["du_types"])
    else:
        return binary_vector([du_to.type], lists["du_types"]) + binary_vector([], lists["du_types"])
           
def extract_operator(edge, lists):
    op_to = None
    du_to_list = edge.from_node.neighbors_in(edge_type="referent")
    if len(du_to_list) > 0:
        du_to = du_to_list[0]
        op_to_list = du_to.neighbors_in(edge_type="scope") + du_to.neighbors_in(edge_type="antecedent") + du_to.neighbors_in(edge_type="consequent")
        if len(op_to_list) > 0:
            op_to = op_to_list[0]
            
    op_from = None
    du_from_list = edge.from_node.neighbors_in(edge_type="referent")
    if len(du_from_list) > 0:
        du_from = du_from_list[0]
        op_from_list = du_from.neighbors_in(edge_type="scope") + du_from.neighbors_in(edge_type="antecedent") + du_from.neighbors_in(edge_type="consequent")
        if len(op_from_list) > 0:
            op_from = op_from_list[0]
    
    if op_to and op_from:
        return binary_vector([op_to.type], lists["operators"]) + binary_vector([op_from.type], lists["operators"])
    elif op_to and not op_from:
        return binary_vector([op_to.type], lists["operators"]) + binary_vector([], lists["operators"])
    elif not op_to and op_from:
        return binary_vector([], lists["operators"]) + binary_vector([op_from.type], lists["operators"])
    else:
        return binary_vector([], lists["operators"]) + binary_vector([], lists["operators"])

           
def extract_event_tense(event_ref, lists):
    temporal_relations = []
    for n in event_ref.neighbors_in(edge_type="int"):
        if n.type == "relation" and "temp_" in n.short():
            temporal_relations.append(n.short())
    return binary_vector(temporal_relations, lists["temporal"])
 
def extract_cardinality(concept_ref, lists):
    cardinality = []
    for n in concept_ref.neighbors_in(edge_type="arg"):
        if n.type == "cardinality":
            cardinality.append(n.name.split(':')[-1])
    return binary_vector(cardinality, lists["card_operators"])
    
 
def extract_event_symbol_hypernyms(node, lists):
    hypernyms = []
    for n in node.neighbors_in(edge_type="instance"):
        if n.type == "event":
            hypernyms += wn_hypernyms(n.short(), wn.VERB)
    if len(hypernyms)>0:
        return binary_vector([hypernyms[0]], lists["event_symbols_hypernyms"])
    else:
        return binary_vector(["notfound"], lists["event_symbols_hypernyms"])

def extract_entity_symbol_hypernyms(node, lists):
    hypernyms = []
    for n in node.neighbors_in(edge_type="instance"):
        if n.type == "concept":
            hypernyms += wn_hypernyms(n.short(), wn.NOUN)
    return binary_vector(hypernyms, lists["entity_symbols_hypernyms"])

def extract_named_type(node, lists):
    named_types = []
    for n in node.neighbors_in(edge_type="instance"):
        if n.type == "named":
            named_types.append(n.name.split(':')[-1])
    return binary_vector(named_types, lists["named_types"])

def extract_edge_type(edge, lists):
    return binary_vector([edge.edge_type], lists["edge_types"])

def extract_related_concept_hypernyms(edge, lists):
    hypernyms = []
    if edge.from_node.type == "relation":
        if edge.edge_type == "int":
            related = edge.from_node.neighbors_out(edge_type="ext")[0]
        elif edge.edge_type == "ext":
            related = edge.from_node.neighbors_out(edge_type="int")[0]
        else:
            related = edge.from_node
        for symbol in related.neighbors_in("instance"):
            if symbol.type == "concept":
                hypernyms += wn_hypernyms(symbol.short(), wn.NOUN)
    return binary_vector(hypernyms, lists["entity_symbols_hypernyms"])

def extract_related_ref_type(edge, lists):
    conditions = []
    if edge.from_node.type == "relation":
        if edge.edge_type == "int":
            related = edge.from_node.neighbors_out(edge_type="ext")[0]
        elif edge.edge_type == "ext":
            related = edge.from_node.neighbors_out(edge_type="int")[0]
        else:
            related = edge.from_node
        for neighbor in related.neighbors_in():
            conditions.append(neighbor.type)
    return binary_vector(conditions, lists["conditions"])

def extract_punctuation(edge, lists):
    if edge.edge_type == "punctuation":
#        return "punctuation"
        return [1]
    else:
#        return "nopunctuation"
        return [0]
        
def extract_surface(edge, lists):
    if edge.edge_type == "surface":
#        return "surface"
        return [1]
    else:
#        return "nosurface"
        return [0]
        
def extract_node_type(edge, lists):
#    return edge.from_node.type
    return binary_vector([edge.from_node.type], lists["node_types"])
    
