from ..DataUnpacker import DataUnpacker
class FAT16DirectoryEntry(DataUnpacker):
    @property
    def file_name(self):
        if '   ' != self.getSTR(8,3):
            return self.getSTR(0,8).rstrip(' ') + '.' + self.getSTR(8,3).rstrip(' ')
        else:
            return self.getSTR(0,8).rstrip(' ')

    @property
    def attributes(self):
        '''
        Attributes: a bitvector.
            Bit 0: read only.
            Bit 1: hidden.
            Bit 2: system file.
            Bit 3: volume label.
            Bit 4: subdirectory.
            Bit 5: archive.
            Bits 6-7: unused.
        '''
        return self.getBYTE(11)

    @property
    def readonly(self):
        return bool(self.attributes & 1)

    @property
    def hidden(self):
        return bool(self.attributes & 1 << 1)

    @property
    def system(self):
        return bool(self.attributes & 1 << 2)

    @property
    def volume_label(self):
        return bool(self.attributes & 1 << 3)

    @property
    def subdirectory(self):
        return bool(self.attributes & 1 << 4)

    @property
    def archive(self):
        return bool(self.attributes & 1 << 5)

    @property
    def time(self):
        '''
        Time (5/6/5 bits, for hour/minutes/doubleseconds)
        '''
        return self.getWORD(22)

    @property
    def date(self):
        '''
        Date (7/4/5 bits, for year-since-1980/month/day)
        '''
        return self.getWORD(24)

    @property
    def starting_cluster(self):
        '''
        Starting Cluster (or 0 for an empty file)
        '''
        return self.getWORD(26)

    @property
    def filesize(self):
        '''
        Filesize in bytes
        '''
        return self.getDWORD(28)
