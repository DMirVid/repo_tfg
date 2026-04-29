
APPS = ("astar" "bwaves" "bzip2" "cactusADM" "calculix" "dealII" "gamess" "gcc" "GemsFDTD" "gobmk" "gromacs" "h264ref" "hmmer" "lbm" "leslie3d" "libquantum" "mcf" "milc" "namd" "omnetpp" "perlbench" "povray" "sjeng" "soplex" "sphinx3" "tonto" "wrf" "xalancbmk" "zeusmp" "mcf_r" "cactuBSSN_r" "namd_r" "parest_r" "povray_r" "lbm_r" "omnetpp_r" "xalancbmk_r" "x264_r" "blender_r" "deepsjeng_r" "imagick_r" "leela_r" "nab_r")


> resultados.csv
echo "APP,ENERGIA_J,TIEMPO_S" > resultados_energia.csv

for app in ${APPS[@]}; do
    
   cat "[${app}]" >> app.yaml

    # Capturar salida de perf stat (va a stderr, por eso 2>&1)
    output=$(sudo perf stat -e power/energy-cores/ bash /home/dmirvid/python-manager/scripts/launch.bash app.yaml --ini-rep 0 --max-rep 1 2>&1)
    
    energia=$(tail -n 5 "$output" | grep -oP '\K[0-9]+\.[0-9]+(?= Joules)')
    
    tiempo=$(tail -n 5 "$output" | grep -oP '\K[0-9]+\.[0-9]+(?= seconds)')
    
    # Procesar los datos
    echo "$app,$energia,$tiempo" >> resultados_energia.csv


done