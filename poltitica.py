

from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, TOPDOWNL1, BACKEND_BOUND, MEMORY_BOUND, DIVIDER, STORE_BOUND, CLK, EXE_3, L3_STALLS
import results

## Eventos necesarios para la politica
# - Intrucciones y ciclos de ambos núcleos
# - Backend Bound y Memory bound para obtener el core
# - Divider 


EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, TOPDOWNL1, BACKEND_BOUND, MEMORY_BOUND, DIVIDER, STORE_BOUND, CLK, EXE_3, L3_STALLS]
P_CORES = set(range(0, 7, 2))
E_CORES = set(range(24, 31, 2))
NEXT_EVAL = 10
MEDIO = 1.21
ALTO = 1.31
MUY_ALTO = 1.36

app_data_p = {}
app_data_e = {}
speedups = {}
fase = 'warmup'
inicio_q = NEXT_EVAL

def calcular_datos(processes):
    global app_data_p, app_data_e, speedups
    for proc_idx, proc in enumerate(processes):
        es_P = any(c <= 16 for c in proc.cores)
        try:
            if es_P:
                ipc_p = proc.event_counts[INSTRUCTION_COUNT_P] / proc.event_counts[CYCLE_COUNT_P]
                clocks = proc.event_counts[CLK]
                slots = proc.event_counts[TOPDOWNL1]
                memory = proc.event_counts[MEMORY_BOUND] / slots if slots > 0 else 0
                backend = proc.event_counts[BACKEND_BOUND] / slots if slots > 0 else 0
                core = backend - memory
                divider = proc.event_counts[DIVIDER] / clocks if clocks > 0 else 0
                dram = proc.event_counts[L3_STALLS] / clocks if clocks > 0 else 0
                store = proc.event_counts[STORE_BOUND] / clocks if clocks > 0 else 0
                ports3 = proc.event_counts[EXE_3] / clocks if clocks > 0 else 0

                app_data_p[proc_idx] = {'name': proc.name, 'ipc': ipc_p, 'memory': memory, 'backend': backend, 'divider': divider, 'dram': dram, 'store': store, 'core': core, 'exe_3': ports3}
            else:
                ipc_e = proc.event_counts[INSTRUCTION_COUNT_E] / proc.event_counts[CYCLE_COUNT_E]
                app_data_e[proc_idx] = {'name': proc.name, 'ipc': ipc_e}

            if proc_idx in app_data_p and proc_idx in app_data_e:
                speedup = app_data_p[proc_idx]['ipc'] / app_data_e[proc_idx]['ipc'] if app_data_e[proc_idx]['ipc'] > 0 else 1
                speedups[proc_idx] = speedup
        except (ZeroDivisionError, KeyError):
            pass


def asignar_cores(sorted_procs, quantum, simple):
    cambio = []
    for i in range(len(sorted_procs)):
        if i < 4:
            core = {i * 2}
        else:
            core = {8 + i*2}
        if simple:
            sorted_procs[i].set_affinity(core)
        else:
            a_P = core.issubset(P_CORES)
            esta_P = sorted_procs[i].cores.issubset(P_CORES)
            a_E = core.issubset(E_CORES)
            esta_E = sorted_procs[i].cores.issubset(E_CORES)
            if sorted_procs[i].cores == core or (a_P and esta_P) or (a_E and esta_E):
                pass
            else:
                if not cambio or i<4:
                    cambio.append(i)
                else:
                    pos_cambio = cambio.pop()
                    guarda = sorted_procs[pos_cambio].cores
                    results.log_message(f"[Policy core movement]:{quantum}:{sorted_procs[pos_cambio].name}:{sorted_procs[pos_cambio].cores}:{sorted_procs[i].cores}")
                    results.log_message(f"[Policy core movement]:{quantum}:{sorted_procs[i].name}:{sorted_procs[i].cores}:{guarda}")
                    sorted_procs[pos_cambio].set_affinity(sorted_procs[i].cores)
                    sorted_procs[i].set_affinity(guarda)


## Devuelve una lista con los procesos ordenados para asignar a los núcleos 
def clasificar(processes, quantum):
    results.log_message(f'[Politica] Clasificación de apps en {quantum}')

    p_core = []
    e_core = []

    for proc_id, proc in enumerate(processes):
        if app_data_p[proc_id]['core'] > app_data_p[proc_id]['memory']:
            if app_data_p[proc_id]['ports3'] > 0.2 and app_data_p[proc_id]['divider'] < 0.2: # Podría cambiarse
                e_core.append(proc)
            elif app_data_p[proc_id]['divider'] > 0.2:
                p_core.append(proc)
        else:
            if app_data_p[proc_id]['dram'] > 0.2:
                e_core.append(proc)
            elif app_data_p[proc_id]['store'] > 0.2:
                p_core.append(proc)

    # Resolución de conflictos




def schedule(processes, quantum=0):
    global fase

    if fase == 'wamrup':
        if quantum >= inicio_q:
            fase = 'medir'
    
    elif fase == 'medir':
        if inicio_q > NEXT_EVAL:
            fase = 'schedule'
            calcular_datos(processes)
            clasificar()

        else:
            fase = 'wamrup'
            calcular_datos(processes)
            asignar_cores(processes[::-1], quantum, simple=True)
            inicio_q += NEXT_EVAL

    elif fase == 'schedule':

