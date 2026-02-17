#!/bin/bash

echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
echo 2200000 | tee /sys/devices/system/cpu/cpufreq/policy{16 .. 31}/scaling_min_freq > /dev/null
echo 2200000 | tee /sys/devices/system/cpu/cpufreq/policy{16 .. 31}/scaling_max_freq > /dev/null

echo 3000000 | tee /sys/devices/system/cpu/cpufreq/policy{2 .. 14}/scaling_min_freq > /dev/null
echo 3000000 | tee /sys/devices/system/cpu/cpufreq/policy{2 .. 14}/scaling_max_freq > /dev/null