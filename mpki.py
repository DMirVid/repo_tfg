#!/usr/bin/python

# Calcula y grafica los MPKI (Misses Per Kilo Instruction) para L1, L2, L3

import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

QUANTUM = 200 # 200ms

def main():
    data = {}

    if len(sys.argv) < 2:
        print("Uso: python mpki.py archivo1 [archivo2 ...]")
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
            
            # Parse: name;core;cpu_core/instructions/;...;cpu_core/mem_load_retired.l1_miss/;cpu_core/mem_load_retired.l2_miss/;cpu_core/mem_load_retired.l3_miss/
            datos = linea.split(";")
            
            if len(datos) < 24:  # Necesitamos al menos 23 campos
                continue
            for i in range(0, len(datos), 24):
                app_name = datos[i]

                try:
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

                    total = frontend + retiring + bad_speculation + backend_bound
                    total = total if total != 0 else 1  # Evitar división por cero
                    retiring_pct = retiring / total
                    bad_speculation_pct = bad_speculation / total
                    frontend_pct = frontend / total
                    backend_bound_pct = backend_bound / total

                    memory_bound = memory_bound / total
                    core_bound = backend_bound_pct - memory_bound

                    l1_miss = float(datos[i+21])
                    l2_miss = float(datos[i+22])
                    l3_miss = float(datos[i+23])
                except (ValueError, IndexError):
                    continue
            
                if instr == 0:
                    instr = 1
                
                # Calcular MPKI = (misses / instructions) * 1000
                mpki_l1 = (l1_miss / instr) * 1000
                mpki_l2 = (l2_miss / instr) * 1000
                mpki_l3 = (l3_miss / instr) * 1000
                
                # Calcular GIPS (Giga Instrucciones Por Segundo)
                # Asumimos frecuencia típica de 3.0 GHz
                frequency_ghz = 3.0
                gips = (instr / cycles) * frequency_ghz
                
                if app_name in data:
                    data[app_name].append((mpki_l1, mpki_l2, mpki_l3, instr, ipc, retiring_pct, bad_speculation_pct, 
                                          frontend_pct, backend_bound_pct, memory_bound, core_bound, gips))
                else:
                    data[app_name] = [(mpki_l1, mpki_l2, mpki_l3, instr, ipc, retiring_pct, bad_speculation_pct, 
                                      frontend_pct, backend_bound_pct, memory_bound, core_bound, gips)]

    # Graficar MPKI para todas las aplicaciones
    if data:
        for app_name, mpki_data in data.items():
            
            # Encontrar el índice donde la app termina (instrucciones dejan de aumentar)
            last_idx = len(mpki_data) - 1
            for i in range(len(mpki_data) - 1, -1, -1):
                if i == 0 or mpki_data[i][3] > mpki_data[i-1][3]:  # instrucciones en posición 3
                    last_idx = i
                    break
            
            fig, ax = plt.subplots(figsize=(14, 10))
            
            # Usar los últimos valores de MPKI
            final_mpki_l1 = mpki_data[last_idx][0]
            final_mpki_l2 = mpki_data[last_idx][1]
            final_mpki_l3 = mpki_data[last_idx][2]
            final_ipc = mpki_data[last_idx][4]
            final_retiring = mpki_data[last_idx][5]
            final_bad_spec = mpki_data[last_idx][6]
            final_frontend = mpki_data[last_idx][7]
            final_backend = mpki_data[last_idx][8]
            final_memory = mpki_data[last_idx][9]
            final_core = mpki_data[last_idx][10]
            final_gips = mpki_data[last_idx][11]
            
            # Datos para el gráfico de barras
            mpki_values = [final_mpki_l1, final_mpki_l2, final_mpki_l3]
            cache_names = ['L1 MPKI', 'L2 MPKI', 'L3 MPKI']
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            # Crear gráfico de barras
            bars = ax.bar(cache_names, mpki_values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
            
            # Agregar valores en las barras
            for i, (bar, val) in enumerate(zip(bars, mpki_values)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:.2f}',
                        ha='center', va='bottom', fontsize=14, fontweight='bold')
            
            ax.set_ylabel('MPKI (Misses Per Kilo Instruction)', fontsize=16, fontweight='bold')
            ax.tick_params(axis='x', labelsize=14)
            ax.tick_params(axis='y', labelsize=14)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Agregar título
            ax.set_title(f'Cache MPKI - {app_name}', fontsize=18, fontweight='bold')
            
            # Crear texto con información adicional fuera de la gráfica
            info_text = f"""Performance Metrics:
            
IPC: {final_ipc:.3f} Instructions/Cycle
GIPS: {final_gips:.3f} Giga Instructions/Second

Top-Down Analysis:
  • Retiring: {final_retiring*100:.1f}%
  • Bad Speculation: {final_bad_spec*100:.1f}%
  • Frontend Bound: {final_frontend*100:.1f}%
  • Backend Bound: {final_backend*100:.1f}%
    - Memory Bound: {final_memory*100:.1f}%
    - Core Bound: {final_core*100:.1f}%"""
            
            # Añadir texto a la figura fuera del área de la gráfica
            fig.text(0.98, 0.50, info_text, fontsize=11, verticalalignment='center',
                    horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                    family='monospace')
            
            plt.tight_layout()
            
            output_filename = '../' + app_name + '_mpki.png'
            
            plt.savefig(output_filename, dpi=100, bbox_inches='tight')
            print(f"Gráfica MPKI guardada: {output_filename}")
            plt.close()
    else:
        print("No se encontraron datos para graficar")
    
    data.clear()

if __name__ == "__main__":    
    main()
