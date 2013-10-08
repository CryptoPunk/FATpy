from DataUnpacker import DataUnpacker
class MultiBlockDataUnpacker(DataUnpacker):
    def __init__(self,blocks,max_len=None):
        self.blocks = blocks
        if isinstance(blocks,DataUnpacker):
            self.blocks = [blocks]
        self.spc = len(self.blocks[0])
        self.max_len = max_len
        for block in self.blocks:
            if not isinstance(block,DataUnpacker):
                raise Exception("MultiBlockDataUnpacker requires the DataUnpacker type, got %s" % block)
            if len(block) != self.spc:
                raise Exception("MultiBlockDataUnpacker requires equal-length blokcs")

    def __len__(self):
        '''
        This should be the length of the data in bytes
        '''
        if self.max_len is not None:
            return self.max_len
        else:
            return self.spc * len(self.blocks)

    def __getitem__(self,key):
        if isinstance(key,(int,long)):
            return self.blocks[int(key/self.spc)][key%self.spc]
        elif isinstance(key,slice):
            #TODO Real Indices support
            
            (start,end,step) = key.indices(MultiBlockDataUnpacker.__len__(self))
            start_block = int(start/self.spc)
            end_block = int(end/self.spc)
            if 1 != step:
                raise KeyError("Can't handle steps in slices")
            elif start_block == end_block:
                buf = self.blocks[start_block].getSTR((start%self.spc),(end%self.spc))
                return buf
            else:
                buf  = self.blocks[start_block].getSTR(start%self.spc,self.spc-start%self.spc)
                for cur_block in range(start_block+1,end_block):
                    buf += self.blocks[cur_block].getSTR(0,self.spc)
                buf += self.blocks[int((end-1)/self.spc)].getSTR(0,end-(start+len(buf)))
                return buf
        else:
            raise KeyError("Can't handle data of type %s" % type(key))

    def getSTR(self,key,length):
        return MultiBlockDataUnpacker.__getitem__(self,slice(key,key+length))
    '''
    def getSTR(self,key,length):
        start = key
        end = key+length

        if int(start/self.spc) == int(end/self.spc):
            return self.blocks[int(key/self.spc)].getSTR((key%self.spc),(key%self.spc+length))
        else:
            buf  = self.blocks[int(start/self.spc)].getSTR(start%self.spc,self.spc-start%self.spc)
            for cur_block in range(int(start/self.spc)+1,int(end/self.spc)):
                buf += self.blocks[cur_block].getSTR(0,self.spc)
            buf += self.blocks[int((end-1)/self.spc)].getSTR(0,end-(start+len(buf)))
            return buf
    '''

