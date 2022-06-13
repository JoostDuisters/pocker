import os
import sys
from typing import List
import syscalls
from pathlib import Path


def _create_mount_namespace(image_dir: Path):
    """
    The first linux namespace that was created was the mount namespace. It can be invoked with the syscalls 
    UNSHARE or CLONE, with the CLONE_NEWNS flag. 
    """
    try:
        # Unshare
        syscalls.unshare(syscalls.CLONE_NEWNS)
    except RuntimeError as e:
        print(f'Error in unshare: {e}')

    syscalls.mount('', '/', '', syscalls.MS_PRIVATE | syscalls.MS_REC, '')

    # Mount 3 important systems: proc, sys and dev
    syscalls.mount('proc', str(image_dir.joinpath('proc')), 'proc')
    syscalls.mount('sysfs', str(image_dir.joinpath('sys')), 'sysfs')
    syscalls.mount('tmpfs', str(image_dir.joinpath('dev')), 'tmpfs', syscalls.MS_NOSUID | syscalls.MS_STRICTATIME, 'mode=755')

    # Separately mount /dev/pts
    os.mkdir(image_dir.joinpath('dev').joinpath('pts'))
    syscalls.mount('devpts', str(image_dir.joinpath('dev').joinpath('pts')), 'devpts')

    # Add important devices to dev


def pocker_run(cmd: List[str], image_dir: Path):

    pid = os.fork()
    # Below gets run twice, once inside and once outside container
    if pid == 0:
        # Inside container
        print("Inside new process")

        _create_mount_namespace(image_dir)

        os.chroot(image_dir)
        os.chdir('/')
        os.execvp(cmd[0], cmd)
    else:
        print('Inside old process')

image_dir = Path("/home/ubuntu/images/ubuntu/a8c4dc1e399c44d5e7eeb14e2cb5fa65c9c724562ade5aa82c2ab69a82cc537f/layer/")
cmd = sys.argv[1:]
pocker_run(cmd, image_dir)
