import sys,os
sys.path.append('lib')
import FATpy

if __name__ == '__main__':
    partition = open(sys.argv[1],"rb")
    fat16 = FATpy.FAT16.FAT16Partition(partition)
    path = sys.argv[2].strip('/').split('/')
    cur_node = fat16.root
    cur_direntry = None
    for part in path:
        found = False
        if not isinstance(cur_node,FATpy.FAT16.FAT16Directory.FAT16Directory):
            raise Exception("Part of the path is a file!: %s" % part)
        for f in cur_node:
            if f.file_name.upper() == part.upper():
                found = True
                cur_direntry = f
                if f.subdirectory:
                    cur_node = fat16.getDirectory(f.starting_cluster)
                else:
                    cur_node = fat16.getClusterChain(f.starting_cluster)
        if not found:
            raise Exception("Can't find file: %s" % part)
    if isinstance(cur_node,FATpy.FAT16.FAT16Directory.FAT16Directory):
        for f in cur_node:
            if f.file_name == "\x00\x00\x00\x00\x00\x00\x00\x00.\x00\x00\x00":
                continue
            if f.subdirectory:
                print "%s/\t%d" % (f.file_name, f.filesize)
            else:
                print "%s\t%d" % (f.file_name, f.filesize)
    else:
        fh = open(cur_direntry.file_name,'wb')
        fh.write(cur_node[0:cur_direntry.filesize])
        fh.close()
