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
            
            # Agrupar en conjuntos de 4
            for i in range(0, len(datos), 4):
                if i + 3 < len(datos):
                    app_name = datos[i]
                    cores = datos[i+1]
                    instr= datos[i+2]
                    cycles = datos[i+3]
                    
                    ipc_value = float(instr) / float(cycles) if float(cycles) != 0 else 0
                    if app_name in data:
                        data[app_name].append(ipc_value)
                    else:
                        data[app_name] = [ipc_value]
    
        # Graficar todas las aplicaciones en una sola gráfica
        if data:
            plt.figure(figsize=(14, 7))
            
            for app_name, ipc_values in data.items():
                tiempo = np.arange(len(ipc_values))
                plt.plot(tiempo, ipc_values, linewidth=1, marker='o', markersize=4, label=app_name)
            
            plt.xlabel('Quantums', fontsize=12)
            plt.title('IPC dinámico', fontsize=14)
            plt.grid(True, alpha=0.3)
            plt.legend(loc='best', fontsize=10)
            plt.tight_layout()
            
            # Guardar figura
            output_filename = '../' + archivo + '.png'
            plt.savefig(output_filename, dpi=100)
            print(f"Gráfica guardada: {output_filename}")
            plt.close()
        else:
            print("No se encontraron datos para graficar")

        data.clear()  # Limpiar datos para el siguiente archivo

if __name__ == "__main__":    
    main()
