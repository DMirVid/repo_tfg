# Ejecutara durante dos cuantums las aplicaciones en los núcleos P y E y obtendrá el speedup y las clasificaremos al rpincipio 
# y luego cada cierto intervalo ir rotando entre los núcleos.
# se clasificaran según el speedup en 

from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, TOPDOWNL1, RETIRING, BAD_SPECULATION, FRONTEND_BOUND, BACKEND_BOUND, MEMORY_BOUND, CORE_BOUND, RETIRING_E, BAD_SPECULATION, FRONTEND_BOUND, BACKEND_BOUND_E
import results



EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, TOPDOWNL1, RETIRING, BAD_SPECULATION, FRONTEND_BOUND, BACKEND_BOUND, MEMORY_BOUND, CORE_BOUND, RETIRING_E, BAD_SPECULATION, FRONTEND_BOUND, BACKEND_BOUND_E]
P_CORES = set(range(0, 15, 2))
E_CORES = set(range(24, 31, 2))
NEXT_EVAL = 10  # 10 quantums = 2 seconds
MEDIO = 1.21    # Speedup <= 1.21: MEDIO
ALTO = 1.31     # Speedup > 1.21 y <= 1.31: ALTO
MUY_ALTO = 1.36 # Speedup > 1.31: MUY_ALTO

primera_ejecucion = True

# Datos guardados entre ejecuciones
# Usar índice del proceso como clave para manejar aplicaciones repetidas
app_data_p = {}  # {proc_index: {'name': ..., 'ipc': valor, ...}}
app_data_e = {}  # {proc_index: {'name': ..., 'ipc': valor, ...}}
speedups = {}    # {proc_index: speedup_value}
clasificaciones = {}  # {proc_index: 'MEDIO'|'ALTO'|'MUY_ALTO'}

def clasificacion(processes, quantum):
    """Clasifica las aplicaciones según su speedup después de la primera ejecución."""
    global clasificaciones
    
    # Calcular speedup para cada proceso usando índice como clave
    for proc_idx, proc in enumerate(processes):
        if proc_idx in speedups:
            speedup = speedups[proc_idx]
            
            if speedup > MUY_ALTO:
                nivel = 'MUY_ALTO'
            elif speedup > ALTO:
                nivel = 'ALTO'
            else:
                nivel = 'MEDIO'

            clasificaciones[proc_idx] = nivel
            results.log_message(f"[Classification]:{quantum}:{proc_idx}:{proc.name}:speedup={speedup:.3f}:level={nivel}")

def calcular_datos(processes):
    """Calcula IPC y datos de rendimiento para P y E, y guarda speedup.
    Usa índice del proceso como clave para manejar aplicaciones repetidas."""
    global app_data_p, app_data_e, speedups
    
    for proc_idx, proc in enumerate(processes):
        es_P = True
        for c in proc.cores:
            if c > 16:
                es_P = False
                break

        try:
            if es_P:
                # Calcular métricas para P-cores
                ipc_p = proc.event_counts[INSTRUCTION_COUNT_P] / proc.event_counts[CYCLE_COUNT_P]
                slots = proc.event_counts[TOPDOWNL1] 
                retiring = proc.event_counts[RETIRING] / slots if slots > 0 else 0
                backend = proc.event_counts[BACKEND_BOUND] / slots if slots > 0 else 0
                memory = proc.event_counts[MEMORY_BOUND] / slots if slots > 0 else 0
                core = backend - memory
                
                # Guardar datos de P (usar índice como clave)
                app_data_p[proc_idx] = {
                    'name': proc.name,
                    'ipc': ipc_p,
                    'retiring': retiring,
                    'backend': backend,
                    'memory': memory,
                    'core': core,
                }
                results.log_message(f"[P-core metrics]:{proc_idx}:{proc.name}:ipc={ipc_p:.3f}")

            else:
                # Calcular métricas para E-cores
                ipc_e = proc.event_counts[INSTRUCTION_COUNT_E] / proc.event_counts[CYCLE_COUNT_E] * (3.0/2.2)
                slots = proc.event_counts[CYCLE_COUNT_E] * 5
                retiring = proc.event_counts[RETIRING_E] / slots if slots > 0 else 0
                backend = proc.event_counts[BACKEND_BOUND_E] / slots if slots > 0 else 0
                
                # Guardar datos de E (usar índice como clave)
                app_data_e[proc_idx] = {
                    'name': proc.name,
                    'ipc': ipc_e,
                    'retiring': retiring,
                    'backend': backend,
                }
                results.log_message(f"[E-core metrics]:{proc_idx}:{proc.name}:ipc={ipc_e:.3f}")
                
                # Calcular speedup: comparar eficiencia en P vs E
                if proc_idx in app_data_p and proc_idx in app_data_e:
                    speedup = app_data_p[proc_idx]['ipc'] / app_data_e[proc_idx]['ipc'] if app_data_e[proc_idx]['ipc'] > 0 else 1
                    speedups[proc_idx] = speedup
                    results.log_message(f"[Speedup calculated]:{proc_idx}:{proc.name}:speedup={speedup:.3f}")

        except (ZeroDivisionError, KeyError):
            results.log_message(f"[Error calculating metrics for {proc_idx}:{proc.name}]")


# Función para asignar apps a cores
# La primera mitad a los núcleos P y la segunda mitad a los núcleos E
# simple = True: asignación directa sin comprobaciones
# simple = False: si la app ya está en el núcleo correcto o en el mismo grupo, no hacer nada. Si no, hacer un intercambio entre una app de la primera mitad y otra de la segunda mitad.
def asignar_cores(sorted_procs, quantum, simple):
    cambio = []
    for i in range(len(sorted_procs)):
        core = {}
        if i < 4:
            core = {i * 2}
        else:
            core = {8+i*2}

        if simple:
            results.log_message(f"[Policy core movement]:{quantum}:{sorted_procs[i].name}:{sorted_procs[i].cores}:{core}")
            sorted_procs[i].set_affinity(core)
        else:
            # Si ya esta en el núcleo correcto o mismo grupo, no hacer nada
            a_P    = core.issubset(P_CORES)
            esta_P = sorted_procs[i].cores.issubset(P_CORES)
            a_E    = core.issubset(E_CORES)
            esta_E = sorted_procs[i].cores.issubset(E_CORES)
            if sorted_procs[i].cores == core or (a_P and esta_P) or (a_E and esta_E):
                pass
            else:
                ## Lista vacia o pertence al mismo grupo de nucleos
                if not cambio or i<4:
                    cambio.append(i)
                else:
                    pos_cambio = cambio.pop()
                    guarda = sorted_procs[pos_cambio].cores
                    results.log_message(f"[Policy pol_FPint]:{quantum}:{sorted_procs[pos_cambio].name}:{sorted_procs[pos_cambio].cores}:{sorted_procs[i].cores}")
                    results.log_message(f"[Policy pol_FPint]:{quantum}:{sorted_procs[i].name}:{sorted_procs[i].cores}:{guarda}")
                    sorted_procs[pos_cambio].set_affinity(sorted_procs[i].cores)
                    sorted_procs[i].set_affinity(guarda)


def schedule_by_classification(processes, quantum):
    """
    Asigna cores según la clasificación de speedup:
    1. MUY_ALTO: directamente en P-cores
    2. ALTO y MEDIO: ordenados por memory_bound (mayor primero) rellenando huecos en P-cores
    3. Resto: en E-cores
    """
    # Separar procesos por clasificación
    muy_altos = []
    altos_medios = []
    sin_clasificar = []
    
    for proc_idx, proc in enumerate(processes):
        if proc_idx not in clasificaciones:
            sin_clasificar.append((proc_idx, proc))
        elif clasificaciones[proc_idx] == 'MUY_ALTO':
            muy_altos.append((proc_idx, proc))
        else:  # ALTO o MEDIO
            altos_medios.append((proc_idx, proc))
    
    # Ordenar ALTO y MEDIO por memory_bound descendente
    # Usar memory_bound de P-core si está disponible, si no usar 0
    def get_memory_bound(proc_idx):
        if proc_idx in app_data_p:
            return app_data_p[proc_idx].get('memory', 0)
        return 0
    
    altos_medios.sort(key=lambda x: get_memory_bound(x[0]), reverse=True)
    
    # Calcular capacidad de cores
    # Asumiendo 4 slots en P-cores y 4 slots en E-cores basado en asignar_cores
    max_p_slots = 4
    max_e_slots = 4
    
    # Asignar MUY_ALTO a P-cores
    p_assignments = []  # [(proc_idx, proc, core_id)]
    for proc_idx, proc in muy_altos:
        if len(p_assignments) < max_p_slots:
            core_id = len(p_assignments) * 2  # 0, 2, 4, 6
            p_assignments.append((proc_idx, proc, {core_id}))
            results.log_message(f"[Schedule MUY_ALTO]:{quantum}:{proc_idx}:{proc.name}:core={core_id}")
    
    # Rellenar huecos en P-cores con ALTO y MEDIO ordenados por memory_bound
    remaining_alto_medio = []
    for proc_idx, proc in altos_medios:
        if len(p_assignments) < max_p_slots:
            core_id = len(p_assignments) * 2
            p_assignments.append((proc_idx, proc, {core_id}))
            results.log_message(f"[Schedule P-core higher memory]:{quantum}:{proc_idx}:{proc.name}:memory_bound={get_memory_bound(proc_idx):.3f}:core={core_id}")
        else:
            remaining_alto_medio.append((proc_idx, proc))
    
    # Asignar resto a E-cores
    e_assignments = []  # [(proc_idx, proc, core_id)]
    for i, (proc_idx, proc) in enumerate(remaining_alto_medio + sin_clasificar):
        if i < max_e_slots:
            core_id = 16 + i * 2  # 16, 18, 20, 22
            e_assignments.append((proc_idx, proc, {core_id}))
            results.log_message(f"[Schedule E-core]:{quantum}:{proc_idx}:{proc.name}:core={core_id}")
    
    # Aplicar asignaciones
    for proc_idx, proc, core in p_assignments:
        results.log_message(f"[Policy core movement]:{quantum}:{proc_idx}:{proc.name}:{proc.cores}:{core}")
        proc.set_affinity(core)
    
    for proc_idx, proc, core in e_assignments:
        results.log_message(f"[Policy core movement]:{quantum}:{proc_idx}:{proc.name}:{proc.cores}:{core}")
        proc.set_affinity(core)


def medir_P(processes, quantum):
    eval = quantum % NEXT_EVAL
    if eval == 0:
        # Primera fase: medir en P-cores
        asignar_cores(processes, quantum, simple=True)
    elif eval == 1:
        # Segunda fase: calcular datos de P-cores
        calcular_datos(processes)
        # Rotar a E-cores para la siguiente medición
        asignar_cores(processes[::-1], quantum, simple=True)
    elif eval == 2:
        # Tercera fase: calcular datos de E-cores y calcular speedup
        calcular_datos(processes)
        # Clasificar basándose en speedup (primera ejecución completada)
        clasificacion(processes, quantum)
        return False
    return True



def schedule(processes, quantum=0):
    """
    Scheduler principal que ejecuta dos fases:
    
    FASE 1 (primera_ejecucion=True): Medición y clasificación (quantums 0-2)
      - quantum 0: Asignar todas las apps a P-cores
      - quantum 1: Calcular métricas de P-cores, rotar a E-cores
      - quantum 2: Calcular métricas de E-cores, calcular speedup y clasificar
      - Resultado: speedups y clasificaciones almacenadas globalmente
    
    FASE 2 (primera_ejecucion=False): Scheduling optimizado basado en clasificación
      - Cada NEXT_EVAL quantums: reasignar cores según clasificación
      - MUY_ALTO: directamente en P-cores
      - ALTO/MEDIO: ordenados por memory_bound, rellenando huecos en P-cores
      - Resto: en E-cores
    """
    global primera_ejecucion

    if primera_ejecucion:
        primera_ejecucion = medir_P(processes, quantum)
    else:
        # FASE 2: Scheduling basado en clasificación
        # Reasignar cada NEXT_EVAL quantums
        if quantum % NEXT_EVAL == 0:
            schedule_by_classification(processes, quantum)
        else:
            # Calcular datos en otros quantums para actualizar métricas
            calcular_datos(processes)


