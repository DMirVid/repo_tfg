
import sys


QUANTUM = 100 # 100ms

def cmp(name):
    return name.lower()


def main():

    if len(sys.argv) < 4:
        print("Uso: python graficar.py num_eventos core archivo1 [archivo2 ...]")
        return

    eventos = int(sys.argv[1])
    core = sys.argv[2]
    archivos = sys.argv[3:]
    data = {}

    for archivo in archivos:
        try:
            with open(archivo, 'r') as f:
                lineas = f.readlines()
        except Exception as e:
            print(f"Error abriendo {archivo}: {e}")
            continue

        try:
            with open(archivo, 'r') as f:
                lineas = f.readlines()
        except Exception as e:
            print(f"Error abriendo {archivo}: {e}")
            return {}
        
        # Procesar cada línea del archivo
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue
            
            # Parse: name;cores;instructions;cycles;...
            datos = linea.split(";")
            
            # Agrupar en conjuntos de 23 + plus
            for i in range(0, len(datos), eventos + 2):
                if i + eventos < len(datos):
                    if linea.startswith("name"):
                        data["aaacabecera"] = datos[i:i+eventos]
                        continue
                    app_name = datos[i]
                    values = datos[i+1:i+eventos]
                    if app_name in data:
                        data[app_name].append(values)
                    else:
                        data[app_name] = [values]


     # Graficar todas las aplicaciones en una sola gráfica de barras
    if data:
        apps_list = list(sorted(data.items(), key=lambda x: cmp(x[0])))

        
        with open("../topdown_all_"+core+".csv", "w") as f:
            f.write("app_name,time_seconds," + ",".join(data["aaacabecera"][1:]) + "\n")
            for app_name, topdown in apps_list:
                # Encontrar el índice donde la app termina (ciclos dejan de aumentar)
                last_idx = len(topdown) - 1
                for i in range(len(topdown) - 1, -1, -1):
                    if i == 0 or topdown[i][2] > topdown[i-1][2]:  # ciclos en posición 2
                        last_idx = i
                        break
                
                # Calcular tiempo: índice * quantum (en milisegundos) / 1000 (para segundos)
                time_seconds = last_idx * QUANTUM / 1000.0
                
                # Obtener la última muestra de la app
                final_sample = topdown[last_idx]
                f.write(f"{app_name},{time_seconds},{','.join(final_sample[0:])}\n")
       
    else:
        print("No se encontraron datos")

    data.clear()  # Limpiar datos para el siguiente archivo

    print("Finalizado")
                    


if __name__ == "__main__":    
    main()