# Source - https://stackoverflow.com/a
# Posted by Mike McKerns, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-09, License - CC BY-SA 4.0

from pathos.multiprocessing import ProcessingPool as Pool

def foo(obj1, obj2):
    a = obj1.x**2
    b = obj2.x**2
    return a,b

class Bar(object):
    def __init__(self, x):
        self.x = x

Pool().map(foo, [Bar(1),Bar(2),Bar(3)], [Bar(4),Bar(5),Bar(6)])
