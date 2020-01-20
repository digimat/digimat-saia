  # Python 2/3 compatibility
import os
from threading import RLock
from datetime import datetime

from prettytable import PrettyTable

import re
import unicodedata
import unidecode


class SAIASymbol(object):
    ATTRIBUTE_FLAG='f'
    ATTRIBUTE_REGISTER='r'
    ATTRIBUTE_TIMER='t'
    ATTRIBUTE_COUNTER='c'

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
        if self.attribute in [SAIASymbol.ATTRIBUTE_FLAG,
                SAIASymbol.ATTRIBUTE_REGISTER,
                SAIASymbol.ATTRIBUTE_TIMER,
                SAIASymbol.ATTRIBUTE_COUNTER]:
            return self._address

    def isFlag(self):
        if self.attribute==SAIASymbol.ATTRIBUTE_FLAG:
            return True
        return False

    def isRegister(self):
        if self.attribute==SAIASymbol.ATTRIBUTE_REGISTER:
            return True
        return False

    def isTimer(self):
        if self.attribute==SAIASymbol.ATTRIBUTE_TIMER:
            return True
        return False

    def isCounter(self):
        if self.attribute==SAIASymbol.ATTRIBUTE_COUNTER:
            return True
        return False

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
        return False

    def __repr__(self):
        if self.attribute:
            return '<%s(attribute=%s, tag=%s, address=%d)>' % (self.__class__.__name__, self.attribute, self.tag, self.address)
        return '<%s(attribute=%s, tag=%s, value=%s)>' % (self.__class__.__name__, self.attribute, self.tag, self.value)


class SAIATagMount(object):
    """
    Special class allowing symbols to be accessed as local variable
    in the SAIASymbols.flags.xxx or SAIASymbols.registers.yyy object
    """

    def __init__(self, symbols):
        # assert symbols.__class.__name__=='SAIASymbols'
        self._symbols=symbols

    @property
    def symbols(self):
        return self._symbols

    def strip_accents(self, text):
        try:
            text = str(text, 'utf-8')
        except:
            pass
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        return str(text)

    def text_to_id(self, text):
        text = self.strip_accents(text.lower())
        text = re.sub('[ ]+', '_', text)
        text = re.sub('[^0-9a-zA-Z_-]', '', text)
        return text

    def normalizeTag(self, tag):
        try:
            tag=self.text_to_id(tag)
            tag=tag.strip(' _')
            tag=tag.replace('.', '_')
            tag=tag.replace('__', '_')
            tag=tag.strip('_')
            return tag
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

    def __getitem__(self, key):
        return self.symbols[key]


class SAIATagMountFlags(SAIATagMount):
    def __getitem__(self, key):
        symbol=self.symbols[key]
        if not symbol:
            symbol=self.symbols.flag(key)
        return symbol


class SAIATagMountRegisters(SAIATagMount):
    def __getitem__(self, key):
        symbol=self.symbols[key]
        if not symbol:
            symbol=self.symbols.register(key)
        return symbol


class SAIATagMountTimers(SAIATagMount):
    def __getitem__(self, key):
        symbol=self.symbols[key]
        if not symbol:
            symbol=self.symbols.timer(key)
        return symbol


class SAIATagMountCounters(SAIATagMount):
    def __getitem__(self, key):
        symbol=self.symbols[key]
        if not symbol:
            symbol=self.symbols.counter(key)
        return symbol


class SAIASymbols(object):
    def __init__(self):
        self._lock=RLock()
        self._filepath=None
        self._symbols={}
        self._index={}
        self._flags=SAIATagMountFlags(self)
        self._registers=SAIATagMountRegisters(self)
        self._timers=SAIATagMountTimers(self)
        self._counters=SAIATagMountCounters(self)
        self._user=None
        self._stamp=None

    def unload(self):
        """release loaded symbolsi (freeing allocated memory)"""
        self._symbols={}
        self._index={}
        self._flags=SAIATagMountFlags(self)
        self._registers=SAIATagMountRegisters(self)
        self._timers=SAIATagMountTimers(self)
        self._counters=SAIATagMountCounters(self)

    @property
    def flags(self):
        return self._flags

    @property
    def registers(self):
        return self._registers

    @property
    def timers(self):
        return self._timers

    @property
    def counters(self):
        return self._counters

    @property
    def user(self):
        return self._user

    @property
    def buildDateTime(self):
        return self._stamp

    def all(self):
        with self._lock:
            return list(self._symbols.values())

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
                    elif symbol.isTimer():
                        self._timers.mount(symbol)
                    elif symbol.isCounter():
                        self._counters.mount(symbol)

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

    def decodeHeader(self, line):
        try:
            if 'user:' in line:
                data=line.split(':', 1)
                self._user=data[1].strip()

            elif 'linked:' in line:
                data=line.split(' '*2)
                for item in data:
                    (key, value)=item.split(':', 1)
                    if key.strip()=='linked':
                        value=value.strip()
                        if value:
                            # TODO: don't know if dateformat is PG5 regional format dependant
                            stamp=datetime.strptime(value, '%m/%d/%y %H:%M')
                            self._stamp=stamp
        except:
            pass

    def loadSymbolsFromData(self, data):
        if data:
            dataSymbols=[]

            header=True
            for n in range(len(data)):
                line=data[n].strip('\n')
                if header:
                    line=line.strip().lower()
                    self.decodeHeader(line)

                    if line=='public symbols':
                        header=False
                        continue
                else:
                    if not line:
                        break

                    if line.lstrip()!=line:
                        dataSymbols[-1]=dataSymbols[-1]+line
                    else:
                        dataSymbols.append(line)

            for line in dataSymbols:
                try:
                    fields=line.split()
                    if '..' in fields[2]:
                        # looks like a range
                        (start, stop)=fields[2].split('..')
                        tag=fields[0]
                        n=0
                        for index in range(int(start), int(stop)+1):
                            fields[0]=tag+str(n)
                            n+=1
                            fields[2]=index
                            symbol=SAIASymbol(fields)
                            self.add(symbol)
                            if index>=stop:
                                break
                            index+=1
                    else:
                        symbol=SAIASymbol(fields)
                        self.add(symbol)
                except:
                    pass

    def retrieveData(self):
        try:
            with open(self._filepath, 'r', errors='ignore') as f:
                return f.readlines()
        except:
            pass

    def load(self, filename, path=None):
        try:
            if not self._symbols:
                fpath=unidecode.unidecode(filename)
                if path:
                    fpath=os.path.join(path, filename)
                self._filepath=os.path.expanduser(fpath)
                data=self.retrieveData()
                self.loadSymbolsFromData(data)
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
        return self.getWithAttribute(SAIASymbol.ATTRIBUTE_FLAG, key)

    def register(self, key):
        return self.getWithAttribute(SAIASymbol.ATTRIBUTE_REGISTER, key)

    def timer(self, key):
        return self.getWithAttribute(SAIASymbol.ATTRIBUTE_TIMER, key)

    def counter(self, key):
        return self.getWithAttribute(SAIASymbol.ATTRIBUTE_COUNTER, key)

    def search(self, key):
        """
        return all matching symbols
        key may be a string or a re.compile() pattern
        """

        symbols=[]
        with self._lock:
            for symbol in self.all():
                try:
                    try:
                        if key.match(symbol.tag):
                            symbols.append(symbol)
                    except:
                        if key in symbol.tag:
                            symbols.append(symbol)
                except:
                    pass
        return symbols

    def table(self, key=None):
        if key:
            symbols=self.search(key)
        else:
            symbols=self.all()

        if symbols and len(symbols)>0:
            t=PrettyTable()
            t.field_names = ['tag', 't', 'index']
            t.align['tag']='l'
            t.align['index']='r'

            for symbol in symbols:
                t.add_row([symbol.tag, symbol.attribute, symbol.index])

            print(t)

    def __repr__(self):
        stamp=self.buildDateTime
        if stamp:
            return '<%s(%d items, buildDateTime=%s)>' % (self.__class__.__name__,
                self.count(),
                stamp.strftime('%d-%m-%Y %H:%M:%S'))
        return '<%s(%d items)>' % (self.__class__.__name__, self.count())


if __name__ == "__main__":
    pass
