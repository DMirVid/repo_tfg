#!/bin/bash

APPS=("gamess_go" "xala" "gamess_l" "astar")

echo "politica,mezcla,run,app,ipc,nucleos,tiempo" > ~/repo_tfg/resultados/tiempos_pol0.csv

echo "politica;mezcla;run;energia;timepo" > ~/repo_tfg/resultados_energia_pol0.csv
#echo "politica;mezcla;run;energia;timepo"
for p in 0 4; do
    for m in 15 16 17; do
        cd ~/ejecuciones/instr_max/politica"${p}"/mezcla"$((m+1))"/
        for r in 0 1; do
            output=$(sudo perf stat -e power/energy-cores/ bash /home/dmirvid/python-manager/scripts/launch.bash apps.yaml --ini-rep 0 --max-rep 1 2>&1)
            # Captura ambos formatos: 543,86 y 2.242,00
            energia=$(echo "$output" | grep "Joules" | grep -oP '[0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]+)?')
            tiempo=$(echo "$output" | grep "seconds" | grep -oP '[0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]+)?')
            # Procesar los datos
            echo "$p;$((m+1));$r;$energia;$tiempo" >> ~/repo_tfg/resultados_energia_pol0.csv
            echo "$p;$((m+1));$r;$energia;$tiempo"

            cd data/
            cp *summary.txt ~/repo_tfg/resultados/instr/p"${p}"/m"$((m+1))"/r"$((r+1))"
            data=($(ls *event_totals.csv))
            output=$(python ~/repo_tfg/print_results.py "${data[@]}")
            while IFS= read -r line; do
                if [[ -n "$line" ]]; then
                    echo ""${p}","$((m+1))","$((r+1))","${line}"" >> ~/repo_tfg/resultados/tiempos_pol0.csv
                fi
            done <<< "$output"
            python ~/repo_tfg/topdown_juntas.py "${data[${@}]}"
            cp ../*.png ~/repo_tfg/resultados/instr/p"${p}"/m"$((m+1))"/r"$((r+1))"
            rm ../*.png
            echo "Graficas copiadas en ~/repo_tfg/resultados/instr/p"${p}"/m"$((m+1))"/r"$((r+1))""
            cd ..
        done
    done
done
