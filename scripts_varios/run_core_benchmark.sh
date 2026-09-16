#!/bin/bash

# Script para compilar y ejecutar el microbenchmark de core
# IA

echo "Compilando microbenchmark..."
gcc -O3 core_microbenchmark.c -o core_microbenchmark -lm

if [ $? -eq 0 ]; then
    echo "Compilación exitosa!"
    echo ""
    echo "Ejecutando benchmark..."
    echo ""
    ./core_microbenchmark
else
    echo "Error en la compilación"
    exit 1
fi
