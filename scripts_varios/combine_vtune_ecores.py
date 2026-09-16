## Genera un csv con todas las aplicaciones y los eventos medidos por VTune en los núcleos P y E.
## Para distintos núcleos se cambia las carpetas de entrada y salida.
## Daniel Mirón

import os
import csv

# Carpeta con los archivos vtune
vtune_folder = "vtuneP"

# Obtener lista de archivos CSV
csv_files = [f for f in os.listdir(vtune_folder) if f.endswith("_vtune_summary.csv")]
csv_files.sort()

# Diccionario para almacenar datos por aplicación
all_data = {}

for csv_file in csv_files:
    # Extraer nombre de aplicación (remover prefijo y sufijo)
    app_name = csv_file.replace("_vtune_summary.csv", "")
    
    filepath = os.path.join(vtune_folder, csv_file)
    
    # Leer el archivo CSV
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        lines = list(reader)
    
    # Extraer líneas 123-166 (índices 122-165 en 0-indexed)
    ecore_section = lines[9:123]
    
    metrics = {}
    current_metric = None
    
    for line in ecore_section:
        if len(line) >= 3:
            hierarchy = line[0]
            metric_name = line[1]
            metric_value = line[2] if line[2] else ""
            
            current_metric = metric_name
            try:
                metrics[metric_name] = float(metric_value) if metric_value else 0.0
            except:
                metrics[metric_name] = 0.0
    
    all_data[app_name] = metrics

# Obtener todas las métricas únicas manteniendo el orden de aparición
all_metrics = []
all_metrics_set = set()
for metrics in all_data.values():
    for metric_name in metrics.keys():
        if metric_name not in all_metrics_set:
            all_metrics.append(metric_name)
            all_metrics_set.add(metric_name)

# Guardar como CSV
output_file = "vtune_pcores_combined.csv"
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    
    # Encabezado
    writer.writerow(["Application"] + all_metrics)
    
    # Datos por aplicación
    for app_name in sorted(all_data.keys(), key=lambda x: x.lower()):
        row = [app_name]
        for metric in all_metrics:
            row.append(all_data[app_name].get(metric, 0.0))
        writer.writerow(row)

print(f"✓ Archivo combinado creado: {output_file}")
print(f"✓ Aplicaciones: {len(all_data)}")
print(f"✓ Métricas: {len(all_metrics)}")
print(f"\nMétricas extraídas:")
for metric in all_metrics:
    print(f"  - {metric}")
