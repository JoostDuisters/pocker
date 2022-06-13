pushd /

while $(grep -q testing /proc/mounts); do 
    sudo umount $(grep testing /proc/mounts | shuf | head -n1 | cut -f2 -d' ') 2>/dev/null
done
popd