import struct


def decode(deviceValue):
    """
    Motorola Fast Floating Point

    float ffpieee(const uint32_t val)
    {
        uint32_t x = val;
        union {
            float f;
            uint32_t i;
        } _fcast;

        x = x + x;		// delete mantissa high bit
        if (x == 0) {
            // if zero, branch zero as finished
            return (float)x;
        }

        uint8_t k = x & 0xff;

        k ^= 0x80;	// to two's complement exponent
        k >>= 1;	// form 8-bit exponent
        k -= 0x82;	// adjust 64 to 127 and excessize

        x = (x & ~0xff) | k;

        x = (x << 16) | (x >> 16);	// swap for high byte placement
        x <<= 7;	// set sign+exp in high byte

        _fcast.i = x;

        return _fcast.f;
    }

    guess there are tons of Motorola references, but I know it from the
    AmigaOS documentation:
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

    print bin(deviceValue)
    x=(deviceValue + deviceValue) & 0xfFFFFFFF
    if x==0:
        return 0.0

    k=x & 0xff
    k=(k ^ 0x80) & 0xff
    k=k >> 1
    k=(k-0x82) & 0xff

    x=(x & 0xffffff00) | k
    print "xa", bin(x)
    x=((x << 16) & 0xFFFF0000) | (x >> 16)
    print "xb", bin(x)
    x=x << 7
    print "xc", bin(x)

    print '%X' % x

    print struct.unpack('>f', struct.pack('>I', x))
    return 10.0


print decode(0x80000042)
