#!/bin/bash

echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
echo 2500000 | tee /sys/devices/system/cpu/cpufreq/policy*/scaling_min_freq > /dev/null
echo 2500000 | tee /sys/devices/system/cpu/cpufreq/policy*/scaling_max_freq > /dev/null