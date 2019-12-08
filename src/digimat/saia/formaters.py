import struct

from .singleton import Singleton


class SAIAValueFormater(Singleton):
    def decode(self, deviceValue):
        """
        decode UINT32 device value (register) to user value
        """
        return deviceValue

    def encode(self, userValue):
        """
        encode user value to UINT32 (SAIA register)
        """
        return userValue


class SAIAValueFormaterFloat32(SAIAValueFormater):
    def decode(self, deviceValue):
        return struct.unpack('>f', struct.pack('>I', deviceValue))[0]

    def encode(self, userValue):
        return struct.unpack('>I', struct.pack('>f', userValue))[0]


class SAIAValueFormaterSwappedFloat32(SAIAValueFormater):
    def decode(self, deviceValue):
        return struct.unpack('<f', struct.pack('>I', deviceValue))[0]

    def encode(self, userValue):
        return struct.unpack('>I', struct.pack('<f', userValue))[0]


class SAIAValueFormaterInteger10(SAIAValueFormater):
    def decode(self, deviceValue):
        deviceValue=struct.unpack('>i', struct.pack('>I', deviceValue))[0]
        return round(float(deviceValue/10.0), 1)

    def encode(self, userValue):
        userValue=int(round(float(userValue)*10.0, 1))
        return struct.unpack('>I', struct.pack('>i', userValue))[0]


class SAIAValueFormaterFFP(SAIAValueFormater):
    """
    Motorola Fast Floating Point

    3 2         1
    10987654321098765432109876543210
    MMMMMMMMMMMMMMMMMMMMMMMMSEEEEEEE
    M..M is the mantissa, forming an unsigned integer of value m.
    E..E is the binary exponent, forming an unsigned integer of value e.
    S is the sign, 0 or 1
    The value of an FFP number is either 0 if all bits are 0, or computed
    as follows:
        s        e-88
    (-1)  * m * 2
    Note that unlike IEEE numbers, FFP numbers can*not* be compared as if
    they were integers.
    """

    def decode(self, deviceValue):
        """
        convert ffp register to ieee float32 value, remaping 32-bits registers bits
        FFP:  MMMMMMMMMMMMMMMMMMMMMMMMSEEEEEEE (deviceValue)
        IEEE: SEEEEEEEEMMMMMMMMMMMMMMMMMMMMMMM (userValue, returned as float32)
        """
        if (deviceValue & 0xffffff00)==0:
            return 0.0

        m=(deviceValue & 0x7fffff00) >> 8
        s=deviceValue & 0x80
        # e=24-(88-(value & 0x7f))-1+127
        e=(deviceValue & 0x7f)+62
        if s:
            m=m | 0x80000000
        m = m | (e << 23)

        userValue=struct.unpack('>f', struct.pack('>I', m))[0]
        return userValue

    def encode(self, userValue):
        """
        convert ieee float32 value to ffp register, remaping 32-bits registers bits
        IEEE: SEEEEEEEEMMMMMMMMMMMMMMMMMMMMMMM (userValue, given as float32)
        FFP:  MMMMMMMMMMMMMMMMMMMMMMMMSEEEEEEE (deviceValue)
        """
        if userValue==0.0:
            return 0

        value=struct.unpack('>I', struct.pack('>f', float(userValue)))[0]
        s=value & 0x80000000
        # e=88-(24-(((value & 0x7f800000) >> 23)-127+1))
        e=((value & 0x7f800000) >> 23)-62
        m=((value & 0x7fffff) | 0x800000) << 8
        m = m | e
        if s:
            m = m | 0x80

        deviceValue=m
        return deviceValue


if __name__ == "__main__":
    pass
