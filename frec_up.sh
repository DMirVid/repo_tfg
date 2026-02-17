#!/bin/bash

echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
echo 2100000 | tee /sys/devices/system/cpu/cpufreq/policy*/scaling_min_freq > /dev/null
echo 3100000 | tee /sys/devices/system/cpu/cpufreq/policy*/scaling_max_freq > /dev/null

cpupower -c 2-14:2 frequency-set -f 3000000
cpupower -c 16-31 frequency-set -f 2200000
