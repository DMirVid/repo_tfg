#!/usr/bin/python   

import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from lib import leer_datos_juntos
import numpy as np

QUANTUM = 200

def main():

    archivos = sys.argv[1:]

    data = {}

    for archivo in archivos:
        data.update(leer_datos_juntos(archivo, eventosP=8, eventosE=6))

    if data:
        apps_list = list(data.items())
        
        for app_name, topdown in apps_list:

            fig, ax1 = plt.subplots(figsize=(16, 8))

            tiempo = [x * QUANTUM / 1000.0 for x in  np.arange(len(topdown))] 

            core = [x[0] for x in topdown]
            ipc_list = [x[1]/x[2] for x in topdown]
            retiring_plot_p = [x[3] if x[0]<16 else 0 for x in topdown]
            bad_plot_p = [x[4] if x[0]<16 else 0 for x in topdown]
            frontend_plot_p = [x[5] if x[0]<16 else 0 for x in topdown]
            backend_bound_plot_p = [x[6] if x[0]<16 else 0 for x in topdown]
            core_bound_plot_p = [x[7] if x[0]<16 else 0 for x in topdown]
            memory_bound_plot_p = [x[8] if x[0]<16 else 0 for x in topdown]

            retiring_plot_e = [x[3] if x[0]>=16 else 0 for x in topdown]
            bad_plot_e = [x[4] if x[0]>=16 else 0 for x in topdown]
            frontend_plot_e = [x[5] if x[0]>=16 else 0 for x in topdown]
            backend_bound_plot_e = [x[6] if x[0]>=16 else 0 for x in topdown]


            color_map = ["cornflowerblue", "gold", "lightgreen", "lightcoral", "crimson"]

            
            ax1.stackplot(tiempo, retiring_plot_p, bad_plot_p, frontend_plot_p, memory_bound_plot_p, core_bound_plot_p, colors=color_map,
                            labels=["Retiring", "Bad speculation", "Frontend","Memory Bound", "Core Bound"], alpha=0.8)

            ax1.stackplot(tiempo, retiring_plot_e, bad_plot_e, frontend_plot_e, backend_bound_plot_e, colors=color_map,
                            labels=["Retiring", "Bad speculation", "Frontend", "Backend Bound"], alpha=0.8)
                

            str_t = f'Time (s)'
            ax1.set_xlabel(str_t, fontsize=18)
            ax1.set_ylabel('Percentage of Time Execution', fontsize=18)
            ax1.tick_params(axis='x', labelsize=18)
            ax1.tick_params(axis='y', labelsize=18)
            ax1.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=None))
            ax1.set_xlim(0, tiempo)
            ax1.set_ylim(0, 1)
            ax1.grid(True, alpha=0.3, axis='y')

            ax2 = ax1.twinx()
            ax2.plot(tiempo, ipc_list, 'o-', color='black', linewidth=2, markersize=1, label='IPC')
            ax2.yaxis.set_major_locator(mtick.MultipleLocator(0.5))
            ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f'))
            ax2.set_ylabel('IPC', fontsize=18)
            ax2.tick_params(axis='y', labelsize=18)
            ax2.set_ylim(0)


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
        print("No se han encontrado datos para graficar.")
    
    data.clear() 

if __name__ == "__main__":    
    main()