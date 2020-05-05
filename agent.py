from itertools import count

class Agent(object):
    id_generator = count()
    """
    
    """
    def __init__(self):
        self.ident = Agent.id_generator.next()

    def __hash__(self):
        return self.ident