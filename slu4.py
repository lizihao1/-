
from collections import defaultdict
import xml.etree.ElementTree as ET
import datetime
from itertools import *
from functools import *

class PetriNet:
    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.id_transitions = {}
        self.from_edges = defaultdict(dict)
        self.to_edges = defaultdict(dict)
        self.markings = {}
        self.start = None
        self.end = None
    
    def reset(self):
        self.markings = {}
        self.add_marking(self.start) 

    def find_enabled_transition(self):
        res = {}
        for transition in self.transitions.keys():
            if self.is_enabled(transition):
                res[transition] = (self.to_edges[transition].keys(), self.from_edges[transition].keys(), transition)
        return res

    def replay(self, trace):
        self.reset()
        consume_count = 0
        produce_count = 0
        retain_count = 0
        miss_count = 0
        miss_tokens = []
        trace_ids = list([ self.transition_name_to_id(x) for x in trace])

        while  self.end not in self.markings or self.markings[self.end] == 0:
            res = self.find_enabled_transition()
            trace_id = None
            for x in trace_ids:
                if x in res:
                   trace_id = x 
                   trace_ids.remove(x)
                   break
            if trace_id != None:
                (froms, tos, trace_id) = res[trace_id]
                consume_count = consume_count + len(froms)
                produce_count = produce_count + len(tos)
            else:
                (froms, tos, trace_id) = res.values()[0]
                retain_count = retain_count + len(froms)
                miss_count = miss_count + len(tos)
                consume_count = consume_count + len(froms)
                produce_count = produce_count + len(tos)

            self.fire_transition(trace_id)

        return (miss_count, retain_count, consume_count, produce_count)
    

    
    def set_start(self, start):
        self.start = start
    
    def set_end(self, end):
        self.end = end

    def add_place(self, name):
        self.places[name] = name

    def add_transition(self, name, id):
        self.transitions[id] = [id, name]
        self.id_transitions[name] = id

    def transition_name_to_id(self, name):
        return self.id_transitions[name] 

    def add_edge(self, source, target):
        self.from_edges[source][target] = target
        self.to_edges[target][source] = source
        return self

    def get_tokens(self, place):
        if place in self.markings:
            return self.markings[place]
        
        return 0

    def is_enabled(self, transition):
        for key in self.to_edges[transition].keys():
            if not key in self.markings or self.markings[key] <= 0:
                return False
        
        return True

    def add_marking(self, place):
        if not place in self.markings:
            self.markings[place] = 0

        self.markings[place] = self.markings[place] + 1

    def fire_transition(self, transition):
        while self.is_enabled(transition):
            for key in self.to_edges[transition].keys():
                if key in self.markings:
                    self.markings[key] = self.markings[key] - 1
                    
            for out in self.from_edges[transition].keys():
                if not out in self.markings:
                    self.markings[out] = 0
                self.markings[out] = self.markings[out] + 1

def read_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    res = {}
    pre = '{http://www.xes-standard.org/}'


    for trace in root.findall(pre + "trace"):
        case_node = trace.find(pre + 'string')
        case_id = case_node.get('value')
        if not case_id in res:
            res[case_id] = []
        
        for event in trace.findall(pre + 'event'):
            item = {}
            for str_item in event.findall(pre + 'string'):
                key = str_item.get('key')
                value = str_item.get('value')
                item[key] = value 

            for int_item in event.findall(pre + 'int'):
                key = int_item.get('key')
                value = int_item.get('value')
                item[key] = int(value)

            for date_item in event.findall(pre + 'date'):
                key = date_item.get('key')
                value = date_item.get('value')
                parts = value.split('T')
                date = parts[0]
                date_parts = date.split('-')
                year = int(date_parts[0])
                month = int(date_parts[1])
                day = int(date_parts[2])
                time = parts[1].split('+')[0]
                time_parts = time.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                second = int(time_parts[2])

                item[key] = datetime.datetime(year, month, day, hour, minute, second, 0)

        
            res[case_id].append(item)
    
    return res

def generate_id(start, step = 1):
    while True:
        yield start
        start = start + step


def alpha(log):
    res_net = PetriNet()
    item_set = set()
    ds_relations = {}
    for key in log.keys():
        items = log[key]
        items = [x['concept:name'] for x in items]
        item_set.update(items)
        item_relations = list(zip(items[:], items[1:]))
        ds_relations.update({item:1 for item in item_relations})
    rca_relations = defaultdict(set)
    ca_relations = defaultdict(set)
    pa_relations = set()
    ch_relations = set()
    for k in ds_relations.keys(): 
        if not (k[1], k[0]) in ds_relations:
            ca_relations[k[0]].add(k[1])
            rca_relations[k[1]].add(k[0])
    for k in ds_relations.keys(): 
        if  (k[1], k[0]) in ds_relations:
            pa_relations.add((k[0], k[1]))
    for k in product(list(item_set), list(item_set)): 
        if not (k[0], k[1]) in ds_relations and not (k[1], k[0]) in ds_relations:
            ch_relations.add((k[0], k[1]))

    pre_set = { k[0] for k in ds_relations.keys()}
    sub_set = { k[1] for k in ds_relations.keys()}
    start_item = list(filter(lambda x: not x in sub_set, item_set))[0]
    end_item = list(filter(lambda x: not x in pre_set, item_set))[0]
    place_id_generator = generate_id(1,1)
    transition_id_generator = generate_id(-1, -1)
    place_start_id = next(place_id_generator)
    
    res_net.add_place(place_start_id)

    for item in item_set:
        res_net.add_transition(item,next(transition_id_generator))

    mark_delete = []
    for pre in ca_relations.keys():
        subs = ca_relations[pre]
        pairs = list(zip(repeat(pre), subs))
        makes = list(combinations(pairs, 2))
        #print("as_relations")
        as_relations = list(filter(lambda k: (k[0][1], k[1][1]) in pa_relations, makes))
        for k in as_relations:

            one = next(place_id_generator)
            res_net.add_place(one)
            #print ("add edge {} {} -> {}".format (k[0][0], res_net.transition_name_to_id(k[0][0]), one))
            res_net.add_edge(res_net.transition_name_to_id(k[0][0]), one)
            #print ("add edge {} -> {} {}".format (one, k[0][1], res_net.transition_name_to_id(k[0][1])))
            res_net.add_edge(one, res_net.transition_name_to_id(k[0][1]))

            two = next(place_id_generator)
            res_net.add_place(two)
            #print ("add edge {} {} -> {}".format( k[1][0], res_net.transition_name_to_id(k[1][0]), two))
            res_net.add_edge(res_net.transition_name_to_id(k[1][0]), two)
            #print ("add edge {} -> {} {}".format(two, k[1][1], res_net.transition_name_to_id(k[1][1])))
            res_net.add_edge(two, res_net.transition_name_to_id(k[1][1]))

            mark_delete.append(k) 

        #print("xs_relations")
        xs_relations = list(filter(lambda k: (k[0][1], k[1][1]) in ch_relations, makes))
        for k in xs_relations:

            one = next(place_id_generator)
            res_net.add_place(one)
            #print ("add edge {} {} -> {}".format( k[0][0], res_net.transition_name_to_id(k[0][0]), one))
            res_net.add_edge(res_net.transition_name_to_id(k[0][0]), one)
            #print ("add edge {} -> {} {}".format( one, k[0][1], res_net.transition_name_to_id(k[0][1])))
            res_net.add_edge(one, res_net.transition_name_to_id(k[0][1]))
            #print ("add edge {} -> {} {}".format( one, k[1][1], res_net.transition_name_to_id(k[1][1])))
            res_net.add_edge(one, res_net.transition_name_to_id(k[1][1]))

            mark_delete.append(k)

    for sub in rca_relations.keys():
        pres = rca_relations[sub]
        pairs = list(zip(pres, repeat(sub)))
        makes = list(combinations(pairs, 2))
        #print("aj_relations")
        aj_relations = list(filter(lambda k: (k[0][0], k[1][0]) in pa_relations, makes))
        for k in aj_relations:

            one = next(place_id_generator)
            res_net.add_place(one)
            #print ("add edge {} {} -> {}".format (k[0][0], res_net.transition_name_to_id(k[0][0]), one))
            res_net.add_edge(res_net.transition_name_to_id(k[0][0]), one)
            #print ("add edge {} -> {} {}".format (one, k[0][1], res_net.transition_name_to_id(k[0][1])))
            res_net.add_edge(one, res_net.transition_name_to_id(k[0][1]))

            two = next(place_id_generator)
            res_net.add_place(two)
            #print ("add edge {} {} -> {}".format( k[1][0], res_net.transition_name_to_id(k[1][0]), two))
            res_net.add_edge(res_net.transition_name_to_id(k[1][0]), two)
            #print ("add edge {} -> {} {}".format(two, k[1][1], res_net.transition_name_to_id(k[1][1])))
            res_net.add_edge(two, res_net.transition_name_to_id(k[1][1]))

            mark_delete.append(k)

        #print("xj_relations")
        one = next(place_id_generator)
        xj_relations = list(filter(lambda k: (k[0][0], k[1][0]) in ch_relations, makes))
        for k in xj_relations:
            res_net.add_place(one)
#            #print ("add edge {} -> {}".format(k[0][0], one))
            res_net.add_edge(res_net.transition_name_to_id(k[0][0]), one)
#            print ("add edge {} -> {}".format (k[1][0], one))
            res_net.add_edge(res_net.transition_name_to_id(k[1][0]), one)
#            print ("add edge {} -> {}".format(one, k[0][1]))
            res_net.add_edge(one, res_net.transition_name_to_id(k[0][1]))

            mark_delete.append(k)

    
    for item in mark_delete:
        if item[0][1] in ca_relations[item[0][0]]:
            ca_relations[item[0][0]].remove(item[0][1])
        if item[1][1] in ca_relations[item[1][0]]:
            ca_relations[item[1][0]].remove(item[1][1])

    
    #print("ca_relations")
    for pre in ca_relations.keys():
        subs = list(ca_relations[pre])
        for sub in subs:
            one = next(place_id_generator)
            #print ("add edge {} -> {}".format(pre, one))
            res_net.add_edge(res_net.transition_name_to_id(pre), one)
            #print ("add edge {} -> {}".format(one, sub))
            res_net.add_edge(one, res_net.transition_name_to_id(sub))

    
    #print ("add edge {} -> {}".format(place_start_id, start_item))
    res_net.add_edge(place_start_id, res_net.transition_name_to_id(start_item))
    place_end_id = next(place_id_generator)
    res_net.add_place(place_end_id)
    #print ("add edge {} -> {}".format(end_item, place_end_id))
    res_net.add_edge(res_net.transition_name_to_id(end_item), place_end_id)
    res_net.add_marking(place_start_id)
    res_net.set_start(place_start_id)
    res_net.set_end(place_end_id)

    return res_net


def fitness_token_replay(log, model):
    res = {}
    trace_dict = {}
    for items in log.values():
        pitems = [x['concept:name'] for x in items]
        pp = ''.join(pitems)
        if pp not in res:
            res[pp]  = 0
        res[pp] = res[pp] + 1
        trace_dict[pp] = pitems
    l1 = 0
    l2 = 0
    r1 = 0
    r2 = 0

    
    for pp in res.keys():
        trace = trace_dict[pp]
        count = res[pp]
        (miss_count, retain_count, consume_count, produce_count) = model.replay(trace)
        l1 = l1 + count*miss_count
        l2 = l2 + count*consume_count
        r1 = r1 + count*retain_count
        r2 = r2 + count*produce_count
    
    return 0.5 * (1 - l1/l2) + 0.5*(1 - r1/r2)
