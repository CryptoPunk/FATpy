from ..Sector import Sector
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

