#!/usr/bin/python
import sys

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
            
            for i in range(0, len(datos), 9):
                if i + 8 < len(datos):
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

        cabecera = "App,Time,Retiring,Bad Speculation,Frontend Bound,Backend Bound,IPC\n"
        
        with open("topdown_all_P.csv", "w") as f:
            f.write(cabecera)
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

                f.write(f"{app_name},{time_seconds},{final_sample[0]},{final_sample[1]},{final_sample[2]},{final_sample[3]},{final_sample[4]}\n")
       
    else:
        print("No se encontraron datos")

    data.clear()  # Limpiar datos para el siguiente archivo

if __name__ == "__main__":    
    main()
