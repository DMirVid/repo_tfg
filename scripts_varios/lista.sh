#!/bin/bash

## Script para listar archivos de un directorio.
## Daniel Mirón

# Directorio por defecto es el actual, o se pasa como argumento
DIRECTORIO="${1:-.}"

ls "$DIRECTORIO" | grep -i "time" | while read archivo; do
    # Crear archivo de salida sin extensión original + .txt
    archivo_sin_ext="${archivo%.*}"
    archivo_salida="${archivo_sin_ext}.txt"
    cat $archivo > ../resultados/$archivo_salida
done
echo "DONE"
