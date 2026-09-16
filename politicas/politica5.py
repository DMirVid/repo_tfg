## Copia de la politica final, por alguna razón.
## Planteaba usar algunos de los eventos medidos en el núcleo E.
## Daniel Mirón. 

from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, TOPDOWNL1, BACKEND_BOUND, MEMORY_BOUND, DIVIDER, STORE_BOUND, CLOCK, EXE_3, L1_STALLS, L2_STALLS, L3_STALLS, BACKEND_BOUND_E, LOAD_STALLS, LOAD_L2_HIT, LOAD_LLC_HIT, LOAD_DRAM_HIT
import results


EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, TOPDOWNL1, BACKEND_BOUND, MEMORY_BOUND, DIVIDER, STORE_BOUND, CLOCK, EXE_3, L1_STALLS, L2_STALLS, L3_STALLS, BACKEND_BOUND_E, LOAD_STALLS, LOAD_L2_HIT, LOAD_LLC_HIT, LOAD_DRAM_HIT]
P_CORES = set(range(0, 7, 2))
E_CORES = set(range(24, 31, 2))
NEXT_EVAL = 5 # 1 segundo
MEDIO = 1.21
ALTO = 1.31
MUY_ALTO = 1.36

app_data_p = {}
app_data_e = {}
speedups = {}
fase = 'warmup'
inicio_q = NEXT_EVAL
sorted_procs = []
rrPE = 0
old_q = 0

def calcular_datos(processes):
    global app_data_p, app_data_e, speedups
    for proc_idx, proc in enumerate(processes):
        es_P = any(c < 16 for c in proc.cores)
        try:
            if es_P:
                ipc_p = proc.event_counts[INSTRUCTION_COUNT_P] / proc.event_counts[CYCLE_COUNT_P]
                clocks = proc.event_counts[CLOCK]
                slots = proc.event_counts[TOPDOWNL1]
                memory = proc.event_counts[MEMORY_BOUND] / slots if slots > 0 else 0
                backend = proc.event_counts[BACKEND_BOUND] / slots if slots > 0 else 0
                core = backend - memory
                divider = proc.event_counts[DIVIDER] / clocks if clocks > 0 else 0
                l2_bound = (proc.event_counts[L1_STALLS] - proc.event_counts[L2_STALLS]) / clocks if clocks > 0 else 0
                dram = proc.event_counts[L3_STALLS] / clocks if clocks > 0 else 0
                store = proc.event_counts[STORE_BOUND] / clocks if clocks > 0 else 0
                ports3 = proc.event_counts[EXE_3] / clocks if clocks > 0 else 0

                app_data_p[proc_idx] = {'name': proc.name, 'ipc': ipc_p, 'memory': memory, 'backend': backend, 'divider': divider, 'dram': dram, 'store': store, 'core': core, 'exe_3': ports3, 'l2_bound': l2_bound}
            else:
                ipc_e = proc.event_counts[INSTRUCTION_COUNT_E] / proc.event_counts[CYCLE_COUNT_E]
                backend = proc.event_counts[BACKEND_BOUND_E] / (proc.event_counts[CYCLE_COUNT_E] * 5)
                loads = proc.event_counts[LOAD_STALLS]
                l2_bound = proc.event_counts[LOAD_L2_HIT] / loads
                l3_bound = proc.event_counts[LOAD_LLC_HIT] / loads
                dram_bound = proc.event_counts[LOAD_DRAM_HIT] / loads

                app_data_e[proc_idx] = {'name': proc.name, 'ipc': ipc_e, 'memory': loads, 'core': backend-loads, 'l2_bound': l2_bound, 'l3_bound': l3_bound, 'dram_bound': dram_bound}

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
            core = {16 + i*2}
        if simple:
            results.log_message(f"[Policy core movement]:{quantum}:{sorted_procs[i].name}:{sorted_procs[i].cores}:{core}")
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
    global app_data_p, app_data_e, speedups, rrPE
    results.log_message(f'[Politica] Clasificación de apps en {quantum}')

    p_core = []
    e_core = []

    for proc_id, proc in enumerate(processes):
        if app_data_p[proc_id]['core'] > app_data_p[proc_id]['memory']:
            if app_data_p[proc_id]['exe_3'] > 0.55 and app_data_p[proc_id]['divider'] < 0.2:
                p_core.append(proc)
                results.log_message(f"[Policy classification]:{quantum}:{proc.name}:P:PUERTOS:{app_data_p[proc_id]['exe_3']}")
            elif app_data_p[proc_id]['divider'] > 0.2:
                e_core.append(proc)
                results.log_message(f"[Policy classification]:{quantum}:{proc.name}:E:DIVIDER:{app_data_p[proc_id]['divider']}")
            else:
                if speedups[proc_id] > MUY_ALTO:
                    p_core.append(proc)
                    results.log_message(f"[Policy classification]:{quantum}:{proc.name}:P:SPEEDUP:CORE:{speedups[proc_id]}:{app_data_p[proc_id]['exe_3']}:{app_data_p[proc_id]['divider']}")
                else:
                    e_core.append(proc)
                    results.log_message(f"[Policy classification]:{quantum}:{proc.name}:E:SPEEDUP:CORE:{speedups[proc_id]}:{app_data_p[proc_id]['exe_3']}:{app_data_p[proc_id]['divider']}")
        else:
            if app_data_p[proc_id]['dram'] > 0.2 or app_data_p[proc_id]['store'] > 0.2:
                e_core.append(proc)
                results.log_message(f"[Policy classification]:{quantum}:{proc.name}:E:DRAM/STORE:{app_data_p[proc_id]['dram']}/{app_data_p[proc_id]['store']}")
            elif app_data_e[proc_id]['l2_bound'] > 0.08:
                p_core.append(proc)
                results.log_message(f"[Policy classification]:{quantum}:{proc.name}:P:L2_BOUND:{app_data_e[proc_id]['l2_bound']}")
            else:
                if speedups[proc_id] > MUY_ALTO:
                    p_core.append(proc)
                    results.log_message(f"[Policy classification]:{quantum}:{proc.name}:P:SPEEDUP:MEM:{speedups[proc_id]}:{app_data_p[proc_id]['dram']}/{app_data_p[proc_id]['store']}:{app_data_e[proc_id]['l2_bound']}")
                else:
                    e_core.append(proc)
                    results.log_message(f"[Policy classification]:{quantum}:{proc.name}:E:SPEEDUP:MEM:{speedups[proc_id]}:{app_data_p[proc_id]['dram']}/{app_data_p[proc_id]['store']}:{app_data_e[proc_id]['l2_bound']}")

    lista_cores = []
    # Resolución de conflictos
    if p_core and e_core:
        rrPE = len(p_core) - len(e_core)
        
        if rrPE > 0:
            p_core.sort(key=lambda p: speedups[processes.index(p)], reverse=True)

        elif rrPE < 0:
            e_core.sort(key=lambda p: speedups[processes.index(p)], reverse=True)

        lista_cores = p_core + e_core

    else:
        lista_cores = sorted(p_core + e_core, key=lambda p: speedups[processes.index(p)], reverse=True)

    return lista_cores


def remover(sorted_procs):
    if rrPE > 0:
        tmp = sorted_procs.pop(0)
        sorted_procs.insert(rrPE//2+3, tmp)
    elif rrPE < 0:
        tmp = sorted_procs.pop(rrPE//2+4)
        sorted_procs.append(tmp)

    return sorted_procs


def schedule(processes, quantum=0):
    global fase, inicio_q, sorted_procs, old_q

    if fase == 'warmup':
        results.log_message(f'[Politica] Warmup de apps en {quantum}')
        if quantum >= inicio_q:
            fase = 'medir'
    
    elif fase == 'medir':
        if inicio_q - old_q >= NEXT_EVAL * 2:
            results.log_message(f'[Politica] Medición 2 de apps en {quantum}')
            fase = 'schedule'
            calcular_datos(processes)
            sorted_procs = clasificar(processes, quantum)
            asignar_cores(sorted_procs, quantum, simple=False)

        else:
            results.log_message(f'[Politica] Medición 1 de apps en {quantum}')
            fase = 'warmup'
            calcular_datos(processes)
            asignar_cores(processes[::-1], quantum, simple=True)
            inicio_q += NEXT_EVAL

    elif fase == 'schedule':
        #results.log_message(f'[Politica] Schedule de apps en {quantum}')
        #asignar_cores([processes[i] for i in sorted_index], quantum, simple=False)
        if quantum % (NEXT_EVAL * 9) == 0:
            fase = 'warmup'
            inicio_q = quantum + NEXT_EVAL
            old_q = quantum
            asignar_cores(processes, quantum, simple=False)
