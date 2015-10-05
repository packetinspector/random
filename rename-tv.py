#!/usr/bin/python

import sys
import os
import shutil

#Grab the arguments
try:
    (scriptname, directory, orgnzbname, jobname, reportnumber, category) = sys.argv
except:
    print "Missing commandline parameters"
    sys.exit(1)

# continue script

dir_final = '/my/tv/dir/'
dir_final_left = '/my/download/leftovers/'

movie_extensions = ['avi', 'mkv', 'wmv', 'mp4', 'ts', 'img', 'iso', 'sub', 'idx', 'srt']
def_remove = ['jpeg', 'jpg', 'url', 'exe']


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

print "Searching %s for renaming and moving" % directory
print "Files will use name: %s" % jobname 
files = os.listdir(directory)
for f in files:

    full_path = os.path.join(directory, f)
    print "Examining (%s)" % f,
    if os.path.isfile(full_path):
        print "type file"
        try:
            root, ext = os.path.splitext(f)
        except:
            print "\tError Splitting Filename"
            continue

        ext = ext.replace('.', '')
        #print "%s , %s" % (root, ext)
        print "\tChecking out %s extension type" % ext

        if ext in def_remove:
            print "\tRemoving %s" % f
            os.remove(full_path)
            continue

        if ext in movie_extensions:
            #We want these things
            new_f = jobname + '.' + ext
            new_path = os.path.join(dir_final, new_f)
            print "\tMoving (%s)\n\tto (%s)" % (full_path, new_path)
            if os.path.exists(new_path):
                print "\tFile Exists. Renaming."
                new_path = os.path.join(dir_final, jobname + '-1.' + ext)
            os.utime(full_path, None)
            os.rename(full_path, new_path)
            continue

        print "Unknown Filetype. Moving to leftovers"
        full_left = os.path.join(dir_final_left, jobname)
        if not os.path.exists(full_left):
            os.mkdir(full_left)

        os.rename(full_path, full_left)

    elif os.path.isdir(full_path):

        print "type dir"
        print "\tNo support for directory, moving to leftovers"
        full_left = os.path.join(dir_final_left, jobname)
        if not os.path.exists(full_left):
            os.mkdir(full_left)
        shutil.move(full_path, full_left)
 
    else:

        print "some other type"

#All done. Directory should be empty by now.
if not os.listdir(directory):
    os.rmdir(directory)
    sys.exit(0)
else:
    print "Dir Not Empty"
    sys.exit(1)
