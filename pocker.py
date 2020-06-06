from manifest_utils import DockerRegistry
import shutil
import os
import uuid
import tarfile
import subprocess
import syscalls


def pocker_pull(image, tag, image_hash, root_dir):
    # Hardcode these for now. Should work in EC2
    architecture = "amd64"
    os_system = "linux"

    # Directory where image will end up
    image_dir = root_dir + "/" + image_hash

    # Initiate docker registry object and pull first manifest
    registry = DockerRegistry(image)
    manifest = registry.get_manifest_json(tag)

    def process_manifest(manifest, registry):
        if manifest['mediaType'] == 'application/vnd.docker.distribution.manifest.list.v2+json':
            for l in manifest['manifests']:
                if l['platform']['architecture'] == architecture:
                    if l['platform']['os'] == os_system:
                        sub_manifest = registry.get_manifest_json(l['digest'])
                        process_manifest(sub_manifest, registry)

        elif manifest['mediaType'] == 'application/vnd.docker.distribution.manifest.v2+json':
            # Handle layers
            for l in manifest['layers']:
                process_manifest(l, registry)

        elif manifest['mediaType'] == 'application/vnd.docker.image.rootfs.diff.tar.gzip':
            digest = manifest['digest']
            tar_dir = root_dir + "/" + uuid.uuid4().hex
            tar_file = tar_dir + "/layer.tar"
            os.makedirs(tar_dir)
            registry.fetch_blob(digest, tar_file)
            tar = tarfile.open(tar_file)
            tar.extractall(image_dir)
            tar.close()
            shutil.rmtree(tar_dir)

        else:
            print('Unexpected Manifest type!! :' + str(manifest))
            return None

    process_manifest(manifest, registry)


def pocker_run(image, tag, cmd=["/bin/bash"]):

    # Directory where image will end up
    root_dir = './testing'  # TODO: make this parameterizable
    image_hash = uuid.uuid4().hex
    image_dir = root_dir + "/" + image_hash

    # TODO: make it keep track of images that have already been pulled.
    pocker_pull(image, tag, image_hash, root_dir)

    # unshare
    syscalls.unshare(
        syscalls.CLONE_NEWUTS |
        syscalls.CLONE_NEWPID |
        syscalls.CLONE_NEWNET |
        syscalls.CLONE_NEWNS)  # uts, pid, mount, ipc

    # change root to image dir
    os.chroot(image_dir)
    os.chdir('/')
    syscalls.mount('/proc', '/proc', 'proc')

    # Execute command
    subprocess.run(cmd)


pocker_run("alpine", "latest")





