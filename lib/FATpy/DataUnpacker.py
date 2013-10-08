from struct import unpack

class DataUnpacker:
    def __init__(self,data):
        if not isinstance(data,str):
            raise Exception("DataUnpacker requires a string")
        self._data = data

    def __len__(self):
        return len(self._data)

    def __getitem__(self,key):
        return self._data[key]
    
    def getBYTE(self,offset):
        return unpack("B",self.getSTR(offset,1))[0]

    def getWORD(self,offset):
        return unpack("H",self.getSTR(offset,2))[0]

    def getDWORD(self,offset):
        return unpack("I",self.getSTR(offset,4))[0]

    def getSTR(self,offset,length):
        S = slice(offset,offset+length)
        return DataUnpacker.__getitem__(self,S)
#        return self._data[offset:offset+length]
