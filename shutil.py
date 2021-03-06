# File: s (Python 2.4)

import os
import sys
import stat
import exceptions
from os.path import abspath
__all__ = [
    'copyfileobj',
    'copyfile',
    'copymode',
    'copystat',
    'copy',
    'copy2',
    'copytree',
    'move',
    'rmtree',
    'Error']

class Error(exceptions.EnvironmentError):
    pass


def copyfileobj(fsrc, fdst, length = 16 * 1024):
    while None:
        buf = fsrc.read(length)
        if not buf:
            break
        


def _samefile(src, dst):
    if hasattr(os.path, 'samefile'):
        
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False
        

    return os.path.normcase(os.path.abspath(src)) == os.path.normcase(os.path.abspath(dst))


def copyfile(src, dst):
    if _samefile(src, dst):
        raise Error, '`%s` and `%s` are the same file' % (src, dst)
    
    fsrc = None
    fdst = None
    
    try:
        fsrc = open(src, 'rb')
        fdst = open(dst, 'wb')
        copyfileobj(fsrc, fdst)
    finally:
        if fdst:
            fdst.close()
        
        if fsrc:
            fsrc.close()
        



def copymode(src, dst):
    if hasattr(os, 'chmod'):
        st = os.stat(src)
        mode = stat.S_IMODE(st.st_mode)
        os.chmod(dst, mode)
    


def copystat(src, dst):
    st = os.stat(src)
    mode = stat.S_IMODE(st.st_mode)
    if hasattr(os, 'utime'):
        os.utime(dst, (st.st_atime, st.st_mtime))
    
    if hasattr(os, 'chmod'):
        os.chmod(dst, mode)
    


def copy(src, dst):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    
    copyfile(src, dst)
    copymode(src, dst)


def copy2(src, dst):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    
    copyfile(src, dst)
    copystat(src, dst)


def copytree(src, dst, symlinks = False):
    names = os.listdir(src)
    os.mkdir(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                copy2(srcname, dstname)
        continue
        except (IOError, os.error):
            why = None
            errors.append((srcname, dstname, why))
            continue
        

    
    if errors:
        raise Error, errors
    


def rmtree(path, ignore_errors = False, onerror = None):
    if ignore_errors:
        
        def onerror(*args):
            pass

    elif onerror is None:
        
        def onerror(*args):
            raise 

    
    names = []
    
    try:
        names = os.listdir(path)
    except os.error:
        err = None
        onerror(os.listdir, path, sys.exc_info())

    for name in names:
        fullname = os.path.join(path, name)
        
        try:
            mode = os.lstat(fullname).st_mode
        except os.error:
            mode = 0

        if stat.S_ISDIR(mode):
            rmtree(fullname, ignore_errors, onerror)
            continue
        
        try:
            os.remove(fullname)
        continue
        except os.error:
            err = None
            onerror(os.remove, fullname, sys.exc_info())
            continue
        

    
    
    try:
        os.rmdir(path)
    except os.error:
        onerror(os.rmdir, path, sys.exc_info())



def move(src, dst):
    
    try:
        os.rename(src, dst)
    except OSError:
        if os.path.isdir(src):
            if destinsrc(src, dst):
                raise Error, "Cannot move a directory '%s' into itself '%s'." % (src, dst)
            
            copytree(src, dst, symlinks = True)
            rmtree(src)
        else:
            copy2(src, dst)
            os.unlink(src)
    except:
        os.path.isdir(src)



def destinsrc(src, dst):
    return abspath(dst).startswith(abspath(src))

