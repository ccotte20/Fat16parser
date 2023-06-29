# Clark Otte
# Lab03 Fat 16 Part 2
# CSC 5347
# April 14, 2022
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

# class for storing file info from root directory
class fatfile:
    def __init__(self, filename, start, size):
        self.filename = filename
        self.start = start
        self.size = size
    def getString(self):
        return "{} Start: {} Size: {}".format(self.filename, self.start, self.size)
    

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

    # go to start/end of root directory and start list of files
    root_dir_start = bytes_per_sector+num_of_FATS*size_of_FATS*bytes_per_sector
    print("Root Directory Start: {}".format(root_dir_start))    
    root_dir_end = root_dir_start + 512*32
    ListOfFiles = []
    
    # read the root directory and store the files
    infile.seek(root_dir_start)
    i = 0
    while(infile.read(1)!= b'\x00'):
        infile.seek(root_dir_start+i)
        fbyte = infile.read(1)
        if(fbyte == b'A'):
            i = i + 32
            infile.seek(root_dir_start+i)
            filename = infile.read(8)
            fileext = infile.read(3)
            filename = "{}.{}".format(filename.decode().rstrip(), fileext.decode())
            
            infile.read(15)
            data = infile.read(2)
            filestart = struct.unpack("<H",data[0:len(data)])[0]
            
            data = infile.read(4)
            filesize = struct.unpack("<I",data[0:len(data)])[0]
            
            file = fatfile(filename, filestart, filesize)
            ListOfFiles.append(file)
            
            i = i + 32
        elif(fbyte == b'\xe5'):
            i = i + 32
            infile.seek(root_dir_start+i+1)
            filename = infile.read(7)
            fileext = infile.read(3)
            filename = "_{}.{}".format(filename.decode().rstrip(), fileext.decode())
            
            infile.read(15)
            data = infile.read(2)
            filestart = struct.unpack("<H",data[0:len(data)])[0]
            
            data = infile.read(4)
            filesize = struct.unpack("<I",data[0:len(data)])[0]
            
            file = fatfile(filename, filestart, filesize)
            ListOfFiles.append(file)
            
            i = i + 32
        else:
            i = i + 64
    
    # print out the list of files
    print("List of files")
    i=0
    for file in ListOfFiles:
        print("File[{}]: {}".format(i, file.getString()))
        i=i+1
    # start the user interaction
    print("Enter the number next to File you wish to download. Enter -1 to download all files. Enter -2 to exit.")
    choice = int(input("Enter Choice: "))
    
    # run program until exit. Gets the file size and start, reads cluster and finds next cluster if there is one
    while(choice != -2):
        if(choice == -1):
            for file in ListOfFiles:
                bleft = file.size
                cluster = file.start
                outfile = open(file.filename,'wb')
                while(bleft!=0):
                    infile.seek(root_dir_end+cluster*bytes_per_sector)
                    if(bleft>512):
                        data = infile.read(512)
                        bleft = bleft-512
                    else:
                        data = infile.read(bleft)
                        bleft = 0
                    outfile.write(data)
                    infile.seek(512+2*cluster)
                    nextcluster = infile.read(2)
                    cluster = struct.unpack("<H",data[0:len(nextcluster)])[0]
                outfile.close()
        else:
            bleft = ListOfFiles[choice].size
            cluster = ListOfFiles[choice].start
            outfile = open(ListOfFiles[choice].filename,'wb')
            while(bleft!=0):
                infile.seek(root_dir_end+cluster*bytes_per_sector)
                if(bleft>512):
                    data = infile.read(512)
                    bleft = bleft-512
                else:
                    data = infile.read(bleft)
                    bleft = 0
                outfile.write(data)
                infile.seek(512+2*cluster)
                nextcluster = infile.read(2)
                cluster = struct.unpack("<H",data[0:len(nextcluster)])[0]
            outfile.close()
        choice = int(input("Enter Choice: "))
    infile.close()
if __name__ == "__main__":
    main(sys.argv)