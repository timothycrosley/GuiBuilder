import cPickle as pickle
import os

class Session(dict):

    def __init__(self, location):
        dict.__init__(self)
        self.location = location
        if not os.path.exists(self.location):
            self.save()
        else:
            self.load()

    def load(self):
        self.clear()
        with open(self.location, 'r') as sessionFile:
            self.update(pickle.loads(sessionFile.read()))

    def save(self):
        with open(self.location, 'w') as sessionFile:
            sessionFile.write(pickle.dumps(self))
