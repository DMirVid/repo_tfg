#!/bin/bash

# Script para compilar y ejecutar el microbenchmark de core

echo "Compilando microbenchmark..."
gcc -O3 -lm core_microbenchmark.c -o core_microbenchmark

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
