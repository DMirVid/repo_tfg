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
    len_datos = 8
    resta = 1
    core = sys.argv[1]
    if core == 'P':
        ancho_issue = 6
        len_datos = 24
        resta = 0
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
            for i in range(0, len(datos), len_datos):
                if i + len_datos - 1 < len(datos):
                    app_name = datos[i]
                    cores = datos[i+1]
                    instr = float(datos[i+2])
                    cycles = float(datos[i+3])
                    if cycles == 0:
                        cycles = 1
                    
                    retiring = float(datos[i+5-resta])
                    bad_speculation = float(datos[i+6-resta])
                    frontend = float(datos[i+7-resta])
                    backend_bound = float(datos[i+8-resta])

                    ipc = instr / cycles
                    total = cycles * ancho_issue
                    total = total if total != 0 else 1
                    backend_bound_norm = backend_bound / total

                    if core == 'P':
                        memory_bound = float(datos[i+9])
                        memory_bound_norm = memory_bound / total
                        core_bound = backend_bound_norm - memory_bound_norm

                        l1_miss = float(datos[i+21])
                        mpki_total = (l1_miss / instr) * 1000
                    if core == 'P':
                        if app_name in data:
                            data[app_name].append((ipc, backend_bound_norm, mpki_total, core_bound, memory_bound_norm))
                        else:
                            data[app_name] = [(ipc, backend_bound_norm, mpki_total, core_bound, memory_bound_norm)]
                    else:
                        if app_name in data:
                            data[app_name].append((ipc, backend_bound_norm))
                        else:
                            data[app_name] = [(ipc, backend_bound_norm)]

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
                ax1.plot(tiempo[:len(ipc_list)], ipc_list, 'o-', label=app_name, color=color, markersize=1, linewidth=1)
            
            str_t = f'Time (s)'
            ax1.set_xlabel(str_t, fontsize=14)
            ax1.set_ylabel('IPC', fontsize=14)
            ax1.tick_params(axis='both', labelsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=10, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=True)
            ax1.set_title('')
            plt.subplots_adjust(top=0.88)
            plt.tight_layout()
            output_filename1 = "../" + archivo.replace('.csv', '_' + core + '_ipc.png')
            plt.savefig(output_filename1, dpi=100)
            print(f"Gráfica IPC guardada: {output_filename1}")
            plt.close()

            # Gráfica 2: Backend Bound
            fig5, ax5 = plt.subplots(figsize=(14, 7))
            for (app_name, values), color in zip(data.items(), colors):
                backend_bound_list = [v[1] for v in values]
                ax5.plot(tiempo[:len(backend_bound_list)], backend_bound_list, '^-', label=app_name, 
                        color=color, markersize=1, linewidth=1)
            
            ax5.set_xlabel(str_t, fontsize=14)
            ax5.set_ylabel('Backend Bound', fontsize=14)
            ax5.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
            ax5.tick_params(axis='both', labelsize=12)
            ax5.grid(True, alpha=0.3)
            ax5.legend(fontsize=10, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=True)
            ax5.set_title('')
            plt.subplots_adjust(top=0.88)
            plt.tight_layout()
            output_filename5 = "../" + archivo.replace('.csv', '_' + core + '_backend_bound.png')
            plt.savefig(output_filename5, dpi=100)
            print(f"Gráfica Backend Bound guardada: {output_filename5}")
            plt.close()
            
            if core == 'P':
                # Gráfica 2: MPKI
                fig2, ax2 = plt.subplots(figsize=(14, 7))
                for (app_name, values), color in zip(data.items(), colors):
                    mpki_list = [v[2] for v in values]
                    ax2.plot(tiempo[:len(mpki_list)], mpki_list, 'o-', label=app_name, color=color, markersize=1, linewidth=1)
                
                ax2.set_xlabel(str_t, fontsize=14)
                ax2.set_ylabel('MPKI', fontsize=14)
                ax2.tick_params(axis='both', labelsize=12)
                ax2.grid(True, alpha=0.3)
                ax2.legend(fontsize=10, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=True)
                ax2.set_title('')
                plt.subplots_adjust(top=0.88)
                plt.tight_layout()
                output_filename2 = "../" + archivo.replace('.csv', '_' + core + '_mpki.png')
                plt.savefig(output_filename2, dpi=100)
                print(f"Gráfica MPKI guardada: {output_filename2}")
                plt.close()
            
            
                # Gráfica 3: Memory Bound
                fig3, ax3 = plt.subplots(figsize=(14, 7))
                for (app_name, values), color in zip(data.items(), colors):
                    memory_bound_list = [v[3] for v in values]
                    ax3.plot(tiempo[:len(memory_bound_list)], memory_bound_list, 'o-', label=app_name, 
                            color=color, markersize=1, linewidth=1)
                
                ax3.set_xlabel(str_t, fontsize=14)
                ax3.set_ylabel('Memory Bound', fontsize=14)
                ax3.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
                ax3.tick_params(axis='both', labelsize=12)
                ax3.grid(True, alpha=0.3)
                ax3.legend(fontsize=10, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=True)
                ax3.set_title('')
                plt.subplots_adjust(top=0.88)
                plt.tight_layout()
                output_filename3 = "../" + archivo.replace('.csv', '_' + core + '_memory_bound.png')
                plt.savefig(output_filename3, dpi=100)
                print(f"Gráfica Memory Bound guardada: {output_filename3}")
                plt.close()
                
                # Gráfica 4: Core Bound
                fig4, ax4 = plt.subplots(figsize=(14, 7))
                for (app_name, values), color in zip(data.items(), colors):
                    core_bound_list = [v[4] for v in values]
                    ax4.plot(tiempo[:len(core_bound_list)], core_bound_list, 's-', label=app_name, 
                            color=color, markersize=1, linewidth=1)
                
                ax4.set_xlabel(str_t, fontsize=14)
                ax4.set_ylabel('Core Bound', fontsize=14)
                ax4.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
                ax4.tick_params(axis='both', labelsize=12)
                ax4.grid(True, alpha=0.3)
                ax4.legend(fontsize=10, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=True)
                ax4.set_title('')
                plt.subplots_adjust(top=0.88)
                plt.tight_layout()
                output_filename4 = "../" + archivo.replace('.csv', '_' + core + '_core_bound.png')
                plt.savefig(output_filename4, dpi=100)
                print(f"Gráfica Core Bound guardada: {output_filename4}")
                plt.close()
            
        else:
            print(f"No se encontraron datos para graficar en {archivo}")

if __name__ == "__main__":    
    main()
