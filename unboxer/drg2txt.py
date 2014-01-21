# unboxer.py
from drg import DRGParser, DRG
import sys
from itertools import permutations,combinations_with_replacement
from time import sleep

def surface_form(ref, debug=False):
    surface_form = []
    
    # map token indices to the referent's in-edges:
    in_edges_dict = dict()
    for edge in ref.in_edges:
        if edge.token_index > 0:
            in_edges_dict[edge.token_index] = edge


    # append main event referent (if any)
    '''
    events = dict()    
    for ie in ref.in_edges:
        if ie.edge_type=="main":
            events[ie.token_index] = ie.from_node
    for index in sorted(events.iterkeys()):
        surface_form.append(["r",events[index].name])
    '''
     
    # sort the edges by token index:
    in_edges = []
    for key in sorted(in_edges_dict.iterkeys()):
        in_edges.append(in_edges_dict[key])
        
    # For each edge, append the tokens.
    for edge_index in range(len(in_edges)):
        edge = in_edges[edge_index]
        for t in edge.tokens:
            surface_form.append(["t",t.encode("utf-8")])

        # follow transitive attributes and append placeholders to their surface forms
        if edge.edge_type == "int":
            related = edge.from_node.neighbors_out(edge_type="ext")[0]
            surface_form.append(["r",related.name])
        
        # append main event referent (if any)
        if edge.edge_type=="main":
            surface_form.append(["r",edge.from_node.name])
            
    # follow equalities:
    #for edge in ref.in_edges:
    #    if edge.edge_type == "ext" and edge.from_node.short() =='equality':
    #        related = edge.from_node.neighbors_out(edge_type="int")[0]
    #        surface_form.append(["r",related.name])

    '''
    events = []
    for oe in ref.out_edges:
        if oe.edge_type=="event":
            eref = oe.to_node.neighbors_out(edge_type="instance")[0]
            events.append(eref)
    for event in events:
        surface_form.append(["r",event.name])
    '''        
    
    # append discourse relations
    for drel in ref.out_edges:
        if "subordinates" in drel.edge_type:
            surface_form.append(["r",drel.to_node.name])

     
    return surface_form
    
# return true if all the elements are tokens
def lt(sf):
    return not ("r" in map(lambda f: f[0], sf))

# returns the duplicates in a list
def dup(l):
    d = []
    while len(l)>0:
        i = l.pop()
        if i in l:
            d.append(i)
    return d

# removes duplicates marked by <d> in text
def removedup(t):
    tokens = t.split(' ')
    
    while True:
        last_step = tokens
        for p1,p2 in combinations_with_replacement(range(len(tokens)),2):
            if tokens[p1]=='<d>' and tokens[p2]=='</d>' and not '<d>' in tokens[p1+1:p2] and not '</d>' in tokens[p1+1:p2]:
                done = False
                for q1,q2 in combinations_with_replacement(range(p2+1, len(tokens)),2):
                    if tokens[p1:p2+1] == tokens[q1:q2+1]:
                        tokens = tokens[:q1] + tokens[q2+1:]
                        done = True
                        break
                if done: break
        if tokens == last_step:
            break
    
    # remove residual tags
    final = []
    for t in tokens:
        if t != '<d>' and t != '</d>':        
            final .append(t)
    return ' '.join(final)
    
def composition(ref1, sf1, ref2, sf2, duplicates):
    if lt(sf1) and ref1 in map(lambda f: f[1], sf2):
        ref = ref2
        i = sf2.index(["r", ref1])

        if ref1 in duplicates:
            # mark duplicates
            sf = sf2[:i] + [['t', '<d>']] + sf1 + [['t','</d>']] + sf2[i+1:]
        else:
            sf = sf2[:i] + sf1 + sf2[i+1:]
        
        return (ref, sf)

    
def unbox(drg, debug=False, concepts=False):
    surface_forms = dict()
    discourse_relations = []
    
    if len(drg.nodes)==0:
        sys.stderr.write("error: no parse found.\n")
        return ""

    # get surface forms from discourse units
    root = None
    du_list = drg.discourse_units()
    for du in du_list:
        if len(du.in_edges) - len(drg.in_edges(du, edge_type="main")) == 0:
            root = du
        surface_forms[du.name] = surface_form(du, debug=debug)
        
    # get surface forms from discourse referents
    for edge in drg.edges:
        if edge.edge_type == "referent":
            ref = edge.to_node
            surface_forms[ref.name] = surface_form(ref, debug=debug)
        if edge.from_node.type == "discourse_unit" and edge.to_node.type == "discourse_unit":
            discourse_relations.append((edge.from_node.name, edge.to_node.name))
                    
    if debug:
        for ref,sf in surface_forms.iteritems():
            sys.stderr.write("{0} : {1}\n".format(ref, " ".join(map(lambda f: f[1], sf))))

    # find double occurrences
    duplicates = []
    for ref,sf in surface_forms.iteritems():
        duplicates.extend(map(lambda f: f[1], sf))
    duplicates = dup(duplicates)
    
    # composition algorithm
    text = ""
    finish = False
    composed = [] # track the referents already composed
    while not finish:
        rule = False
        # for each couple of distinct discourse referent
        for (ref1, sf1),(ref2, sf2) in permutations(surface_forms.iteritems(), 2):
            # try to apply composition rule
            c = composition(ref1, sf1, ref2, sf2, duplicates)
            #sys.stderr.write("[C?] {0} : {1}\n".format(ref1, ref2))
            if c != None:
                ref, sf = c
                if debug:
                    sys.stderr.write("[C] {0} : {1}\n".format(ref, sf))
                
                surface_forms[ref]=sf
                rule = True
                last_composition = sf
                
                break
            if (ref1, ref2) in discourse_relations:
                sf = sf1 + sf2
                ref = ref1
                surface_forms.pop(ref1)
                surface_forms.pop(ref2)
                surface_forms[ref]=sf
                if debug:
                    sys.stderr.write("[R] {0} : {1}\n".format(ref, sf))
                rule = True
                break
        if not rule:
            sys.stderr.write("Stuck in infinite loop, halting.\n")
            return " ".join(map(lambda f:f[1], surface_forms[root.name]))
        
        # stop condition
        finish = True
        for ref, sf in surface_forms.iteritems():
            if not lt(sf):
                finish = False
    
    if concepts == False:
        # postprocessing: remove duplicates
        output = " ".join(map(lambda f:f[1],last_composition))
        return removedup(output)
        #return " ".join(map(lambda f:f[1],surface_forms[root.name]))
        
    else:
        # print the complete surface forms for concepts discourse referents
        for e in drg.edges:
            if e.edge_type == 'instance' and e.from_node.type == 'concept':
                sfl = map(lambda x:x[1],surface_forms[e.to_node.name])
                if sfl[0].startswith('<P>'):
                    sfl = sfl[1:]
                if sfl[-1].startswith('<P>'):
                    sfl = sfl[:-1]
                sfl2 = []
                for t in sfl:
                    if t.startswith('<P>'):
                        sfl2.append(t[3:])
                    else:
                        sfl2.append(t)
                sf = ' '.join(sfl2)
                print e.to_node.name, sf

