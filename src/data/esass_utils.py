import errno
import os
import sys


def rm_file(f_name):
    if os.path.isfile(f_name) is True:
        os.remove(f_name)


def preclear(*arg):
    for files in arg:
        if isinstance(files, str):
            rm_file(files)
        elif isinstance(files, list):
            for f in files:
                rm_file(f)
        else:
            sys.exit(f'ERROR: {files}')


def make_dir(dir_to_make):
    try:
        os.makedirs(dir_to_make)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
