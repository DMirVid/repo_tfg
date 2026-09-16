#!/bin/bash

## Pone la frecuencia base en los procesadores
## Daniel Mirón

echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null

for i in {16..31}; do
  echo 2200000 > /sys/devices/system/cpu/cpufreq/policy$i/scaling_min_freq
done
for i in {16..31}; do
  echo 2200000 > /sys/devices/system/cpu/cpufreq/policy$i/scaling_max_freq
done

for i in {0..15}; do
  echo 3000000 > /sys/devices/system/cpu/cpufreq/policy$i/scaling_min_freq
done
for i in {0..15}; do
  echo 3000000 > /sys/devices/system/cpu/cpufreq/policy$i/scaling_max_freq
done
