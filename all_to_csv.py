
import sys


QUANTUM = 100  # 100ms

def cmp(name):
    return name.lower()


def main():

    if len(sys.argv) < 4:
        print("Uso: python all_to_csv.py num_eventos core archivo1 [archivo2 ...]")
        return

    eventos = int(sys.argv[1])
    core = sys.argv[2]
    archivos = sys.argv[3:]
    data = {}
    cabecera = None

    # Procesar todos los archivos
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
            if not linea:
                continue
            
            # Parse: name;cores;instructions;cycles;...
            datos = linea.split(";")
            
            # Guardar cabecera si es la primera línea
            if datos[0].lower() == "name":
                cabecera = datos[0:eventos+2]
                continue
            
            # Agrupar en conjuntos de (eventos + 2) campos
            for i in range(0, len(datos), eventos + 2):
                if i + eventos + 1 < len(datos):
                    app_name = datos[i]
                    values = datos[i+1:i+eventos+2]
                    
                    if app_name not in data:
                        data[app_name] = []
                    data[app_name].append(values)

    # Escribir CSV con cabecera y tiempo
    if data and cabecera:
        apps_list = list(sorted(data.items(), key=lambda x: cmp(x[0])))
        
        output_file = f"../topdown_all_{core}.csv"
        with open(output_file, "w") as f:
            # Escribir cabecera
            f.write("app_name,time_seconds," + ",".join(cabecera[1:]) + "\n")
            
            # Escribir datos de cada aplicación
            for app_name, samples in apps_list:
                # Encontrar el índice donde la app termina (ciclos dejan de aumentar)
                last_idx = len(samples) - 1
                for i in range(len(samples) - 1, -1, -1):
                    if i == 0 or int(samples[i][2]) > int(samples[i-1][2]):
                        last_idx = i
                        break
                
                # Calcular tiempo: índice * quantum (en milisegundos) / 1000 (para segundos)
                time_seconds = last_idx * QUANTUM / 1000.0
                
                # Obtener la última muestra de la app
                final_sample = samples[last_idx]
                f.write(f"{app_name},{time_seconds}," + ",".join(final_sample) + "\n")
        
        print(f"Archivo guardado en: {output_file}")
        print(f"Aplicaciones procesadas: {len(apps_list)}")
    else:
        if not cabecera:
            print("Error: No se encontró cabecera en los archivos")
        else:
            print("Error: No se encontraron datos")
                    


if __name__ == "__main__":    
    main()