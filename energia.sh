#!/bin/bash

APPS=("gcc" "bwaves" "bzip2" "calculix" "dealII" "GemsFDTD" "gobmk" "gromacs" "h264ref" "hmmer" "lbm" "leslie3d" "libquantum" "milc" "omnetpp" "perlbench" "sjeng" "soplex" "tonto" "wrf" "xalancbmk" "zeusmp" "mcf_r" "cactuBSSN_r" "namd_r" "parest_r" "omnetpp_r" "x264_r" "blender_r" "deepsjeng_r" "imagick_r" "nab_r")

echo "APP;NUM;MODO;ENERGIA;TIEMPO" > ~/repo_tfg/energia_nucleosTODO.csv

for app in "${APPS[@]}"; do

    for i in 32; do
        yaml="["
        for ((x=0; x<$i; x++)); do
            yaml+=" ${app}"
        done
        yaml+="]"
        echo "$yaml" > app.yaml

        sudo bash /home/dmirvid/python-manager/scripts/launch.bash app.yaml --ini-rep 0 --max-rep 1 &
        pid=$(echo $!)
        sleep 5

        output=$(sudo perf stat -e power/energy-cores/ sleep 10 2>&1)
        energia=$(echo "$output" | grep "Joules" | grep -oP '[0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]+)?')
        tiempo=$(echo "$output" | grep "seconds" | grep -oP '[0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]+)?')

        echo "$app;$i;TODO;$energia;$tiempo" >> ~/repo_tfg/energia_nucleosTODO.csv
        echo "$app;$i;TODO;$energia;$tiempo"
        sudo kill "${pid}"
    done
done
