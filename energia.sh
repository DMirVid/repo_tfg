#!/bin/bash

for i in {0..7}; do
    sudo taskset -c "${i}" /home/dmirvid/repo_tfg/core_microbenchmark > /dev/null &
done

echo "Durante 10 segundos con todos los núcleos activos..."
sleep 10
