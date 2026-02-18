#!/usr/bin/python

import sys
import os
from pathlib import Path

def validar_datos(app_name, core_type, tiempo):
    if tiempo < 1:
        # Buscar el CSV correspondiente a esta app y core
        csv_files = [f for f in os.listdir('.') if f.startswith(app_name + '-' + core_type) and f.endswith('.csv')]
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                # Si el CSV tiene solo 1 línea (o está vacío), hay error
                if len(df) <= 1:
                    print(f"Advertencia: {csv_file} tiene solo {len(df)} línea(s). Puede haber un error de ejecución.")
                    return False
            except Exception as e:
                print(f"Error al leer {csv_file}: {e}")
                return False
    return True

def main():
    lista = sys.argv[1:]
    
    if not lista:
        print("Uso: python graficar.py archivo1-core archivo2-core ...")
        print("Ejemplo: python graficar.py app1-E app1-P app2-E app2-P")
        return
    
    datos = []
    
    for archivo in lista:
        try:
            # Extraer nombre de app y tipo de core del nombre del archivo
            nombre_base = Path(archivo).stem  # Elimina la extensión
            partes = nombre_base.split('-')
            
            if len(partes) < 2:
                print(f"Advertencia: nombre de archivo {archivo} no tiene formato correcto (app-core)")
                continue
            
            app = partes[0]  # Todo menos la última parte es el app
            core = partes[1]  # Última parte es el core (P o E)
            
            # Leer el tiempo del archivo
            with open(archivo, 'r') as f:
                contenido = f.read().strip()
                if not contenido:
                    print(f"Error: {archivo} está vacío")
                    continue
                tiempo = float(contenido)
            
            # Validar datos
            if not validar_datos(app, core, tiempo):
                print(f"Datos inválidos para {archivo}, saltando...")
                continue
            
            tipo_core = "P" if int(core) > 14 else "E"
            datos.append({'App': app, 'Tipo Core': tipo_core, 'Tiempo (s)': tiempo})
            print(f"✓ {app}: Core {core} = {tiempo:.4f}s")
            
        except FileNotFoundError:
            print(f"Error: archivo {archivo} no encontrado")
        except ValueError:
            print(f"Error: no se puede convertir el tiempo en {archivo} a float")
        except Exception as e:
            print(f"Error procesando {archivo}: {e}")
    
    if not datos:
        print("No hay datos válidos para graficar")
        return
    
    # Crear DataFrame
    df = pd.DataFrame(datos)
    
    # Guardar en CSV
    csv_out = 'resultados_graficos.csv'
    df.to_csv(csv_out, index=False)
    print(f"\n✓ Datos guardados en {csv_out}")
    

if __name__ == "__main__":    
    main()
