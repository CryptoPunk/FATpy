class FAT16Table():
    def __init__(self):
        self.sectors = []
        self.x = 0

    def __len__(self):
        return len(self.sectors[0]) * len(self.sectors)

    def __getitem__(self,key):
        if not isinstance(key,(int,long)):
            raise KeyError("Not a number")
        cpb = len(self.sectors[0])
        return self.sectors[int(key/cpb)][key%cpb]

    def __iter__(self):
        return self

    def next(self):
        if (self.x >= len(self)):
            raise StopIteration()
        self.x += 1
        return self[self.x-1]
        
    def appendSector(self,sector):
        self.sectors.append(sector)

    @property
    def media_descriptor(self):
        return self.sectors[0][0] & 0xFF

    @property
    def end_of_cluster_chain(self):
        return self.sectors[0][1]
