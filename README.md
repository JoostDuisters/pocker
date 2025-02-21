# Building your own docker

In this repository I recreate a minimal version of Docker in several 100s of lines of Python.

My interest in this topic was initially sparked by [bocker](https://github.com/p8952/bocker), a simple bash script that manages to "implement" docker in about 100 lines of Bash (as you can see, I haven't been very original with the name of this project either). 

## Creating the Docker run command

We're going to use the above image as our starting point. We start with the following scaffolding code:
```python
import os
import sys
from typing import List


def pocker_run(cmd: List[str], image_dir: str):

    pid = os.fork()
    # Below gets run twice, once inside and once outside container
    if pid == 0:
        # Inside container
        print("Inside new process")
        os.chroot(image_dir)
        os.chdir('/')
        os.execvp(cmd[0], cmd)
    else:
        print('Inside old process')

image_dir = "/home/ubuntu/images/ubuntu/a8c4dc1e399c44d5e7eeb14e2cb5fa65c9c724562ade5aa82c2ab69a82cc537f/layer/"
cmd = sys.argv[1:]
pocker_run(cmd, image_dir)
```

This code by itsself creates a subprocess and executes it with our image as it's root. I will be adding the steps to isolate this process between the print line :`print("Inside new process")` and the line that executes the command: `os.execvp(cmd[0], cmd)`. I will isolate each of the step as isolated python functions like so:

```python
import os
import sys
from typing import List


def pocker_run(cmd: List[str], image_dir: str):

    pid = os.fork()
    # Below gets run twice, once inside and once outside container
    if pid == 0:
        # Inside container
        print("Inside new process")
        _create_mount_namespace()
        _create_proc_folder()
        _create_sys_folder()
        _create_temp_folder()
        _create_dev_folder()

        os.chroot(image_dir)
        os.chdir('/')
        os.execvp(cmd[0], cmd)
    else:
        print('Inside old process')

image_dir = "/home/ubuntu/images/ubuntu/a8c4dc1e399c44d5e7eeb14e2cb5fa65c9c724562ade5aa82c2ab69a82cc537f/layer/"
cmd = sys.argv[1:]
pocker_run(cmd, image_dir)
```
# TODO: update once actually finalized



