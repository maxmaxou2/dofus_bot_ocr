from messageTypes import types
import struct

INT_SIZE = 32
SHORT_SIZE = 16
SHORT_MIN_VALUE = -32768
SHORT_MAX_VALUE = 32767
UNSIGNED_SHORT_MAX_VALUE = 65536
CHUNK_BIT_SIZE = 7
MAX_ENCODING_LENGTH = INT_SIZE // CHUNK_BIT_SIZE
MASK_10000000 = 128
MASK_01111111 = 127

class Paquet :
    def __init__(self, id, length, content) :
        self.id = id
        self.len = length
        self.content = content
        if str(id) in types :
            self.type = types[str(id)]
        else :
            self.type = 'Unknown'
        self.position = 0

    def isComplete(self) :
        return self.len == len(self.content)
    
    def read(self, nb :int) :
        data = self.content[self.position:self.position+nb]
        self.position+=nb
        return data

    def readInt(self) :
        return int.from_bytes(self.read(4), 'big')
    
    def readDouble(self) :
        return struct.unpack('>d', self.read(8))[0]

        # Exemple pour read_var_short
    def readVarShort(self):
        value = 0
        offset = 0
        while offset < SHORT_SIZE:
            b = int.from_bytes(self.read(1), 'big')
            has_next = (b & MASK_10000000) == MASK_10000000
            if offset > 0:
                value += (b & MASK_01111111) << offset
            else:
                value += b & MASK_01111111
            offset += CHUNK_BIT_SIZE
            if not has_next:
                if value > SHORT_MAX_VALUE:
                    value -= UNSIGNED_SHORT_MAX_VALUE
                return value
        raise ValueError("Too much data")