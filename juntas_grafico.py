#!/usr/bin/python

# Crea tres gráficas de líneas mostrando múltiples aplicaciones ejecutándose juntas:
# 1. IPC de cada aplicación a lo largo del tiempo
# 2. MPKI de cada aplicación a lo largo del tiempo
# 3. Memory Bound y Core Bound de cada aplicación

import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

QUANTUM = 200 # 200ms

def main():
    if len(sys.argv) < 3:
        print("Uso: python juntas_grafico.py core archivo1 [archivo2 ...]")
        return
    
    ancho_issue = 5
    plus = 0
    core = sys.argv[1]
    if core == 'P':
        plus = 1
        ancho_issue = 6
    archivos = sys.argv[2:]
    
    # Procesar cada archivo
    for archivo in archivos:
        data = {}  # app_name -> list of tuples
        
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
            
            # Parse: name;cores;instructions;cycles;...
            datos = linea.split(";")
            
            # Agrupar en conjuntos de 23 + plus
            for i in range(0, len(datos), 23 + plus):
                if i + 22 + plus < len(datos):
                    app_name = datos[i]
                    cores = datos[i+1]
                    instr = float(datos[i+2])
                    cycles = float(datos[i+3])
                    if cycles == 0:
                        cycles = 1
                    
                    retiring = float(datos[i+5])
                    bad_speculation = float(datos[i+6])
                    frontend = float(datos[i+7])
                    backend_bound = float(datos[i+8])
                    memory_bound = float(datos[i+9])

                    ipc = instr / cycles

                    total = cycles * ancho_issue
                    total = total if total != 0 else 1
                    memory_bound_norm = memory_bound / total
                    backend_bound_norm = backend_bound / total
                    core_bound = backend_bound_norm - memory_bound_norm

                    l1_miss = float(datos[i+21])
                    mpki_total = (l1_miss / instr) * 1000

                    if app_name in data:
                        data[app_name].append((ipc, mpki_total, memory_bound_norm, core_bound))
                    else:
                        data[app_name] = [(ipc, mpki_total, memory_bound_norm, core_bound)]

        # Generar las tres gráficas combinadas si hay datos
        if data:
            # Determinar el máximo número de puntos de tiempo
            max_len = max(len(values) for values in data.values())
            tiempo = [x * QUANTUM / 1000.0 for x in np.arange(max_len)]
            
            # Colores para cada aplicación
            colors = plt.cm.tab20(np.linspace(0, 1, len(data)))
            
            # Gráfica 1: IPC
            fig1, ax1 = plt.subplots(figsize=(14, 7))
            for (app_name, values), color in zip(data.items(), colors):
                ipc_list = [v[0] for v in values]
                ax1.plot(tiempo[:len(ipc_list)], ipc_list, 'o-', label=app_name, color=color, markersize=3, linewidth=2)
            
            str_t = f'Time (s)'
            ax1.set_xlabel(str_t, fontsize=14)
            ax1.set_ylabel('IPC', fontsize=14)
            ax1.tick_params(axis='both', labelsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=10, loc='best')
            ax1.set_title('IPC de Aplicaciones Ejecutadas Juntas', fontsize=16, fontweight='bold')
            plt.tight_layout()
            output_filename1 = archivo.replace('.csv', '_ipc.png')
            plt.savefig(output_filename1, dpi=100)
            print(f"Gráfica IPC guardada: {output_filename1}")
            plt.close()
            
            # Gráfica 2: MPKI
            fig2, ax2 = plt.subplots(figsize=(14, 7))
            for (app_name, values), color in zip(data.items(), colors):
                mpki_list = [v[1] for v in values]
                ax2.plot(tiempo[:len(mpki_list)], mpki_list, 'o-', label=app_name, color=color, markersize=3, linewidth=2)
            
            ax2.set_xlabel(str_t, fontsize=14)
            ax2.set_ylabel('MPKI (Misses Per Kilo Instructions)', fontsize=14)
            ax2.tick_params(axis='both', labelsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=10, loc='best')
            ax2.set_title('MPKI de Aplicaciones Ejecutadas Juntas', fontsize=16, fontweight='bold')
            plt.tight_layout()
            output_filename2 = archivo.replace('.csv', '_mpki.png')
            plt.savefig(output_filename2, dpi=100)
            print(f"Gráfica MPKI guardada: {output_filename2}")
            plt.close()
            
            # Gráfica 3: Memory Bound y Core Bound
            fig3, ax3 = plt.subplots(figsize=(14, 7))
            for (app_name, values), color in zip(data.items(), colors):
                memory_bound_list = [v[2] for v in values]
                core_bound_list = [v[3] for v in values]
                ax3.plot(tiempo[:len(memory_bound_list)], memory_bound_list, 'o-', label=f'{app_name} (Memory Bound)', 
                        color=color, markersize=3, linewidth=2, linestyle='-', alpha=0.7)
                ax3.plot(tiempo[:len(core_bound_list)], core_bound_list, 's-', label=f'{app_name} (Core Bound)', 
                        color=color, markersize=3, linewidth=2, linestyle='--', alpha=0.7)
            
            ax3.set_xlabel(str_t, fontsize=14)
            ax3.set_ylabel('Percentage of Time Execution', fontsize=14)
            ax3.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
            ax3.tick_params(axis='both', labelsize=12)
            ax3.grid(True, alpha=0.3)
            ax3.legend(fontsize=9, loc='best', ncol=2)
            ax3.set_title('Memory Bound y Core Bound de Aplicaciones', fontsize=16, fontweight='bold')
            plt.tight_layout()
            output_filename3 = archivo.replace('.csv', '_bounds.png')
            plt.savefig(output_filename3, dpi=100)
            print(f"Gráfica Bounds guardada: {output_filename3}")
            plt.close()
        else:
            print(f"No se encontraron datos para graficar en {archivo}")

if __name__ == "__main__":    
    main()
