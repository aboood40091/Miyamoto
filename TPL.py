try:
	raise ImportError('')
	print('a')
	import pyximport
	print('b')
	pyximport.install()
	print('c')
	import TPLcy
	print('d')
except ImportError:
	print('e')
	from TPLpy import *
	print('f')
print('g')

# Enums
I4 = 0
I8 = 1
IA4 = 2
IA8 = 3
RGB565 = 4
RGB4A3 = 5
RGBA8 = 6
CI4 = 8
CI8 = 9
CI14x2 = 10
CMPR = 14

def algorithm(type):
    """Returns the appropriate algorithm based on the type specified"""
    if not isinstance(type, int):
        raise TypeError('Type is not an int')

    if type == CI4:
        raise ValueError('CI4 is not supported')
    elif type == CI8:
        raise ValueError('CI8 is not supported')
    elif type == CI14x2:
        raise ValueError('CI14x2 is not supported')
    elif type == CMPR:
        raise ValueError('CMPR is not supported')
    elif type < 0 or type in (7, 11, 12, 13) or type > 14:
        raise ValueError('Unrecognized type')

    if type == I4:
    	return I4Decoder
    elif type == I8:
    	return I8Decoder
    elif type == IA4:
    	return IA4Decoder
    elif type == IA8:
    	return IA8Decoder
    elif type == RGB565:
    	return RGB565Decoder
    elif type == RGB4A3:
    	return RGB4A3Decoder
    elif type == RGBA8:
    	return RGBA8Decoder
