from threading import RLock


class SAIASymbol(object):
    def __init__(self, data):
        self._attribute=None
        self._tag=None
        self._address=None
        self._value=None
        self.load(data)

    @property
    def attribute(self):
        return self._attribute

    @property
    def tag(self):
        return self._tag

    @property
    def address(self):
        return self._address

    @property
    def value(self):
        return self._value

    @property
    def index(self):
        if self.attribute in ['r', 'f', 'c']:
            return self._address

    def isFlag(self):
        if self.attribute=='f':
            return True

    def isRegister(self):
        if self.attribute=='r':
            return True

    def isCounter(self):
        if self.attribute=='c':
            return True

    def load(self, data):
        try:
            if data:
                self._tag=data[0].lower()
                if data[1].isalpha():
                    self._attribute=data[1].lower()
                    self._address=int(data[2])
                else:
                    self._value=data[1]
        except:
            pass

    def isValid(self):
        if self._tag:
            if self._attribute:
                if self._address is not None:
                    return True
            else:
                if self._value is not None:
                    return True

    def __repr__(self):
        if self.attribute:
            return '<%s(%s:%s:%d)>' % (self.__class__.__name__, self.attribute, self.tag, self.address)
        return '<%s(%s:%s:%s)>' % (self.__class__.__name__, self.attribute, self.tag, self.value)


class SAIATagMount(object):
    def normalizeTag(self, tag):
        try:
            tag=tag.strip('_')
            tag=tag.replace('.', '_')
            tag=tag.replace('__', '_')
            tag=tag.strip('_')
        finally:
            return tag

    def mount(self, symbol):
        assert symbol.__class__.__name__=='SAIASymbol'
        tag=self.normalizeTag(symbol.tag)
        if tag:
            try:
                if not hasattr(self, tag):
                    setattr(self, tag, symbol)
            except:
                pass


class SAIASymbols(object):
    def __init__(self, filename=None):
        self._lock=RLock()
        self._symbols={}
        self._index={}
        self._flags=SAIATagMount()
        self._registers=SAIATagMount()
        self.load(filename)

    @property
    def flags(self):
        return self._flags

    @property
    def registers(self):
        return self._registers

    def all(self):
        with self._lock:
            return self._symbols.values()

    def count(self):
        with self._lock:
            return len(self._symbols)

    def get(self, key):
        with self._lock:
            try:
                return self._symbols[key.lower()]
            except:
                pass

    def __getitem__(self, key):
        return self.get(key)

    def mount(self):
        """
        create object variables for each symbol for better interactive usage
        with interpreter autocompletion
        """

        with self._lock:
            for symbol in self.all():
                if symbol.isValid():
                    if symbol.isFlag():
                        self._flags.mount(symbol)
                    elif symbol.isRegister():
                        self._registers.mount(symbol)

    def add(self, symbol):
        assert symbol.__class__.__name__=='SAIASymbol'

        if symbol and symbol.isValid():
            if not self.get(symbol.tag):
                with self._lock:
                    self._symbols[symbol.tag]=symbol
                    if symbol.attribute:
                        try:
                            self._index[symbol.attribute]
                        except:
                            self._index[symbol.attribute]={}
                        self._index[symbol.attribute][symbol.index]=symbol
                    return symbol

    def loadSymbolsFromData(self, data):
        section=False
        dataSymbols=[]

        for n in range(len(data)):
            line=data[n].strip('\n')

            if section:
                if not line:
                    break

                if line.lstrip()!=line:
                    dataSymbols[-1]=dataSymbols[-1]+line
                else:
                    dataSymbols.append(line)
            else:
                if line.strip().lower()=='public symbols':
                    section=True
                    continue

        for line in dataSymbols:
            symbol=SAIASymbol(line.split())
            self.add(symbol)

    def load(self, filename):
        try:
            if not self._symbols:
                with open(filename, 'r') as f:
                    self.loadSymbolsFromData(f.readlines())
        except:
            pass

    def getWithAttribute(self, attribute, key):
        symbol=self.get(key)
        if not symbol:
            with self._lock:
                try:
                    symbol=self._index[attribute][int(key)]
                except:
                    pass

        if symbol and symbol.attribute==attribute:
            return symbol

    def flag(self, key):
        return self.getWithAttribute('f', key)

    def register(self, key):
        return self.getWithAttribute('r', key)

    def counter(self, key):
        return self.getWithAttribute('c', key)


if __name__ == "__main__":
    pass
