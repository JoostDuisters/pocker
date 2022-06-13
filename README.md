# Building your own docker

In this repository I recreate a minimal version of Docker in several 100s of lines of Python. Just as an initial disclaimer: it is not a good idea to rewrite Docker in Python as it's not really the right language for it (better would be to use C/C++ or Go for instance). However this exercise does give a lot of fascinating insights into what a container really is, and how (Docker) images work.

My interest in this topic was initially sparked by [bocker](https://github.com/p8952/bocker), a simple bash script that manages to "implement" docker in about 100 lines of Bash (as you can see, I haven't been very original with the name of this project either). 

## Intro

### What is a container?
In my experience definitions of Docker often come in two flavours: either people describe it as a tool to package and ship your applications, or they describe it as a VM that can run on another machine (your own laptop for instance). Both are actually pretty good descriptions of what Docker does. The former description largely captures Dockers' ablity to build images from a set of instructions in a Dockerfile, whereas the later actually describes the container runtime. 

Interestingly, Docker doesn't implement their own container runtime. They use [containerd](https://containerd.io/) under the hood. As a matter of fact, the concept of "containerisation" existed long before Docker. Containerization refers to the concept of isolating or jailing a (sub)process, on a computer (think for instance your python script or any kind of application). The reason you would want to isolate a certain process is to give it equal or elevated access/permission compared to it's parent process, whilst preventing it from doing any damage to anything other than itsself and it's child processes.

This concept is quite nicely illustrated in [this](https://www.youtube.com/watch?v=8fi7uSYlOdc&feature=youtu.be&list=PLEx5khR4g7PJzxBWC9c6xx0LghEIxCLwm) video as well, but here are some tests that you can do to illustrate it yourself (The comparissons are clearest if you run ubuntu images on an ubuntu machine):

1. Run `docker run --rm -d ubuntu:latest sleep 300` and subsequently run `ps -aux`. You will see "`sleep 300`" somewhere in that list: the containerised process is actually visible from outside the container and looks like any other process.
2. Run `docker run --rm -it ubuntu:latest /bin/bash` (you will be inside the container now). You'll immediately notice that you are the root user inside the container, even if you started the contianer from a non-root user (note: docker itsself does need root access, more on why this is the case later). You can do the following steps on both the container side, as well as in a fresh terminal to compare:
TODO: add examples of commands you can run.

In order to isolate a process, the container runtime makes use of [namespaces](https://en.wikipedia.org/wiki/Linux_namespaces) and [cgroups](https://en.wikipedia.org/wiki/Cgroups). These are two core features of the Linux kernel. Namespaces isolate the subprocess and give it it's own set of linux kernel resources, allowing it for instance to have it's own "view" of the filesystem (mount namespace), have its' own set of (sub) processes (PID and IPC namespaces), have a different hostname, and operate as it's own user (for instance root). Any changes that the process makes within any of those namespaces would only be reflected for itsself and its' subprocesses. Cgroups (which confusingly also are namespaced), restrict the amount of CPU, Memory, Disk, etc. that the process can use. This prevents it from impacting the parent process/host machine by draining all the resources. It is the fact that Docker (or rather containerd) uses plain and simple Linux core functionality that make it so easy to reverse engineer it in Bash or C. I found out the hard way that it is a bit harder in Python, as it doesn't have direct access to any of this functionality.

### Then what does Docker do? (Images)
If containers are almost completely built on top of core Linux functionality, then what value does Docker really add? The best way to look at Docker is as a platform that makes everything around containerisation easier. Most of this comes in the form of the `docker pull` and `docker build` commands, that allow you to download pre-built images from public or private repositories, and easily build images from a set of instructions (Dockerfile).

But this actually begs the question, what is an image exactly? To explore this, we can run the command `docker save ubuntu -o images/ubuntu/ubuntu.tar`. This will download the ubuntu image to the specified folder as a tar file. The ubuntu image is fairly simple because it only consists of a single layer (more on this later when we recreate the docker pull command). After unpacking the tar file (`tar -xvf images/ubuntu/ubuntu.tar -C images/ubuntu/`) you will see this single layer in the form of a hash, next to some other metadata files: 

Inside that layer folder (starting with a8c4d... in the above case) you find some more metadatafiles, alongside a file called layer.tar. If we extract this file into its own folder `tar -xvf images/ubuntu/a8c4dc1e399c.../layer.tar -C images/ubuntu/a8c4dc1e399c.../layer`, what you will see is something like the following (`ls -la`):

Indeed that looks a lot like running `ls /`:


This is simply a copy of the root file system of ubuntu. When you "containerize" a process using Docker, it get's executed with this new folder as its' filesystem. To achieve this, again a core Linux functionality is used: chroot (as in change root). This command switches the root (i.e. `/`) to this subfolder. To illustrate, I place an empty file called "IMAGE" inside the image root (`touch ~/images/ubuntu/a8c4d.../layer/IMAGE`). Now running the command `sudo chroot ~/images/ubuntu/a8c4d.../layer` and subsequently `ls -la /`, you can see that IMAGE file:


This is really all an image is: a compressed copy of an entire filesystem. The `docker build` command convienently allows you to start with an existing file system, and install any packages/dependencies inside that filesystem before you start the container process.

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



