#!/usr/bin/python
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

QUANTUM = 100 # 100ms

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
            
            # Agrupar en conjuntos de 21
            for i in range(0, len(datos), 22):
                if i + 21 < len(datos):
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
                    #memory_bound = float(datos[i+9])

                    ipc = instr / cycles

                    total = frontend + retiring + bad_speculation + backend_bound
                    total = total if total != 0 else 1  # Evitar división por cero
                    retiring = retiring / total
                    bad_speculation = bad_speculation / total
                    frontend = frontend / total
                    backend_bound = backend_bound / total

                    # memory_bound = memory_bound / total
                    # core_bound = backend_bound - memory_bound

                    if app_name in data:
                        data[app_name].append((retiring, bad_speculation, frontend, backend_bound, ipc, cycles))
                    else:
                        data[app_name] = [(retiring, bad_speculation, frontend, backend_bound, ipc, cycles)]

    # Graficar todas las aplicaciones en una sola gráfica de barras
    if data:
        apps_list = list(data.items())
        
        # Preparar datos para el gráfico de barras
        app_names = []
        app_times = []
        retiring_values = []
        bad_speculation_values = []
        frontend_values = []
        backend_bound = []
        #core_bound_values = []
        #memory_bound_values = []
        ipc_values = []
        
        for app_name, topdown in apps_list:
            # Encontrar el índice donde la app termina (ciclos dejan de aumentar)
            last_idx = len(topdown) - 1
            for i in range(len(topdown) - 1, -1, -1):
                if i == 0 or topdown[i][5] > topdown[i-1][5]:  # ciclos en posición 5
                    last_idx = i
                    break
            
            # Calcular tiempo: índice * quantum (en milisegundos) / 1000 (para segundos)
            time_seconds = last_idx * QUANTUM / 1000.0
            
            # Obtener la última muestra de la app
            final_sample = topdown[last_idx]
            
            app_names.append(app_name)
            app_times.append(time_seconds)
            retiring_values.append(final_sample[0])
            bad_speculation_values.append(final_sample[1])
            frontend_values.append(final_sample[2])
            backend_bound.append(final_sample[3])
            #core_bound_values.append(final_sample[3])
            #memory_bound_values.append(final_sample[4])
            ipc_values.append(final_sample[4])
        
        # Crear gráfica de barras apiladas
        fig, ax1 = plt.subplots(figsize=(20, 8))
        
        x_pos = np.arange(len(app_names))
        width = 0.6
        
        # Colores para las barras
        color_map = ["cornflowerblue", "gold", "lightgreen", "lightcoral", "crimson"]
        
        # Crear barras apiladas con borde gris
        p1 = ax1.bar(x_pos, retiring_values, width, label='Retiring', color=color_map[0], alpha=0.8, edgecolor='gray', linewidth=1.5)
        p2 = ax1.bar(x_pos, bad_speculation_values, width, bottom=retiring_values, 
                     label='Bad speculation', color=color_map[1], alpha=0.8, edgecolor='gray', linewidth=1.5)
        
        cumulative = [r + b for r, b in zip(retiring_values, bad_speculation_values)]
        p3 = ax1.bar(x_pos, frontend_values, width, bottom=cumulative,
                     label='Frontend', color=color_map[2], alpha=0.8, edgecolor='gray', linewidth=1.5)
        
        cumulative = [c + f for c, f in zip(cumulative, frontend_values)]
        p4 = ax1.bar(x_pos, backend_bound, width, bottom=cumulative,
                     label='Backend_bound', color=color_map[3], alpha=0.8, edgecolor='gray', linewidth=1.5)

        # Configurar etiquetas del eje X con nombre y tiempo
        x_labels = [f"{name}\n({time:.2f}s)" for name, time in zip(app_names, app_times)]
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(x_labels, fontsize=12)
        
        ax1.set_ylabel('Percentage of Time Execution', fontsize=18)
        ax1.tick_params(axis='y', labelsize=18)
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=None))
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Eje secundario para IPC
        ax2 = ax1.twinx()
        ax2.scatter(x_pos, ipc_values, s=100, color='white', edgecolor='black', linewidth=2, zorder=5, label='IPC')
        ax2.yaxis.set_major_locator(mtick.MultipleLocator(0.5))
        ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f'))
        ax2.set_ylabel('IPC', fontsize=18)
        ax2.tick_params(axis='y', labelsize=18)
        ax2.set_ylim(0, 5)
        
        # Leyenda
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=14, ncol=6)
        
        plt.tight_layout()
        
        output_filename = '../topdown_all_apps.png'
        
        plt.savefig(output_filename, dpi=100, bbox_inches='tight')
        print(f"Gráfica guardada: {output_filename}")
        plt.close()
    else:
        print("No se encontraron datos para graficar")

    data.clear()  # Limpiar datos para el siguiente archivo

if __name__ == "__main__":    
    main()
