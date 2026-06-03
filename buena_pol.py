# Ejecutara durante dos cuantums las aplicaciones en los núcleos P y E y obtendrá el speedup y las clasificaremos al rpincipio 
# y luego cada cierto intervalo ir rotando entre los núcleos.
# se clasificaran según el speedup en 

from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, TOPDOWNL1, RETIRING, BAD_SPECULATION, FRONTEND_BOUND, BACKEND_BOUND, MEMORY_BOUND, RETIRING_E, BAD_SPECULATION_E, FRONTEND_BOUND_E, BACKEND_BOUND_E
import results

EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, TOPDOWNL1, RETIRING, BAD_SPECULATION, FRONTEND_BOUND, BACKEND_BOUND, MEMORY_BOUND, RETIRING_E, BAD_SPECULATION_E, FRONTEND_BOUND_E, BACKEND_BOUND_E]
P_CORES = set(range(0, 15, 2))
E_CORES = set(range(24, 31, 2))
NEXT_EVAL = 10
MEDIO = 1.21
ALTO = 1.31
MUY_ALTO = 1.36

phase = 'warmup'
quantum_inicio_medida = NEXT_EVAL
app_data_p = {}
app_data_e = {}
speedups = {}
clasificaciones = {}

def clasificacion(processes):
    global clasificaciones
    for proc_idx in speedups:
        if proc_idx not in clasificaciones:
            speedup = speedups[proc_idx]
            if speedup > MUY_ALTO:
                nivel = 'MUY_ALTO'
            elif speedup > ALTO:
                nivel = 'ALTO'
            else:
                nivel = 'MEDIO'
            clasificaciones[proc_idx] = nivel

def calcular_datos(processes):
    global app_data_p, app_data_e, speedups
    for proc_idx, proc in enumerate(processes):
        es_P = any(c <= 16 for c in proc.cores)
        try:
            if es_P:
                ipc_p = proc.event_counts[INSTRUCTION_COUNT_P] / proc.event_counts[CYCLE_COUNT_P]
                slots = proc.event_counts[TOPDOWNL1]
                retiring = proc.event_counts[RETIRING]
                bad_speculation = proc.event_counts[BAD_SPECULATION]
                memory = proc.event_counts[MEMORY_BOUND] / slots if slots > 0 else 0
                backend = proc.event_counts[BACKEND_BOUND] / slots if slots > 0 else 0
                app_data_p[proc_idx] = {'name': proc.name, 'ipc': ipc_p, 'memory': memory, 'backend': backend, 'retiring': retiring, 'bad_speculation': bad_speculation}
            else:
                ipc_e = proc.event_counts[INSTRUCTION_COUNT_E] / proc.event_counts[CYCLE_COUNT_E]
                retiring_e = proc.event_counts[RETIRING_E]
                bad_speculation_e = proc.event_counts[BAD_SPECULATION_E]
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


def schedule_by_classification(processes, quantum):
    # muy_altos = []
    # altos_medios = []
    # sin_clasificar = []

    # for proc_idx, proc in enumerate(processes):
    #     if proc_idx not in clasificaciones:
    #         sin_clasificar.append((proc_idx, proc))
    #     elif clasificaciones[proc_idx] == 'MUY_ALTO':
    #         muy_altos.append((proc_idx, proc))
    #     else:
    #         altos_medios.append((proc_idx, proc))
    
    # def get_memory_bound(proc_idx):
    #     return app_data_p.get(proc_idx, {}).get('memory', 0) if proc_idx in app_data_p else 0
    
    # altos_medios.sort(key=lambda x: get_memory_bound(x[0]), reverse=True)
    
    # p_assignments = []
    # for proc_idx, proc in muy_altos:
    #     if len(p_assignments) < 4:
    #         p_assignments.append((proc_idx, proc))
    
    # remaining_alto_medio = []
    # for proc_idx, proc in altos_medios:
    #     if len(p_assignments) < 4:
    #         p_assignments.append((proc_idx, proc))
    #     else:
    #         remaining_alto_medio.append((proc_idx, proc))
    
    # e_assignments = []
    # for i, (proc_idx, proc) in enumerate(remaining_alto_medio + sin_clasificar):
    #     if i < 4:
    #         e_assignments.append((proc_idx, proc))
    
    # sorted_procs = [proc for _, proc in p_assignments] + [proc for _, proc in e_assignments]
    sorted_procs = sorted(processes, key=lambda p: speedups.get(processes.index(p), 0), reverse=True)
    asignar_cores(sorted_procs, quantum, simple=False)


def schedule(processes, quantum=0):
    global phase
    
    if phase == 'warmup':
        if quantum >= quantum_inicio_medida:
            phase = 'measure'
            results.log_message(f"[Phase warmup->measure at quantum {quantum}]")
    
    if phase == 'measure':
        eval_offset = (quantum - quantum_inicio_medida) % NEXT_EVAL
        if eval_offset == 0:
            asignar_cores(processes, quantum, simple=True)
        elif eval_offset == 1:
            calcular_datos(processes)
            asignar_cores(processes[::-1], quantum, simple=True)
        elif eval_offset == 2:
            calcular_datos(processes)
            clasificacion(processes)
            phase = 'schedule'
            results.log_message(f"[Phase measure->schedule at quantum {quantum}]")
    
    elif phase == 'schedule':
        if quantum % NEXT_EVAL == 0:
            schedule_by_classification(processes, quantum)


