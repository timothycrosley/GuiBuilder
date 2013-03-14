'''
    Session.py

    Defines how the GuiBuilder session should be saved and loaded.

    Copyright (C) 2013  Timothy Edmund Crosley

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

try:
    import cPickle as pickle
except ImportError:
    import pickle

import os
import sys

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
            try:
                if sys.version >= "3":
                    self.update(pickle.loads(bytes(sessionFile.read(), 'utf8')))
                else:
                    self.update(pickle.loads(sessionFile.read()))
            except Exception:
                pass

    def save(self):
        with open(self.location, 'w') as sessionFile:
            sessionFile.write(str(pickle.dumps(self)))
