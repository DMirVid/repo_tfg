#!/usr/bin/python
import sys
import matplotlib.pyplot as plt
import numpy as np

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
            
            # Agrupar en conjuntos de 7
            for i in range(0, len(datos), 7):
                if i + 3 < len(datos):
                    app_name = datos[i]
                    cores = datos[i+1]
                    instr= datos[i+2]
                    cycles = datos[i+3]
                    mem_bound = float(datos[i+5])
                    backend_bound = float(datos[i+6])

                    core_bound = backend_bound - mem_bound
                    core_per = (core_bound/backend_bound) * 100
                    mem_per = (mem_bound/backend_bound) * 100

                    if app_name in data:
                        data[app_name].append((core_per, mem_per))
                    else:
                        data[app_name] = [(core_per, mem_per)]
    
        # Graficar todas las aplicaciones en gráficas individuales
        if data:
            apps_list = list(data.items())
            
            for app in apps_list:
                app_name, backend = app
                plt.figure(figsize=(16, 8))
                
                tiempo = np.arange(len(backend))
                core_per_list = [x[0] for x in backend]
                mem_per_list = [x[1] for x in backend]

                plt.stackplot(tiempo, core_per_list, mem_per_list,
                              labels=[f"{app_name}_core", f"{app_name}_mem"], alpha=0.8)
                
                plt.xlabel('Quantums', fontsize=18)
                plt.ylabel('Backend bound (%)', fontsize=18)
                plt.xticks(fontsize=18)
                plt.yticks(range(0, 101, 10), fontsize=18)
                plt.grid(True, alpha=0.3)
                plt.xlim(0, 6000)
                plt.ylim(0, 100)
                plt.subplots_adjust(top=0.85)
                plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), fontsize=16, ncol=4)
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
