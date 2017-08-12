import math


def ftobin(value):
    (d, i)=math.modf(value)
    bvalue=bin(int(i))

    m=bvalue[3:]
    e=len(m)
    print e, m

    m=''

    while True:
        (d, i)=math.modf(value)
        print value, i, d
        if d==0:
            break
        value=d*2
        if value>=1.0:
            m+='1'
        else:
            m+='0'

import struct


def ffp2ieee(value):
    s=value & 0x80
    # e=24-(88-(value & 0x7f))-1+127
    e=(value & 0x7f)+62
    m=(value & 0x7fffff00) >> 8
    if s:
        m=m | 0x80000000
    m = m | (e << 23)
    print m
    print bin(m)
    return struct.unpack('>f', struct.pack('>I', m))[0]


def ieee2ffp(value):
    s=value & 0x80000000
    # e=88-(24-(((value & 0x7f800000) >> 23)-127+1))
    e=((value & 0x7f800000) >> 23)-62
    m=((value & 0x7fffff) | 0x800000) << 8
    m = m | e
    if s:
        m = m | 0x80
    return struct.unpack('>f', struct.pack('>I', m))[0]

















print ffp2ieee(0xaca00048)
print ieee2ffp(1126998016)


