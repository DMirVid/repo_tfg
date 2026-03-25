#!/usr/bin/python
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
    ipc_values = []
    speedup_values = []

    P_cores = sys.argv[1]
    E_cores = sys.argv[2]

    f_p = open(P_cores, 'r')
    f_e = open(E_cores, 'r')

    # Leer ambos archivos simultáneamente
    for line_P, line_E in zip(f_p, f_e):
        line_P = line_P.strip()
        line_E = line_E.strip()

        if not line_P or not line_E or line_P.startswith("App") or line_E.startswith("App"):
            continue
        
        # Parse: App,Time,Retiring,Bad Speculation,Frontend Bound,Backend Bound,IPC
        datos_P = line_P.split(",")
        datos_E = line_E.split(",")

        if datos_P[0] != datos_E[0]:
            print(f"Error: Las aplicaciones no coinciden: {datos_P[0]} vs {datos_E[0]}")
            continue

        speedup_tiempo = float(datos_P[1]) / float(datos_E[1])
        app_names.append(datos_P[0])

        retiring_values.append((speedup_tiempo * float(datos_P[2]), float(datos_E[2])))
        bad_speculation_values.append((speedup_tiempo * float(datos_P[3]), float(datos_E[3])))
        frontend_values.append((speedup_tiempo * float(datos_P[4]), float(datos_E[4])))
        backend_bound.append((speedup_tiempo * float(datos_P[5]), float(datos_E[5])))
        ipc_values.append((float(datos_P[6]), float(datos_E[6])))
        speedup_values.append(float(datos_P[6]) / float(datos_E[6]))

    fig, ax1 = plt.subplots(figsize=(21, 9))
    x_pos = np.arange(len(app_names))
    width = 0.8

    # Colores para las barras
    color_map = ["cornflowerblue", "gold", "lightgreen", "lightcoral", "crimson"]

    max_comulative = 1.0
    # Graficar 2 barras apiladas para cada aplicación una para el topdown de P_cores y otra para el de E_cores
    for i in range(len(app_names)):
        p1 = ax1.bar(x_pos[i], retiring_values[i][0], width, label='Retiring' if i == 0 else "", color=color_map[0], alpha=0.8, edgecolor='gray', linewidth=3)
        p2 = ax1.bar(x_pos[i], bad_speculation_values[i][0], width, bottom=retiring_values[i][0], 
                     label='Bad speculation' if i == 0 else "", color=color_map[1], alpha=0.8, edgecolor='gray', linewidth=3)
        
        cumulative_P = retiring_values[i][0] + bad_speculation_values[i][0]
        p3 = ax1.bar(x_pos[i], frontend_values[i][0], width, bottom=cumulative_P,
                     label='Frontend' if i == 0 else "", color=color_map[2], alpha=0.8, edgecolor='gray', linewidth=3)
        
        cumulative_P += frontend_values[i][0]
        p4 = ax1.bar(x_pos[i], backend_bound[i][0], width, bottom=cumulative_P,
                     label='Backend_bound' if i == 0 else "", color=color_map[3], alpha=0.8, edgecolor='gray', linewidth=3)
        
        cumulative_P += backend_bound[i][0]
        if cumulative_P > max_comulative:
            max_comulative = cumulative_P

        # Barras para E_cores
        # p5 = ax1.bar(x_pos[i] + width/4, retiring_values[i][1], width/2, color=color_map[0], alpha=0.5, edgecolor='gray', linewidth=3)
        # p6 = ax1.bar(x_pos[i] + width/4, bad_speculation_values[i][1], width/2, bottom=retiring_values[i][1], 
        #              color=color_map[1], alpha=0.5, edgecolor='gray', linewidth=3)
        
        # cumulative_E = retiring_values[i][1] + bad_speculation_values[i][1]
        # p7 = ax1.bar(x_pos[i] + width/4, frontend_values[i][1], width/2, bottom=cumulative_E,
        #              color=color_map[2], alpha=0.5, edgecolor='gray', linewidth=3)
        # cumulative_E += frontend_values[i][1]
        # p8 = ax1.bar(x_pos[i] + width/4, backend_bound[i][1], width/2, bottom=cumulative_E,
        #              color=color_map[3], alpha=0.5, edgecolor='gray', linewidth=3)
        
        x_labels = [name for name in app_names]
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(x_labels, fontsize=20, rotation=90)
        ax1.set_ylabel('Percentage of Time Execution', fontsize=20)
        ax1.tick_params(axis='y', labelsize=18)
        ax1.yaxis.set_major_locator(mtick.MultipleLocator(0.1))
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=None))
        ax1.set_ylim(0, max_comulative)
        ax1.set_xlim(-0.5, len(app_names) - 0.5)
        ax1.grid(True, alpha=0.3, axis='y')

        ax2 = ax1.twinx()
        ax2.scatter(x_pos, speedup_values, s=100, color='white', edgecolor='black', linewidth=2, zorder=5, label='SpeedUp')
        ax2.yaxis.set_major_locator(mtick.MultipleLocator(0.25))
        ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f'))
        ax2.set_ylabel('SpeedUp IPC', fontsize=20)
        ax2.tick_params(axis='y', labelsize=18)
        ax2.set_ylim(1, 2.5)

        # Leyenda fuera de la gráfica arriba en el centro
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='center', bbox_to_anchor=(0.5, 1.15), fontsize=20, ncol=6, frameon=True)
        
        plt.tight_layout()
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15)

    output_filename = 'topdown_both.png'
        
    plt.savefig(output_filename, dpi=100, bbox_inches='tight')
    print(f"Gráfica guardada: {output_filename}")
    plt.close()

if __name__ == "__main__":    
    main()
