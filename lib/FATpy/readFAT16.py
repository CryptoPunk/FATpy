#!/usr/bin/python
import sys
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
        return self[offset:offset+length]
#        return self._data[offset:offset+length]

class MultiBlockDataUnpacker(DataUnpacker):
    def __init__(self,blocks):
        self.blocks = blocks
        self.spc = len(self.blocks[0])
        for block in self.blocks:
            if not isinstance(block,DataUnpacker):
                raise Exception("MultiBlockDataUnpacker requires the DataUnpacker type, got %s" % block)
            if len(block) != self.spc:
                raise Exception("MultiBlockDataUnpacker requires equal-length blokcs")

    def __len__(self):
        return self.spc * len(self.blocks)

    def __getitem__(self,key):
        print key
        if not isinstance(key,(int,long)):
            raise KeyError("Not a number")
        return self.blocks[int(key/self.spc)][key%self.spc]

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


class Sector(DataUnpacker):
    pass
#    def __init__(self,*args,**kwargs):
#        DataUnpacker.__init__(self,*args,**kwargs)


class Partition():
    def __init__(self,partition):
        self._fh = partition
        self.readBootSector()
        self.readFAT()
        self.readROOT()

    def readSector(self,where=None):
        if where is not None:
            self.seekSector(where)
        return Sector(self._fh.read(self.boot_sector.bps))

    def seekSector(self,where):
        self._fh.seek(where * self.boot_sector.bps)

    def readBootSector(self):
        self.boot_sector = FAT16BootSector(self._fh.read(512))

    def readFAT(self):
        raise Exception("Unimplemented!")

    def readROOT(self):
        raise Exception("Unimplemented!")

class FAT16Partition(Partition):
    def readFAT(self):
        self.fats = []
        self.seekSector(self.boot_sector.reserved_sectors)

        for x in range(self.boot_sector.fat_copies):
            fat = FAT16Table()

            for y in range(self.boot_sector.sectors_per_fat):
                fat.appendSector(self.readFAT16TableSector())

            self.fats.append(fat)
        self.fat = self.fats[0]

    def readFAT16TableSector(self,where=None):
        if where is not None:
            self.seekSector(where)
        return FAT16TableSector(self._fh.read(self.boot_sector.bps))

    def readROOT(self):
        root_sectors = (self.boot_sector.root_entries*32)/self.boot_sector.bps
        self.seekSector(self.boot_sector.reserved_sectors + self.boot_sector.sectors_per_fat * self.boot_sector.fat_copies)
        self.root = FAT16Directory([self.readSector() for x in range(root_sectors)])

    def getClusterChain(self,key):
        chain = [key]
        if self.fat[chain[-1]] == self.fat.end_of_cluster_chain:
            chain.append(self.fat[chain[-1]])
        print chain
        return ClusterChain([self.getCluster(x) for x in chain])

    def getCluster(self,key):
        offset  = self.boot_sector.reserved_sectors
        offset += self.boot_sector.sectors_per_fat * self.boot_sector.fat_copies
        offset += (self.boot_sector.root_entries*32)/self.boot_sector.bps
        if 0 < (self.boot_sector.root_entries*32)%self.boot_sector.bps:
            offset += 1
        offset += 2
        return Cluster([self.readSector(offset+key+x) for x in range(self.boot_sector.spc)])

    def getDirectory(self,key):
        return FAT16Directory(self.getClusterChain(key))

class ClusterChain(MultiBlockDataUnpacker):
    pass
    
class Cluster(MultiBlockDataUnpacker):
    pass
    

class FAT16Directory(MultiBlockDataUnpacker):
    def __init__(self,*args,**kwargs):
        MultiBlockDataUnpacker.__init__(self,*args,**kwargs)
        self.x = 0
    
    def __len__(self):
        return MultiBlockDataUnpacker.__len__(self)/32

    def __getitem__(self,key):
        if not isinstance(key,(int,long)):
            raise KeyError("Not a number")
        return FAT16DirectoryEntry(self.getSTR(key*32,32))

    def __iter__(self):
        return self

    def next(self):
        if (self.x >= len(self)):
            raise StopIteration()
        self.x += 1
        return self[self.x-1]

class FAT16DirectoryEntry(DataUnpacker):
    @property
    def file_name(self):
        return self.getSTR(0,8) + '.' + self.getSTR(8,3)

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

    def media_descriptor(self):
        return self.sectors[0][0] & 0xFF

    def end_of_cluster_chain(self):
        return self.sectors[0][1]

class FAT16TableSector(Sector):
    def __init__(self,*args,**kwargs):
        Sector.__init__(self,*args,**kwargs)
        self.x = 0

    def __getitem__(self,key):
        return self.getWORD(key*2)

    def __len__(self):
        return len(self._data)/2

    def __iter__(self):
        return self

    def next(self):
        if (self.x >= len(self)):
            raise StopIteration()
        self.x += 1
        return self[self.x-1]
        
class FAT16BootSector(Sector):
    @property
    def jumpcode(self):
        '''
        jumpcode:
        Because the MBR transfers CPU execution to the boot sector, the first 
        few bytes of the FAT boot sector must be valid executable instructions
        for an 80x86 CPU. In practice these first instructions constitute a 
        "jump" instruction and occupy the first 3 bytes of the boot sector. 
        This jump serves to skip over the next several bytes which are not 
        "executable."
        '''

        return self.getSTR(0x00,3)

    @property
    def OEM_ID(self):
        '''
        OEM ID:
        Following the jump instruction is an 8 byte "OEM ID".
        This is typically a string of characters that identifies the operating 
        system that formatted the volume.
        '''
        return self.getSTR(0x03,8)

    @property
    def bps(self):
        '''
        Bytes Per Sector: 
        This is the size of a hardware sector and for most disks in use in the
        United States, the value of this field will be 512.
        '''
        return self.getWORD(0x0b)

    @property
    def spc(self):
        '''
        Sectors Per Cluster:
        Because FAT is limited in the number of clusters (or "allocation units")
        that it can track, large volumes are supported by increasing the number
        of sectors per cluster. The cluster factor for a FAT volume is entirely
        dependent on the size of the volume. Valid values for this field are 
        1, 2, 4, 8, 16, 32, 64, and 128. 
        '''
        return self.getBYTE(0x0d)

    @property
    def reserved_sectors(self):
        '''
        Reserved Sectors: 
        This represents the number of sectors preceding the start of the first 
        FAT, including the boot sector itself. It should always have a value of
        at least 1.
        '''
        return self.getWORD(0x0e)

    @property
    def fat_copies(self):
        '''
        FATs:
        This is the number of copies of the FAT table stored on the disk. 
        Typically, the value of this field is 2.
        '''
        return self.getBYTE(0x10)

    @property
    def root_entries(self):
        '''
        Root Entries:
        This is the total number of file name entries that can be stored in
        the root directory of the volume. On a typical hard drive, the value 
        of this field is 512. Note, however, that one entry is always used as a 
        Volume Label, and that files with long file names will use up multiple 
        entries per file. This means the largest number of files in the root 
        directory is typically 511, but that you will run out of entries before
        that if long file names are used.
        '''
        return self.getWORD(0x11)

    @property
    def small_sectors(self):
        '''
        Small Sectors:
        This field is used to store the number of sectors on the disk if the 
        size of the volume is small enough. For larger volumes, this field has 
        a value of 0, and we refer instead to the "Large Sectors" value which 
        comes later.
        '''
        return self.getWORD(0x13)

    @property
    def media_descriptor(self):
        '''
        Media Descriptor: This byte provides information about the media being
        used. The following table lists some of the recognized media descriptor
        values and their associated media. Note that the media descriptor byte
        may be associated with more than one disk capacity.

            Byte   Capacity   Media Size and Type
            F0     2.88 MB    3.5-inch, 2-sided, 36-sector
            F0     1.44 MB    3.5-inch, 2-sided, 18-sector
            F9     720 KB     3.5-inch, 2-sided, 9-sector
            F9     1.2 MB     5.25-inch, 2-sided, 15-sector
            FD     360 KB     5.25-inch, 2-sided, 9-sector
            FF     320 KB     5.25-inch, 2-sided, 8-sector
            FC     180 KB     5.25-inch, 1-sided, 9-sector
            FE     160 KB     5.25-inch, 1-sided, 8-sector
            F8     -----      Fixed disk
        '''
        return self.getBYTE(0x15)

    @property
    def sectors_per_fat(self):
        '''
        Sectors Per FAT:
        This is the number of sectors occupied by each of the FATs on the volume.
        Given this information, together with the number of FATs and reserved 
        sectors listed above, we can compute where the root directory begins. 
        Given the number of entries in the root directory, we can also compute
        where the user data area of the disk begins.
        '''
        return self.getWORD(0x16)

    @property
    def sectors_per_track(self):
        '''
        Sectors Per Track:
        Part of the apparent disk geometry in use when the disk was formatted.
        '''
        return self.getWORD(0x18)

    @property
    def num_heads(self):
        '''
        Heads:
        Part of the apparent disk geometry in use when the disk was formatted.
        '''
        return self.getWORD(0x1A)

    @property
    def num_hidden_sectors(self):
        '''
        Hidden Sectors:
        This is the number of sectors on the physical disk preceding the start
        of the volume. (that is, before the boot sector itself) It is used 
        during the boot sequence in order to calculate the absolute offset to
        the root directory and data areas.
        '''
        return self.getDWORD(0x1C)

    @property
    def large_sectors(self):
        '''
        Large Sectors:
        If the Small Sectors field is zero, this field contains the total 
        number of sectors used by the FAT volume.
        '''
        return self.getDWORD(0x20)

    @property
    def drive_number(self):
        '''
        Physical Drive Number: 
        This is related to the BIOS physical drive number. Floppy drives are
        numbered starting with 0x00 for the A: drive, while physical hard 
        disks are numbered starting with 0x80. Typically, you would set this 
        value prior to issuing an INT 13 BIOS call in order to specify the 
        device to access. The on-disk value stored in this field is typically
        0x00 for floppies and 0x80 for hard disks, regardless of how many 
        physical disk drives exist, because the value is only relevant if 
        the device is a boot device.
        '''
        return self.getBYTE(0x24)

    @property
    def current_head(self):
        '''
        Current Head: This is another field typically used when doing INT13
        BIOS calls. The value would originally have been used to store the
        track on which the boot record was located, but the value stored on
        disk is not currently used as such. Therefore, Windows NT uses this 
        field to store two flags:

          * The low order bit is a "dirty" flag, used to indicate that autochk
            should run chkdsk against the volume at boot time.

          * The second lowest bit is a flag indicating that a surface scan 
            should also be run.

        '''
        return self.getBYTE(0x25)

    @property
    def extended_signature(self):
        '''
        Signature:
        The extended boot record signature must be either 0x28 or 0x29 in order
        to be recognized by Windows NT.
        '''
        return self.getBYTE(0x26)

    @property
    def ID(self):
        '''
        ID: The ID is a random serial number assigned at format time in order
        to aid in distinguishing one disk from another.
        '''
        return self.getDWORD(0x27)

    @property
    def volume_label(self):
        '''
        Volume Label:
        This field was used to store the volume label, but the volume label
        is now stored as a special file in the root directory.
        '''
        return self.getSTR(0x2B,11)

    @property
    def system_id(self):
        '''
        System ID:
        This field is either "FAT12" or "FAT16," depending on the format of 
        the disk.
        '''
        return self.getSTR(0x36,8)

    @property
    def executable_code(self):
        '''
        On a bootable volume, the area following the Extended BIOS Parameter 
        Block is typically executable boot code. This code is responsible for
        performing whatever actions are necessary to continue the boot-strap 
        process. On Windows NT systems, this boot code will identify the 
        location of the NTLDR file, load it into memory, and transfer 
        execution to that file. Even on a non-bootable floppy disk, there is
        executable code in this area. The code necessary to print the familiar
        message, "Non-system disk or disk error" is found on most standard, 
        MS-DOS formatted floppy disks that were not formatted with the "system"
        option.
        '''
        return self.getSTR(0x3E,488)

    @property
    def executable_marker(self):
        '''
        Finally, the last two bytes in any boot sector always have the hexidecimal values: 0x55 0xAA. 
        '''
        return self.getSTR(0x1FE,2)

if __name__ == '__main__':
    partition = open(sys.argv[1],"rb")
    fat16 = FAT16Partition(partition)

    from pprint import pprint
    for f in fat16.root:
        if f.file_name[0] != '\x00':
            if f.subdirectory:
                print f.file_name + "/"
                subdir = fat16.getDirectory(f.starting_cluster)
                for f in subdir:
                    print f.file_name
#                print fat16.getClusterChain(f.starting_cluster)
            else:
                print f.file_name
