#!/bin/bash

## Script antiguo para ejecutar una aplicación en un único núcleo sin Manager. (Basado en un script de Lucia)
## Daniel Mirón

function join_by { local IFS="$1"; shift; echo "$*"; }

EVENTS_P="cpu_core/instructions/,cpu_core/cycles/"
EVENTS_E="cpu_atom/instructions/,cpu_atom/cycles/"

WORKLOADS=$1
CORES="0 16"
QUANTUM=200
POS=0

mkdir -p data
mkdir -p run

## Frecuencia base No está funcionando por defecto están en performance
##cpupower -c 0 frequency-set -f 3000000    # Núcleo P
##cpupower -c 16 frequency-set -f 2200000   # Núcleo E

while read WL; do
    for core in ${CORES}; do
	rm /home/dmirvid/fin.txt

        WL=$(echo $WL | tr '\-[],' " ")
        ID=$(join_by - ${WL[POS]}_${core})
        OUT=data/${ID}.csv
        FIN_OUT=data/${ID}_total_time.csv

        echo $ID

        ## Ejecutar aplicación 
        mkdir run/${ID}
        cd run/${ID}
        sudo taskset -c ${core} /home/dmirvid/app_sola.py ${WL[POS]} > out 2> err &

        ## Monitorizar eventos
        start=$(date +%s.%N)
        echo "${WL} has started!"
	if [[ ${core} == '0' ]]
        then
        	sudo perf stat -e ${EVENTS_P} -C ${core} -I ${QUANTUM} -x ',' -A -o ../../${OUT} &
        else
        	sudo perf stat -e ${EVENTS_E} -C ${core} -I ${QUANTUM} -x ',' -A -o ../../${OUT} &
	fi


        ## Esperar a que termine la aplicación
        FILE=/home/dmirvid/fin.txt
        while [ ! -f "$FILE" ]; do
                sleep 0.2
        done

        end=$(date +%s.%N)
        runtime=$(echo "$end - $start" | bc)
        echo $runtime > ../../${FIN_OUT}

        ## Stop monitoring Perf
        echo "$WL has finished!"
        sudo killall perf

        ## Clean CSV file
        sed -i '1d' ../../${OUT}
        sed -i '1d' ../../${OUT}
        OUTtmp=data/${ID}_${REP}_tmp.csv
        ( echo "Time,CPU,Counter_value,,Event_name,runtime_counter,percentage_measurement_time,variance,," ; cat ../../${OUT} ) > ../../${OUTtmp}
        cp ../../${OUTtmp} ../../${OUT}
        rm ../../${OUTtmp}
        cd ../..

    done


done < $WORKLOADS
