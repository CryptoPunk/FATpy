from ..MultiBlockDataUnpacker import MultiBlockDataUnpacker
from .FAT16DirectoryEntry import FAT16DirectoryEntry
class FAT16Directory(MultiBlockDataUnpacker):
    def __init__(self,*args,**kwargs):
        MultiBlockDataUnpacker.__init__(self,*args,**kwargs)
        self.x = 0
    
    def __len__(self):
        return MultiBlockDataUnpacker.__len__(self)/32

    def __getitem__(self,key):
        if isinstance(key,(int,long)):
            return FAT16DirectoryEntry(self.getSTR(key*32,32))
        else:
            raise KeyError("Not a number")

    def __iter__(self):
        return self

    def next(self):
        if (self.x >= len(self)):
            raise StopIteration()
        self.x += 1
        return self[self.x-1]
