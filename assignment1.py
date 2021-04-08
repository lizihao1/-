from collections import defaultdict

class PetriNet:
    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.from_edges = defaultdict(dict)
        self.to_edges = defaultdict(dict)
        self.markings = {}

    def add_place(self, name):
        self.places[name] = name

    def add_transition(self, name, id):
        self.transitions[id] = [id, name]

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
