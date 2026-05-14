#!/usr/bin/python

# Comparativa entre P_cores y E_cores para cada aplicación
# mostrando el topdown de cada uno y el speedup del IPC en una gráfica de barras apiladas. 

import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

def main():

    if len(sys.argv) < 3:
        print("Uso: python graficar.py P_cores E_cores")
        return
    
    app_names = []  
    app_times = []
    retiring_values = []
    bad_speculation_values = []
    frontend_values = []
    backend_bound = []
    memory_bound_values = []
    core_bound_values = []
    ipc_values = []
    speedup_values = []

    norm = float(3/2.2)

    P_cores = sys.argv[1]
    E_cores = sys.argv[2]

    f_p = open(P_cores, 'r')
    f_e = open(E_cores, 'r')

    # Leer ambos archivos simultáneamente
    for line_P, line_E in zip(f_p, f_e):
        line_P = line_P.strip()
        line_E = line_E.strip()

        if not line_P or not line_E or line_P.startswith("app") or line_E.startswith("app"):
            continue
        
        # Parse: App,Time,Retiring,Bad Speculation,Frontend Bound,Backend Bound,IPC
        datos_P = line_P.split(",")
        datos_E = line_E.split(",")

        if datos_P[0] != datos_E[0]:
            print(f"Error: Las aplicaciones no coinciden: {datos_P[0]} vs {datos_E[0]}")
            continue

        speedup_tiempo = float(datos_E[1]) / float(datos_P[1])
        app_names.append(datos_P[0])
        
        # P_cores: índices correctos para cpu_core
        slots_P = float(datos_P[5])  # cpu_core/TOPDOWN.SLOTS/
        retiring_P = float(datos_P[6])  # cpu_core/topdown-retiring/
        bad_spec_P = float(datos_P[7])  # cpu_core/topdown-bad-spec/
        fe_bound_P = float(datos_P[8])  # cpu_core/topdown-fe-bound/
        be_bound_P = float(datos_P[9])  # cpu_core/topdown-be-bound/
        mem_bound_P = float(datos_P[10])  # cpu_core/topdown-mem-bound/
        
        # E_cores: índices correctos para cpu_atom (no tiene TOPDOWN.SLOTS, usar cycles*4)
        cycles_E = float(datos_E[4])  # cpu_atom/cycles/
        slots_E = cycles_E * 5  # Atom tiene 5 slots por ciclo
        retiring_E = float(datos_E[5])  # cpu_atom/topdown-retiring/
        bad_spec_E = float(datos_E[6])  # cpu_atom/topdown-bad-spec/
        fe_bound_E = float(datos_E[7])  # cpu_atom/topdown-fe-bound/
        be_bound_E = float(datos_E[8])  # cpu_atom/topdown-be-bound/
        
        retiring_values.append((retiring_P / slots_P, norm * retiring_E / slots_E))
        bad_speculation_values.append((bad_spec_P / slots_P, norm * bad_spec_E / slots_E))
        frontend_values.append((fe_bound_P / slots_P, norm * fe_bound_E / slots_E))
        backend_bound.append(norm * be_bound_E / slots_E)
        memory_bound_values.append(mem_bound_P / slots_P)
        core_bound_values.append(be_bound_P / slots_P - mem_bound_P / slots_P)
        ipc_values.append((float(datos_P[3]) / float(datos_P[4]), float(datos_E[3]) / float(datos_E[4])))
        speedup_values.append(ipc_values[-1][0] / ipc_values[-1][1] * norm)

    # # Ordenar todos los datos por speedup de menor a mayor
    # sorted_indices = sorted(range(len(speedup_values)), key=lambda i: speedup_values[i])
    
    # app_names = [app_names[i] for i in sorted_indices]
    # retiring_values = [retiring_values[i] for i in sorted_indices]
    # bad_speculation_values = [bad_speculation_values[i] for i in sorted_indices]
    # frontend_values = [frontend_values[i] for i in sorted_indices]
    # backend_bound = [backend_bound[i] for i in sorted_indices]
    # memory_bound_values = [memory_bound_values[i] for i in sorted_indices]
    # core_bound_values = [core_bound_values[i] for i in sorted_indices]
    # ipc_values = [ipc_values[i] for i in sorted_indices]
    # speedup_values = [speedup_values[i] for i in sorted_indices]

    fig, ax1 = plt.subplots(figsize=(21, 9))
    x_pos = np.arange(len(app_names))
    width = 0.8

    # Colores para las barras
    color_map = ["cornflowerblue", "gold", "lightgreen", "lightcoral", "crimson"]

    max_comulative = 1.0
    # Graficar 2 barras apiladas para cada aplicación una para el topdown de P_cores y otra para el de E_cores
    for i in range(len(app_names)):
        p1 = ax1.bar(x_pos[i] - width/4, retiring_values[i][0], width/2, label='Retiring' if i == 0 else "", color=color_map[0], alpha=0.8, edgecolor='gray', linewidth=3)
        p2 = ax1.bar(x_pos[i] - width/4, bad_speculation_values[i][0], width/2, bottom=retiring_values[i][0], 
                     label='Bad speculation' if i == 0 else "", color=color_map[1], alpha=0.8, edgecolor='gray', linewidth=3)
        
        cumulative_P = retiring_values[i][0] + bad_speculation_values[i][0]
        p3 = ax1.bar(x_pos[i] - width/4, frontend_values[i][0], width/2, bottom=cumulative_P,
                     label='Frontend' if i == 0 else "", color=color_map[2], alpha=0.8, edgecolor='gray', linewidth=3)
        
        cumulative_P += frontend_values[i][0]
        p42 = ax1.bar(x_pos[i] - width/4, core_bound_values[i], width/2, bottom=cumulative_P,
                     label='Core_bound' if i == 0 else "", color=color_map[3], alpha=0.8, edgecolor='gray', linewidth=3)
        
        cumulative_P += core_bound_values[i]
        p4 = ax1.bar(x_pos[i] - width/4, memory_bound_values[i], width/2, bottom=cumulative_P,
                     label='Memory_bound' if i == 0 else "", color=color_map[4], alpha=0.8, edgecolor='gray', linewidth=3)

        cumulative_P += core_bound_values[i]
        if cumulative_P > max_comulative:
            max_comulative = cumulative_P

        # Barras para E_cores
        p5 = ax1.bar(x_pos[i] + width/4, retiring_values[i][1], width/2, color=color_map[0], alpha=0.5, edgecolor='gray', linewidth=3)
        p6 = ax1.bar(x_pos[i] + width/4, bad_speculation_values[i][1], width/2, bottom=retiring_values[i][1], 
                     color=color_map[1], alpha=0.5, edgecolor='gray', linewidth=3)
        
        cumulative_E = retiring_values[i][1] + bad_speculation_values[i][1]
        p7 = ax1.bar(x_pos[i] + width/4, frontend_values[i][1], width/2, bottom=cumulative_E,
                     color=color_map[2], alpha=0.5, edgecolor='gray', linewidth=3)
        cumulative_E += frontend_values[i][1]
        p8 = ax1.bar(x_pos[i] + width/4, backend_bound[i], width/2, bottom=cumulative_E, label='Backend_bound' if i == 0 else "",
                     color=color_map[3], alpha=0.5, edgecolor='gray', linewidth=3)
        
        x_labels = [name for name in app_names]
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(x_labels, fontsize=20, rotation=90)
        ax1.set_ylabel('Percentage of Time Execution', fontsize=20)
        ax1.tick_params(axis='y', labelsize=18)
        ax1.yaxis.set_major_locator(mtick.MultipleLocator(0.1))
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=None))
        ax1.set_ylim(0, 1.5)
        ax1.set_xlim(-0.5, len(app_names) - 0.5)
        ax1.grid(True, alpha=0.3, axis='y')

        ax2 = ax1.twinx()
        ax2.scatter(x_pos, speedup_values, s=100, color='white', edgecolor='black', linewidth=2, zorder=5, label='Speedup')
        ax2.yaxis.set_major_locator(mtick.MultipleLocator(0.25))
        ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f'))
        ax2.set_ylabel('Speedup IPC', fontsize=20)
        ax2.tick_params(axis='y', labelsize=18)
        ax2.set_ylim(1, 3)

        # Leyenda fuera de la gráfica arriba en el centro
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='center', bbox_to_anchor=(0.5, 1.15), fontsize=20, ncol=7, frameon=True)
        
        plt.tight_layout()
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15)

    output_filename = 'topdown_both.png'
        
    plt.savefig(output_filename, dpi=100, bbox_inches='tight')
    print(f"Gráfica guardada: {output_filename}")
    plt.close()

if __name__ == "__main__":    
    main()
