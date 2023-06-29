# Clark Otte
# Lab03 Fat 16
# CSC 5347
# March 27, 2022
# This program assumes the target file is in the same directory as the program file.
# To run this program, run as normal with the filename of the disk drive as an additional argument.  For example 'python3 fat16parser.py fatImg.dd'
# Deleted files will be listed with an underscore as the first character of their name.
import subprocess
import os
import shutil
import argparse
import sys
import struct
import re

def main(argv):
    
    infile = open(sys.argv[1],'rb')
    
    # get bytes per sector
    infile.seek(11)
    data = infile.read(2)
    bytes_per_sector = struct.unpack("<H",data[0:len(data)])[0]
    print("Bytes per sector: {}".format(bytes_per_sector))
    
    # get sectors per cluster
    infile.seek(13)
    data = infile.read(1)
    sectors_per_cluster = struct.unpack("<H", data + b'\x00')[0]
    print("Sectors per cluster: {}".format(sectors_per_cluster))
    
    # get total number of sectors
    infile.seek(19)
    data = infile.read(2)
    total_sectors = struct.unpack("<H",data[0:len(data)])[0]
    print("Total sectors: {}".format(total_sectors))
    
    # get number of FATs
    infile.seek(16)
    data = infile.read(1)
    num_of_FATS = struct.unpack("<H", data + b'\x00')[0]
    print("Number of FATs: {}".format(num_of_FATS))

    # get size of FATS
    infile.seek(22)
    data = infile.read(2)
    size_of_FATS = struct.unpack("<H",data[0:len(data)])[0]
    print("Size of FATs: {}".format(size_of_FATS))

    # go to start of root directory and read files
    root_dir_start = bytes_per_sector+num_of_FATS*size_of_FATS*bytes_per_sector
    print("Root Directory Start: {}".format(root_dir_start))    
    print("List of files")
    infile.seek(root_dir_start)
    i = 0
    while(infile.read(1)!= b'\x00'):
        infile.seek(root_dir_start+i)
        if(infile.read(1) == b'A'):
            i = i + 32
            infile.seek(root_dir_start+i)
            filename = infile.read(8)
            fileext = infile.read(3)
            print("{}.{}".format(filename.decode().rstrip(), fileext.decode()))
            i = i + 32
        else:
            i = i + 64
            
    # go to start of root directory and read deleted files
    print("List of deleted files")
    infile.seek(root_dir_start)
    i = 0
    while(infile.read(1)!= b'\x00'):
        infile.seek(root_dir_start+i)
        if(infile.read(1) == b'\xe5'):
            i = i + 32
            infile.seek(root_dir_start+i+1)
            filename = infile.read(7)
            fileext = infile.read(3)
            print("_{}.{}".format(filename.decode().rstrip(), fileext.decode()))
            i = i + 32
        else:
            i = i + 64
    infile.close()
if __name__ == "__main__":
    main(sys.argv)