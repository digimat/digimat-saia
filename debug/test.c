#include <stdio.h>


float ffpieee(unsigned long int val)
{
    unsigned int x = val;
    union {
        float f;
        unsigned int i;
    } _fcast;

    x = x + x;		// delete mantissa high bit
    if (x == 0) {
        // if zero, branch zero as finished
        return (float)x;
    }

    unsigned char k = x & 0xff;

    k ^= 0x80;	// to two's complement exponent
    k >>= 1;	// form 8-bit exponent
    k -= 0x82;	// adjust 64 to 127 and excessize

    x = (x & ~0xff) | k;

    x = (x << 16) | (x >> 16);	// swap for high byte placement
    x <<= 7;	// set sign+exp in high byte

    _fcast.i = x;

    return _fcast.f;
}

int main(void)
{
    printf("conversion=%f", ffpieee(0x80000042));

}
