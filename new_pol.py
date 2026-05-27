## Política de asignación de cores basado en IPC
## Daniel Mirón

from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, TOPDOWNL1, RETIRING,  BACKEND_BOUND, RETIRING_E, BACKEND_BOUND_E
import results
import random
import math

# Events used by the policy
EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, TOPDOWNL1, RETIRING, BACKEND_BOUND, RETIRING_E, BACKEND_BOUND_E]
P_CORES = set(range(0, 15, 2))
E_CORES = set(range(24, 31, 2))
NEXT_EVAL = 10  # 10 quantums = 2 seconds


def obtener_calcular_eventos(processes, ipc):

    for i, proc in enumerate(processes):

        es_P = True
        for c in proc.cores:
            if c > 16:
                es_P = False
                break

        if es_P:
            try:
                ipc[i] = proc.event_counts[INSTRUCTION_COUNT_P] / proc.event_counts[CYCLE_COUNT_P]
                slots = proc.event_counts[TOPDOWNL1] 
                retiring = proc.event_counts[RETIRING] / slots
                backend = proc.event_counts[BACKEND_BOUND] / slots
                ipc[i] *= backend * retiring

            except ZeroDivisionError:
                ipc[i] = 0.25

        else:
            try:
                ipc[i] = proc.event_counts[INSTRUCTION_COUNT_E] / proc.event_counts[CYCLE_COUNT_E] * (3.0/2.2)
                slots = proc.event_counts[CYCLE_COUNT_E] * 5
                retiring = proc.event_counts[RETIRING_E] / slots
                backend = proc.event_counts[BACKEND_BOUND_E] / slots
                ipc[i] *= backend * retiring

            except ZeroDivisionError:
                ipc[i] = 0.25

### Eejcuta durante 1 quantum todas las aplicaciones en los núcleos P
def medir_en_P(processes, quantum):
    global simple
    simple = True
    results.log_message(f"[Policy pol_FPint]:{quantum}:Movement to P cores")
    for i, proc in enumerate(processes):
        results.log_message(f"[Policy pol_FPint]:{quantum}:{proc.name}:{proc.cores}:{i*2}")
        proc.set_affinity({i*2})


def asignar_cores(sorted_procs, quantum, simple):

    cambio = []
    for i in range(len(sorted_procs)):
        core = {}
        if i < 4:
            core = {i * 2}
        else:
            core = {16+i*2}

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


## Solo funciona si al inico las aplicaciones estan dividas entre los cores P y E
def schedule(processes, quantum=0):

    if quantum % NEXT_EVAL == 0:
        ipc = [0] * len(processes)
        obtener_calcular_eventos(processes, ipc)

        # Ordenar procesos por IPC
        sorted_procs = sorted(processes, key=lambda x: ipc[processes.index(x)], reverse=True)
        random_index = math.floor(random.random() * len(processes))
        sorted_procs.append(sorted_procs.pop(random_index))
        asignar_cores(sorted_procs, quantum, simple=False)
