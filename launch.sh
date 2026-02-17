#!/bin/bash

function join_by { local IFS="$1"; shift; echo "$*"; }

WORKLOADS=$1        ## Aplicación
ASSIGNED_CORE=$2    ## Núcleo asignado (P o E)
EVENTS=$3           ## Eventos a monitorizar (P o E)
QUANTUM=200
POS=0

mkdir -p data
mkdir -p run

# Preparar nombre de la aplicación
WL=$(echo $WORKLOADS | tr '\-[],' " ")
ID=$(join_by - ${WL[@]}_${ASSIGNED_CORE})
OUT="data/${ID}.csv"
FIN_OUT="data/${ID}_total_time.csv"

## Crear directorio de ejecución
mkdir -p "run/${ID}"
cd "run/${ID}"
sudo taskset -c ${ASSIGNED_CORE} /home/dmirvid/app_sola.py ${WL[@]} > out 2> err &
app_pid=$!

## Monitorizar eventos
start=$(date +%s.%N)
echo "${WL} has started!"
sudo perf stat -e ${EVENTS} -C ${ASSIGNED_CORE} -I ${QUANTUM} -x ',' -A -o ../../${OUT} &

## Esperar a que termine la aplicación
while kill -0 $app_pid 2>/dev/null; do
    sleep 0.2
done

## Registrar tiempo
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
