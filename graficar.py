#!/usr/bin/python

# Muestra el IPC a lo largo del tiempo de hasta 8 aplicaciones en una misma gráfica de lineas

import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

def main():
    data = {}

    if len(sys.argv) < 2:
        print("Uso: python graficar.py archivo1 [archivo2 ...]")
        return
    
    archivos = sys.argv[1:]
    
    # Procesar cada archivo
    for archivo in archivos:
        try:
            with open(archivo, 'r') as f:
                lineas = f.readlines()
        except Exception as e:
            print(f"Error abriendo {archivo}: {e}")
            continue
        
        # Procesar cada línea del archivo
        for linea in lineas:
            linea = linea.strip()
            if not linea or linea.startswith("name"):
                continue
            
            # Parse: name;cores;instructions_path;cycles_path (puede repetirse)
            datos = linea.split(";")
            
            # Agrupar en conjuntos de 4
            for i in range(0, len(datos), 22):
                if i + 21 < len(datos):
                    app_name = datos[i]
                    cores = datos[i+1]
                    instr= datos[i+2]
                    cycles = datos[i+3]
                    
                    ipc_value = float(instr) / float(cycles) if float(cycles) != 0 else 0
                    if app_name in data:
                        data[app_name].append(ipc_value)
                    else:
                        data[app_name] = [ipc_value]
    
    # Graficar todas las aplicaciones en gráficas de máximo 8 apps
    if data:
        apps_list = list(data.items())
        num_graficas = (len(apps_list) + 7) // 8  # Dividir en grupos de 8
        
        for grafica_num in range(num_graficas):
            inicio = grafica_num * 8
            fin = min((grafica_num + 1) * 8, len(apps_list))
            apps_grupo = apps_list[inicio:fin]
            
            plt.figure(figsize=(16, 9))
            
            for app_name, ipc_values in apps_grupo:
                tiempo = np.arange(len(ipc_values))
                plt.plot(tiempo, ipc_values, linewidth=1, marker='o', markersize=1, label=app_name)
            
            plt.xlabel('Tiempo', fontsize=20)
            plt.ylabel('IPC', fontsize=20)
            plt.xticks(fontsize=20)
            plt.yticks(fontsize=20)
            plt.grid(True, alpha=0.3)
            plt.xlim(0, 6000)
            plt.ylim(0, 5)
            plt.subplots_adjust(top=0.80)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), fontsize=20, ncol=4)
            plt.tight_layout()
            
            # Guardar figura con número de página si hay múltiples gráficas
            output_filename = f'../P_core_grafica_{grafica_num + 1}.png'
            
            plt.savefig(output_filename, dpi=100)
            print(f"Gráfica guardada: {output_filename}")
            plt.close()
    else:
        print("No se encontraron datos para graficar")

    data.clear()  # Limpiar datos para el siguiente archivo

if __name__ == "__main__":    
    main()
