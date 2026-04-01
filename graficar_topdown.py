#!/usr/bin/python

# Crea una gráfica de area para cada aplicaión con sus datos de topdown, usando un eje secundario para el IPC.

import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

QUANTUM = 100 # 100ms

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
            
            # Agrupar en conjuntos de 21
            for i in range(0, len(datos), 9 + plus):
                if i + 8 + plus < len(datos):
                    app_name = datos[i]
                    cores = datos[i+1]
                    instr = float(datos[i+2])
                    cycles = float(datos[i+3])
                    if cycles == 0:
                        cycles = 1
                    retiring = float(datos[i+4 + plus])
                    bad_speculation = float(datos[i+5 + plus])
                    frontend = float(datos[i+6 + plus])
                    backend_bound = float(datos[i+7 + plus])
                    memory_bound = float(datos[i+9])

                    ipc = instr / cycles

                    total = frontend + retiring + bad_speculation + backend_bound
                    total = total if total != 0 else 1  # Evitar división por cero
                    retiring = retiring / total
                    bad_speculation = bad_speculation / total
                    frontend = frontend / total
                    backend_bound = backend_bound / total

                    memory_bound = memory_bound / total
                    core_bound = backend_bound - memory_bound

                    if app_name in data:
                        data[app_name].append((retiring, bad_speculation, frontend, memory_bound, core_bound, ipc, cycles))
                    else:
                        data[app_name] = [(retiring, bad_speculation, frontend, memory_bound, core_bound, ipc, cycles)]

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
            retiring_plot = [x[0] for x in topdown[:last_idx + 1]]
            bad_plot = [x[1] for x in topdown[:last_idx + 1]]
            frontend_plot = [x[2] for x in topdown[:last_idx + 1]]
            memory_bound = [x[3] for x in topdown[:last_idx + 1]]
            core_bound = [x[4] for x in topdown[:last_idx + 1]]
            ipc_list = [x[5] for x in topdown[:last_idx + 1]]

            # eje principal: area apilada
            color_map = ["cornflowerblue", "gold", "lightgreen", "lightcoral", "crimson"]
            ax1.stackplot(tiempo, retiring_plot, bad_plot, frontend_plot, memory_bound, core_bound, colors=color_map,
                            labels=["Retiring", "Bad speculation", "Frontend", "Memory Bound", "Core Bound"], alpha=0.8)
            str_t = f'Time (s) Total: {seconds//60:.0f}m {seconds%60:.0f}s'
            ax1.set_xlabel(str_t, fontsize=18)
            ax1.set_ylabel('Percertage of Time Execution', fontsize=18)
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
