import os
import ctypes
import ctypes.util

# libc = ctypes.CDLL(None)
libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
libc.mount.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p)

# Constants from https://github.com/karelzak/util-linux/blob/master/include/namespace.h
CLONE_NEWNS = 0x00020000
CLONE_NEWCGROUP = 0x02000000
CLONE_NEWUTS = 0x04000000
CLONE_NEWIPC = 0x08000000
CLONE_NEWNET = 0x40000000
CLONE_NEWUSER = 0x10000000
CLONE_NEWPID = 0x20000000
CLONE_NEWTIME = 0x00000080

MS_NOSUID = 0x2
MS_STRICTATIME = 0x1000000
MS_PRIVATE = 0x40000
MS_REC = 0x4000

MNT_DETACH = 0x2


def mount(source, target, filesystemtype, mountflags = 0, data=''):
    rc = libc.mount(source.encode(), target.encode(), filesystemtype.encode(), mountflags, data.encode())
    if rc < 0:
        errno = ctypes.get_errno()
        raise Exception(os.strerror(errno))


def unshare(flags):
    rc = libc.unshare(flags)
    if rc < 0:
        errno = ctypes.get_errno()
        raise Exception(os.strerror(errno))


def unmount(device, options=0):
    ret = libc.umount2(device.encode(), options)
    if ret < 0:
        errno = ctypes.get_errno()
        raise Exception(os.strerror(errno))
