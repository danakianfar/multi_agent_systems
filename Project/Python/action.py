import heapq


class ActionHeap(object):
    def __init__(self, initial=None):
        if initial:
            self._data = [(key(item), item) for item in initial]
            heapq.heapify(self._data)
        else:
            self._data = []

    def push(self, action):
        assert isinstance(action, Action)
        heapq.heappush(self._data, action)

    def pop(self):
        return heapq.heappop(self._data).callback
    
    def peek(self):
        if len(self._data) > 0:
            return heapq.nsmallest(1, self._data)[0].time
        else:
            return -1
        
    def plot(self):
        print(self._data)
        
        

class Action:
    def __init__(self, time, callback):
        self.time = time
        self.callback = callback
        
    def __lt__(self, other):
        assert isinstance(other, self.__class__)
        return self.time < other.time
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.time == other.time
        else:
            return False
    
    def __str__(self):
        return '{}, {}'.format(self.time, self.callback)
    
    def __repr__(self):
        return str(self)