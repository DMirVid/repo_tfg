### DEFINICIONES
ANCHO_ISSUE_P = 6
ANCHO_ISSUE_E = 5


### Lee un archivo de datos en formato csv y el core en el que se ejecuta
### Devuelve un diccionario con la siguiente estructura:
### {
###     P core -> app_name: [(instr, cycles, ipc, retiring_norm, bad_speculation_norm, frontend_norm, backend_bound_norm, core_bound, memory_bound_norm,  mpki_l1_total, mpki_l2_total, mpki_l3_total), ...],
###     E core -> app_name: [(instr, cycles, ipc, retiring_norm, bad_speculation_norm, frontend_norm, backend_bound_norm), ...]
### }
def leer_datos(core, archivo):

    ancho_issue = ANCHO_ISSUE_E
    len_datos = 8
    resta = 1
    if core == 'P':
        ancho_issue = ANCHO_ISSUE_P
        len_datos = 24
        resta = 0

    data = {}  # app_name -> list of tuples
    
    try:
        with open(archivo, 'r') as f:
            lineas = f.readlines()
    except Exception as e:
        print(f"Error abriendo {archivo}: {e}")
        return {}
    
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

                retiring_norm = retiring / total
                bad_speculation_norm = bad_speculation / total
                frontend_norm = frontend / total
                backend_bound_norm = backend_bound / total

                if core == 'P':
                    memory_bound = float(datos[i+9])
                    memory_bound_norm = memory_bound / total
                    core_bound = backend_bound_norm - memory_bound_norm

                    l1_miss = float(datos[i+21])
                    l2_miss = float(datos[i+22])
                    l3_miss = float(datos[i+23])
                    mpki_l1_total = (l1_miss / instr) * 1000
                    mpki_l2_total = (l2_miss / instr) * 1000
                    mpki_l3_total = (l3_miss / instr) * 1000
                if core == 'P':
                    if app_name in data:
                        data[app_name].append((instr, cycles, ipc, retiring_norm, bad_speculation_norm, frontend_norm, backend_bound_norm, core_bound, memory_bound_norm, mpki_l1_total, mpki_l2_total, mpki_l3_total))
                    else:
                        data[app_name] = [(instr, cycles, ipc, retiring_norm, bad_speculation_norm, frontend_norm, backend_bound_norm, core_bound, memory_bound_norm, mpki_l1_total, mpki_l2_total, mpki_l3_total)]
                else:
                    if app_name in data:
                        data[app_name].append((instr, cycles, ipc, retiring_norm, bad_speculation_norm, frontend_norm, backend_bound_norm))
                    else:
                        data[app_name] = [(instr, cycles, ipc, retiring_norm, bad_speculation_norm, frontend_norm, backend_bound_norm)]
    
    return data



### Lee un archivo de datos en formato csv y el core en el que se ejecuta
### Primero los todos los eventos del core P y luego los del E
### Devuelve un diccionario con la siguiente estructura:
### {
###    app_name: [(core, instr, cycles, ipc, retiring_norm, bad_speculation_norm, frontend_norm, backend_bound_norm, core_bound, memory_bound_norm), ...],
### }
def leer_datos_juntos(archivo, eventosP=0, eventosE=0):

    data = {}  # app_name -> list of tuples
    
    try:
        with open(archivo, 'r') as f:
            lineas = f.readlines()
    except Exception as e:
        print(f"Error abriendo {archivo}: {e}")
        return {}
    
    # Procesar cada línea del archivo
    for linea in lineas:
        linea = linea.strip()
        if not linea or linea.startswith("name"):
            continue
        
        # Parse: name;cores;instructions;cycles;...
        datos = linea.split(";")
        
        # Agrupar en conjuntos de 23 + plus
        for i in range(0, len(datos), 2 + eventosP + eventosE):
            if i + 2 + eventosP + eventosE - 1 < len(datos):
                app_name = datos[i]
                core = int(datos[i+1])

                ## Leer eventos P
                if core < 16:
                    instr = float(datos[i+2])
                    cycles = float(datos[i+3])
                    if cycles == 0:
                        cycles = 1
                    
                    retiring = float(datos[i+5])
                    bad_speculation = float(datos[i+6])
                    frontend = float(datos[i+7])
                    backend_bound = float(datos[i+8])
                    memory_bound = float(datos[i+9])

                    slots = cycles * ANCHO_ISSUE_P
                    slots = slots if slots != 0 else 1

                    retiring_norm = retiring / slots
                    bad_speculation_norm = bad_speculation / slots
                    frontend_norm = frontend / slots
                    backend_bound_norm = backend_bound / slots
                    memory_bound_norm = memory_bound / slots
                    core_bound = backend_bound_norm - memory_bound_norm
               
                else:
                    salto = eventosP + 2
                    instr = float(datos[i+salto])
                    cycles = float(datos[i+1+salto])
                    if cycles == 0:
                        cycles = 1
                    
                    retiring = float(datos[i+2+salto])
                    bad_speculation = float(datos[i+3+salto])
                    frontend = float(datos[i+4+salto])
                    backend_bound = float(datos[i+5+salto])

                    slots = cycles * ANCHO_ISSUE_E
                    slots = slots if slots != 0 else 1

                    retiring_norm = retiring / slots
                    bad_speculation_norm = bad_speculation / slots
                    frontend_norm = frontend / slots
                    backend_bound_norm = backend_bound / slots

                    memory_bound_norm = 0
                    core_bound = 0

                if app_name in data:
                    data[app_name].append((core, instr, cycles, retiring_norm, bad_speculation_norm, frontend_norm, backend_bound_norm, core_bound, memory_bound_norm))
                else:
                    data[app_name] = [(core, instr, cycles, retiring_norm, bad_speculation_norm, frontend_norm, backend_bound_norm, core_bound, memory_bound_norm)]
    return data
