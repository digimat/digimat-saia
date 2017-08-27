class Singleton(object):
    # def __new__(cls, *args, **kwds):
        # if not hasattr(cls, 'instance'):
            # cls.instance=super(Singleton, cls).__new__(cls, *args, **kwds)
        # return cls.instance

    def __new__(cls, *args, **kwds):
        if not hasattr(cls, 'instance'):
            cls.instance=super(Singleton, cls).__new__(cls)
        return cls.instance


if __name__ == "__main__":
    pass
