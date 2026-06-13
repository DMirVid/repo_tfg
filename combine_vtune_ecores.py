import os
import csv

# Carpeta con los archivos vtune
vtune_folder = "vtune"

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
    ecore_section = lines[122:166]
    
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

# Obtener todas las métricas únicas
all_metrics = set()
for metrics in all_data.values():
    all_metrics.update(metrics.keys())

all_metrics = list(all_metrics)

# Guardar como CSV
output_file = "vtune_ecores_combined.csv"
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
