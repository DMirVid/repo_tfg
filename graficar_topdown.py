#!/usr/bin/python

# Crea una gráfica de area para cada aplicaión con sus datos de topdown, usando un eje secundario para el IPC.

import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from lib import leer_datos
import numpy as np

QUANTUM = 200 # 200ms

def main():
    data = {}

    if len(sys.argv) < 3:
        print("Uso: python graficar.py core archivo1 [archivo2 ...]")
        return
    
    plus = 0
    core = sys.argv[1]
    if core == 'P':
        plus = 1
    archivos = sys.argv[2:]
    
    data = {} 
    # Procesar cada archivo
    for archivo in archivos:
       data.update(leer_datos(core, archivo))

    # Graficar todas las aplicaciones en gráficas individuales
    if data:
        apps_list = list(data.items())
        
        for app_name, topdown in apps_list:

            # Encontrar el índice donde la app termina (ciclos dejan de aumentar)
            last_idx = len(topdown) - 1
            for i in range(len(topdown) - 1, -1, -1):
                if i == 0 or topdown[i][5] > topdown[i-1][5]:  # ciclos en posición 5
                    last_idx = i
                    break

            fig, ax1 = plt.subplots(figsize=(16, 8))
            
            seconds = last_idx * QUANTUM / 1000.0
            tiempo = [x * QUANTUM / 1000.0 for x in  np.arange(last_idx + 1)]  # Convertir a segundos
            ipc_list = [x[0] for x in topdown[:last_idx + 1]]
            retiring_plot = [x[1] for x in topdown[:last_idx + 1]]
            bad_plot = [x[2] for x in topdown[:last_idx + 1]]
            frontend_plot = [x[3] for x in topdown[:last_idx + 1]]
            backend_bound_plot = [x[4] for x in topdown[:last_idx + 1]]

            color_map = ["cornflowerblue", "gold", "lightgreen", "lightcoral", "crimson"]
            if core == 'P':
                core_bound = [x[5] for x in topdown[:last_idx + 1]]
                memory_bound = [x[6] for x in topdown[:last_idx + 1]]
                ax1.stackplot(tiempo, retiring_plot, bad_plot, frontend_plot, backend_bound_plot, core_bound, memory_bound, colors=color_map,
                                labels=["Retiring", "Bad speculation", "Frontend", "Core Bound", "Memory Bound"], alpha=0.8)
            else:
                ax1.stackplot(tiempo, retiring_plot, bad_plot, frontend_plot, backend_bound_plot, colors=color_map,
                                labels=["Retiring", "Bad speculation", "Frontend", "Backend Bound"], alpha=0.8)
            
            # eje principal: area apilada
            str_t = f'Time (s) Total: {seconds//60:.0f}m {seconds%60:.0f}s'
            ax1.set_xlabel(str_t, fontsize=18)
            ax1.set_ylabel('Percentage of Time Execution', fontsize=18)
            ax1.tick_params(axis='x', labelsize=18)
            ax1.tick_params(axis='y', labelsize=18)
            ax1.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=None))
            ax1.set_xlim(0, seconds)
            ax1.set_ylim(0, 1)
            ax1.grid(True, alpha=0.3, axis='y')

            # eje secundario: IPC
            ax2 = ax1.twinx()
            ax2.plot(tiempo, ipc_list, 'o-', color='black', linewidth=2, markersize=1, label='IPC')
            ax2.yaxis.set_major_locator(mtick.MultipleLocator(0.5))
            ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f'))
            ax2.set_ylabel('IPC', fontsize=18)
            ax2.tick_params(axis='y', labelsize=18)
            ax2.set_ylim(0, 5)

            # Crear espacio en la parte superior para la leyenda
            lines, labels = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()

            plt.subplots_adjust(top=0.85)
            plt.legend(lines + lines2, labels + labels2, 
                        loc='upper center', bbox_to_anchor=(0.5, 1.15), 
                        fontsize=16, ncol=6)
            
            plt.tight_layout()
            
            output_filename = '../' + app_name + '.png'
            
            plt.savefig(output_filename, dpi=100)
            print(f"Gráfica guardada: {output_filename}")
            plt.close()
    else:
        print("No se encontraron datos para graficar")

    data.clear()  # Limpiar datos para el siguiente archivo

if __name__ == "__main__":    
    main()
