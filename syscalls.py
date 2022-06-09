from enum import Flag
import os
import ctypes


libc = ctypes.CDLL(None)

get_errno_loc = libc.__errno_location
get_errno_loc.restype = ctypes.POINTER(ctypes.c_int)

# Constants from https://github.com/karelzak/util-linux/blob/master/include/namespace.h
CLONE_NEWNS = 0x00020000
CLONE_NEWCGROUP = 0x02000000
CLONE_NEWUTS = 0x04000000
CLONE_NEWIPC = 0x08000000
CLONE_NEWNET = 0x40000000
CLONE_NEWUSER = 0x10000000
CLONE_NEWPID = 0x20000000
CLONE_NEWTIME = 0x00000080


def mount(source, target, fst, flags = 0):
    rc = libc.mount(source.encode(), target.encode(), fst.encode(), flags)
    if rc == -1:
        raise Exception(os.strerror(get_errno_loc()[0]))


def unshare(flags):
    rc = libc.unshare(flags)
    if rc == -1:
        raise Exception(os.strerror(get_errno_loc()[0]))





