# Artifact for Final Year Project

This repository is for artifact evaluation(i.e., 软硬件验收 in Chinese) of final year project(FYP) in Xidian University.

## Notes

Run app on specific core

```bash
taskset -c 0 <command>
```

Check process on CPU 0

```bash
bash -c 
```

Isolate one core on Ubuntu

```bash
vim /etc/default/grub
# GRUB_CMDLINE_LINUX="isolcpus=0"
# update grub (/boot/grub/grub.cfg)
sudo update-grub
# Verify it through /boot/grub/grub.cfg

# Check if CPU0 is really isolated (no user process at all)
ps -o pid,psr,comm -p <pid> # standard syntax (instead of BSD style)
ps -eo pid,psr,comm | awk  '($2 == 0)'
```
