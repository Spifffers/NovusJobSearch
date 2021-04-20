import os, fnmatch, sys, time
import tkinter as tk
from os.path import join, getsize
print ('')

# first attempt.  Apparently os.walk retrieves all the file information about each file which makes it functional but slow
def walkdirs(path, find):
    total1 = 0
    total2 = 0
    for root, dir, files in os.walk(path):
        for dirName in dir:
            total1 += 1
            #using if string1 in string2 is easier but won't let you use wildcards
            if fnmatch.fnmatch(dirName, '*' + find + '*'):
               total2 += 1
               #print(dirName)
    return total1, total2

#The scandir function returns an iterator to a list of file objects.  It is significantly faster than os.walk or os.listdir
#   because those two retrieve all the file information for each file as it makes the original list
#This function was my attempt at making a recursive function.  The problem is that it spent all it's time recursing down
#   into subdirectories that were never going to have the job numbers were looking for.  It's functional but way too slow
def recursesubdirs(path, find):
    total1 = 0
    total2 = 0
    for entry in os.scandir(path):
        if(entry.is_dir()):
            dirCounts = recursesubdirs(entry.path, find)
            total1 += dirCounts[0]
            total1 += 1
            total2 += dirCounts[1]
            if fnmatch.fnmatch(entry.path, '*' + find + '*'):
               total2 += 1
               print(entry.path, "YES")
               return total1, total2
            print(entry.path, "NO")
    return total1, total2          

# This was an attempt to do a breadth first search instead of depth. in was supposed to search all the files in a directory before recursively 
#   going deeper into each one. I think it works but it was still too slow because there are so many directories we know are
#   incorrect and shouldn't bother searching at all.
def recursesubdirsfast(path, find):
    total1 = 0
    total2 = 0
    #dirs = os.scandir(path)
    # scan all dirs for search string
    for entry in os.scandir(path):
        if(entry.is_dir()):
            total1 += 1
            if fnmatch.fnmatch(entry.path, '*' + find + '*'):
               total2 += 1
               print(entry.path, "YES")
               return total1, total2
 #           print(entry.path, "NO")
    # scan all subdirs for search string
    for entry in os.scandir(path):
        if(entry.is_dir()):
            dirCounts = recursesubdirsfast(entry.path, find)
            total1 += dirCounts[0]
            total2 += dirCounts[1]
            if(total2 > 0):
                return total1, total2
    return total1, total2  
   
   
# My best attempt.  It uses this first function just to go into the Projects or Jobs folder.  then calls another function to search 
#   all the directory names.  I was tryign to do some recursive stuff but abandoned that.  This could all be done in one function 
#   with nested if statements.
# It returns both the number of directories scanned and the found count.  It quits after finding one so the found Count isn't that useful
def findfastfiltered(path, find):
    scannedCount = 0
    foundCount = 0
    # scan all top level dirs
    for entry in os.scandir(path):
        #print("scanning", entry.path)      # eg n:\Calgary
        # expect a Project directory
        if(os.path.isdir(os.path.join(entry.path, 'Projects'))):
            print("\n scanning   ", os.path.join(entry.path, 'Projects'))   # eg n:\Calgary\Projects
            dirCounts = findsubdirs(os.path.join(entry.path, 'Projects'), find)
            scannedCount += dirCounts[0]
            foundCount += dirCounts[1]
            # if we want the entire script to quit as soon as once match happens, return here if foundCount > 0
            if(foundCount > 0):
                return scannedCount, foundCount
        # or exepct a Jobs directory (guelph 2020 and 2021 are like this)
        elif (os.path.isdir(os.path.join(entry.path, 'Jobs'))):
            print("\n scanning   ", os.path.join(entry.path, 'Jobs'))
            dirCounts = findsubdirs(os.path.join(entry.path, 'Jobs'), find)
            scannedCount += dirCounts[0]
            foundCount += dirCounts[1]
            # if we want the entire script to quit as soon as once match happens, return here if foundCount > 0
            if(foundCount > 0):
                return scannedCount, foundCount
    return scannedCount, foundCount      

# to make this work as quickly as possible i had to essentially know the expected directory structure and only 
#   search the pertinent directories.  Doing it iteratively over everything was too slow.
def findsubdirs(path, find):
    # search for both job numbers with . or - no matter what the user requested
    findString1  = find.replace('.', '-')
    findString2 = find.replace('-', '.')

    scannedCount = 0
    foundCount = 0
    skippedCount = 0
    currentdir = path
    for entry in os.scandir(path):
        if(entry.is_dir()):
            # some of the directories are read only and python fails when trying to get the subdirs of it. Needed a try/except statement
            try :
                currentdir = entry.path
                #print("scanning      ", entry.path)   # eg n:\Calbgary\Projects\ClientName
                # print out # characters without a newline just to let you know it's doing something
                print("#",end="",flush=True)
                for subentry in os.scandir(entry.path):
                    currentdir = subentry.path
                    if(subentry.is_dir()):
                        # guelph 2020 and 20201 have a specific path n:\guelph\jobs\2021\Jobs\jobnumber
                        if fnmatch.fnmatch(subentry.path, '*' + 'Jobs' + '*' + 'Jobs'):
                            #print("looking", subentry.path) 
                            print("#",end="",flush=True)
                            for subsubentry in os.scandir(subentry.path):
                                #print("snooping", subsubentry.path)
                                currentdir = subsubentry.path
                                # search for both the string with . and with -
                                if (findString1 in subsubentry.path) or (findString2 in subsubentry.path):
                                    foundCount += 1
                                    print("\nFOUND!--->  ", subsubentry.path)
                                    return scannedCount, foundCount
                        # all other directorys have n:\calgary\Projects\clientname\jobnumber            
                        else:
                            #print("checking         ", subentry.path)  # eg n:\Calbgary\Projects\ClientName\Jobname
                            scannedCount += 1
                            if (findString1 in subentry.path) or (findString2 in subentry.path):
                                foundCount += 1
                                print("\nFOUND!--->  ", subentry.path)
                                return scannedCount, foundCount
            except PermissionError:
                print("\nERROR permissions denied ", currentdir)
    return scannedCount, foundCount  
   
# This is for when i allowed command line arguments to the python script   
#findString1  = str(sys.argv[2]).replace('.', '-')
#print ('Searching for ', '*' + findString1 + '*')
#findString2 = str(sys.argv[2]).replace('-', '.')
#print ('Searching for ', '*' + findString2 + '*\n')
    
commandFind = input('Enter Search String : ')

findString1  = str(commandFind).replace('.', '-')
print ('Searching for ', '*' + findString1 + '*')
findString2 = str(commandFind).replace('-', '.')
print ('Searching for ', '*' + findString2 + '*\n')
    
start1 = time.perf_counter()    
#dircount = findfastfiltered(str(sys.argv[1]), str(sys.argv[2]))
dircount = findfastfiltered('n:', commandFind)
end1 = time.perf_counter()
print("\nsubdir dircount is", dircount, "directories in ", end1 - start1, "s")

commandFind = input('Press any key to exit')

