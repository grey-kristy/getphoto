#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Require exif-py https://github.com/ianare/exif-py
#

import os
import sys
import re
from datetime import datetime
from shutil import copyfile
import EXIF

MOUNT_DIR   = '/Volumes'
TARGET_DIR  = 'Pictures/Photo'   # ~/$TARGET_DIR


def get_exif_date(fname):
    f = open(fname, 'rb')
    tags = EXIF.process_file(f, details=False, stop_tag='DateTimeOriginal')
    f.close()
    return tags['EXIF DateTimeOriginal']

def get_dcim_dirs():
    for dir in os.listdir(MOUNT_DIR):
        for subdir in os.listdir(MOUNT_DIR+'/'+dir):
            if not os.path.isdir(os.path.join(MOUNT_DIR,dir,subdir)):
                continue
            if subdir == 'DCIM':
                break
        else:
            continue
        break
    path = '%s/%s/%s' % (MOUNT_DIR, dir, subdir)
    return ['%s/%s' % (path, dir) for dir in os.listdir(path) if dir != 'MISC']

def make_dir(d, suff, title):
    dir = "%s/%s/%4d/%02d_%02d_%s/%s" % (
        os.getenv("HOME"), TARGET_DIR, d.year, d.month, d.day, title, suff
    )
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def copy_raw(dir, title, old_date=None):
    MONTHS = ('','Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    new_dir = None
    dir_date = None
    for fname in os.listdir(dir):
        path_name = '%s/%s' % (dir, fname) 
        try: 
            date = get_exif_date(path_name)
        except KeyError:
            continue

        suff = re.search('\.([^.]+)$', fname).group(1).lower()
        d = datetime.strptime(str(date), '%Y:%m:%d %H:%M:%S')
        new_fname = '%04d%s%02d_%02d%02d%02d.%s' % (
            d.year, MONTHS[d.month], d.day, d.hour, d.minute, d.second, suff
            )

        if not new_dir:
            if old_date:
                dir_date = old_date
            else:
                dir_date = date
            dd = datetime.strptime(str(dir_date), '%Y:%m:%d %H:%M:%S')            
            new_dir = make_dir(dd, suff, title)

        new_file = new_dir+'/'+new_fname
        if os.path.exists(new_file):
            print "error: file %s already exist" % new_file
        else:
            print "copy %s %s" % (path_name, new_file)
            copyfile(path_name, new_file)
            pass
    return dir_date

def get_title():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        print "Usage: %s 'event title'" % (os.path.basename(sys.argv[0]))
        sys.exit(1)

def main():
    title = get_title()
    old_date = None
    for dir in get_dcim_dirs():
        new_date = copy_raw(dir, title, old_date)    
        old_date = new_date    

main()
