class Singleton(object):
    """Use to create a singleton"""
    def __new__(cls, *args, **kwds):
        """
        >>> s = Singleton()
        >>> p = Singleton()
        >>> id(s) == id(p)
        True
        """
        self = "__self__"
        if not hasattr(cls, self):
            instance = object.__new__(cls)
            instance.init(*args, **kwds)
            setattr(cls, self, instance)
        return getattr(cls, self)

    def init(self, *args, **kwds):
        pass


class Test(Singleton):
    def init(self):
        print "INIT"


class Test2(Test):
    def init(self):
        print "INIT2"


t=Test()
t1=Test()
t2=Test()


print t, t1, t2

a=Test2()
a1=Test2()
a2=Test2()

print a, a1, a2

