#!/usr/bin/python   

## Programa que imprime por pantalla cunatos cambios de núcleo se realizaron urante la ejecución.
## Es llamado por otro programa.
## Daniel Mirón

import sys
from lib import leer_datos_juntos
import numpy as np

ANCHO_ISSUE_P = 6
ANCHO_ISSUE_E = 5

QUANTUM = 200

def main():

    archivos = sys.argv[1:]
    eventosP=15
    eventosE=10
    data = {}

    for archivo in archivos:
    
        try:
            with open(archivo, 'r') as f:
                lineas = f.readlines()
        except Exception as e:
            print(f"Error abriendo {archivo}: {e}")
            return {}
        
        set_nombres = set()

        # Procesar cada línea del archivo
        for linea in lineas:
            linea = linea.strip()
            if not linea or linea.startswith("name"):
                continue
            
            # Parse: name;cores;instructions;cycles;...
            datos = linea.split(";")
        
            set_nombres.clear()
            
            for i in range(0, len(datos), 2 + eventosP + eventosE):
                if i + 2 + eventosP + eventosE - 1 < len(datos):
                    app_name = datos[i]
                    core = int(datos[i+1])

                    if not set_nombres or app_name not in set_nombres:
                        set_nombres.add(app_name)
                    else:
                        set_nombres.add(app_name + "REPEAT")
                        app_name += "REPEAT"

                    instr = 0
                    cycles = 0
                    instrE = 0
                    cyclesE = 0

                    ## Leer eventos P
                    if core < 16:
                        instr = float(datos[i+2])
                        cycles = float(datos[i+3])
                        if cycles == 0:
                            cycles = 1
                        
                
                    else:
                        salto = eventosP + 2
                        instrE = float(datos[i+salto])
                        cyclesE = float(datos[i+1+salto])
                        if cyclesE == 0:
                            cyclesE = 1
                        

                    if app_name in data:
                        instr = instr if instr != 0 else data[app_name][-1][1]
                        cycles = cycles if cycles != 0 else data[app_name][-1][2]
                        instrE = instrE if instrE != 0 else data[app_name][-1][3]
                        cyclesE = cyclesE if cyclesE != 0 else data[app_name][-1][4]
                        data[app_name].append((core, instr, cycles, instrE, cyclesE))
                    else:
                        data[app_name] = [(core, instr, cycles, instrE, cyclesE)]
            

        if data:
            apps_list = list(data.items())
            
            for app_name, topdown in apps_list:

                tiempo = [x * QUANTUM / 1000.0 for x in  np.arange(len(topdown))] 

                core = [x[0] for x in topdown]
                ipc = (data[app_name][-1][1]+data[app_name][-1][3])/(data[app_name][-1][2]+data[app_name][-1][4])


                cambios_core = 0
                for i in range(1, len(core)):
                    if core[i] != core[i-1] and (core[i] > 16 and core[i-1] < 16 or core[i] < 16 and core[i-1] > 16):
                        cambios_core += 1

                print(f"{app_name},{ipc},{cambios_core},{tiempo[-1]}\n")
                
        else:
            print("No se han encontrado datos para graficar.")
        
        data.clear() 

if __name__ == "__main__":    
    main()
