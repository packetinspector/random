#!/usr/bin/python

import sys
import os
import shutil

#Grab the arguments
#print sys.argv
try:
    (scriptname, directory, orgnzbname, jobname, reportnumber, category, group, postprocstatus) = sys.argv
except:
    print "Missing commandline parameters"
    sys.exit(1)

# continue script
dir_final = '/final/directory/tvshows/'
dir_final_left = '/path/to/leftovers/'

movie_extensions = ['avi', 'mkv', 'wmv', 'mp4', 'ts', 'img', 'iso', 'sub', 'idx', 'srt']
def_remove = ['jpeg', 'jpg', 'url', 'exe', 'png']


if not os.path.exists(directory):
    print "Directory is gone"
    sys.exit(1)


def move_to_left(item_root, item, item_type):
    pass

'''
if str(category) != 'tv' or str(reportnumber) != 'tv':
    print "This is only for TV"
    sys.exit(1)
'''
#Init
leftover = 0


print "Searching %s for renaming and moving" % directory
print "Files will use name: %s" % jobname
print
files = os.listdir(directory)
for f in files:

    full_path = os.path.join(directory, f)
    print "[ %s ]" % f,
    if os.path.isfile(full_path):
        print "is file",
        try:
            root, ext = os.path.splitext(f)
        except:
            print "\tError Splitting Filename"
            continue

        ext = ext.replace('.', '')
        #print "%s , %s" % (root, ext)
        print "with %s extension" % ext

        if ext in def_remove:
            print "\tRemoving %s" % f
            os.remove(full_path)
            continue

        if ext in movie_extensions:
            #We want these things
            new_f = jobname + '.' + ext
            new_path = os.path.join(dir_final, new_f)
            print "\tMoving [ %s ]\n\tto [ %s ]" % (full_path, new_path)
            #Use While exists to cover multiples...
            dupe_counter = 0
            while os.path.exists(new_path):
                print "\tFile Exists. Renaming."
                dupe_counter += 1
                new_path = os.path.join(dir_final, jobname + '-' + str(dupe_counter) + '.' + ext)
            os.utime(full_path, None)
            os.rename(full_path, new_path)
            continue

        print "\tUnknown Filetype. Moving to leftovers"
        full_left = os.path.join(dir_final_left, jobname)
        if not os.path.exists(full_left):
            os.mkdir(full_left)
        #Retain original filename
        os.rename(full_path, os.path.join(full_left, f))
        leftover += 1

    elif os.path.isdir(full_path):

        print "is a directory"
        print "\tNo support for directory, moving to leftovers"
        full_left = os.path.join(dir_final_left, jobname)
        if not os.path.exists(full_left):
            os.mkdir(full_left)
        temp_dir = os.path.join(full_left, f)
        if os.path.exists(temp_dir):
            print "\tDirectory Already Exists. Removing"
            shutil.rmtree(full_path, ignore_errors=True)
            continue

        shutil.move(full_path, full_left)
        leftover += 1

    else:

        print "some other type"

#All done. Directory should be empty by now.
if not os.listdir(directory):
    os.rmdir(directory)
    if leftover > 0:
        print "You have leftovers"
    sys.exit(0)
else:
    print "Dir Not Empty"
    sys.exit(1)
