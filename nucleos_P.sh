#!/bin/bash

function join_by { local IFS="$1"; shift; echo "$*"; }

# Crear arrays asociativos para tracking por núcleo
declare -A CORE_PID=()        # core_id -> PID
declare -A CORE_APP=()        # core_id -> Nombre aplicación

EVENTS_P="cpu_core/instructions/,cpu_core/cycles/"

WORKLOADS=$1
CORES="2 4 6 8 10 12 14"

# Inicializar array de núcleos
function initialize_cores() {
    for core in ${CORES}; do
        CORE_PID[$core]=""
        CORE_APP[$core]=""
    done
}

# Función para encontrar el primer núcleo libre
function find_free_core() {
    for core in ${CORES}; do
        # Si no hay PID o el proceso ya terminó
        if [[ -z "${CORE_PID[$core]}" ]]; then
            return 0  # Éxito
        fi

        # Verificar si el proceso sigue vivo
        if ! kill -0 "${CORE_PID[$core]}" 2>/dev/null; then
            CORE_PID[$core]=""
            CORE_APP[$core]=""
            return 0
        fi
    done
    return 1  # Fallo, todos ocupados
}

# Función para esperar a que haya un núcleo libre
function wait_for_free_core() {
    while true; do
        find_free_core && break
        echo "Todos los núcleos P ocupados. Esperando liberación..."
        sleep 10
    done
}

# Función para asignar aplicación a un núcleo
function assign_to_core() {
    local app_name=$1
    local pid=$2

    for core in ${CORES}; do
        if [[ -z "${CORE_PID[$core]}" ]]; then
            CORE_PID[$core]=$pid
            CORE_APP[$core]=$app_name
            return
        fi
    done
}

## Frecuencia base 
## ¡¡No hay permisos suficientes!!
##cpupower -c 0 frequency-set -f 3000000    # Núcleo P

# Inicializar núcleos
initialize_cores

while read WL; do
        # Esperar a que haya un núcleo libre
        wait_for_free_core

        # Preparar nombre de la aplicación
        WL=$(echo $WL | tr '\-[],' " ")
        APP_NAME=$(join_by - ${WL[@]})

        find_free_core
        assign_to_core "$APP_NAME" $$  # Temporal, se actualizará

        # Encontrar el núcleo nuevamente para obtener su ID
        for core in ${CORES}; do
            if [[ "${CORE_APP[$core]}" == "$APP_NAME" ]]; then
                ASSIGNED_CORE=$core
                break
            fi
        done

        sudo taskset -c ${ASSIGNED_CORE} /home/dmirvid/launch.sh ${WL[@]} ${ASSIGNED_CORE} ${EVENTS_P} > out 2> err &
        app_pid=$!

        # Actualizar el PID en el tracking
        CORE_PID[$ASSIGNED_CORE]=$app_pid

done < $WORKLOADS

for core in ${CORES}; do
    if [[ -n "${CORE_PID[$core]}" ]]; then
        wait "${CORE_PID[$core]}"
    fi