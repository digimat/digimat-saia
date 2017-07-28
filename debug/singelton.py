class Singleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance=super(Singleton, cls).__new__(cls)
        return cls.instance



s=Singleton()
s1=Singleton()

print s, s1

class MySingleton(Singleton):
    def __init__(self):
        self._y=1
        pass


m=MySingleton()
m1=MySingleton()

print m, m1




