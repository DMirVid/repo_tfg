## Política de asignación de cores basado en IPC
## Daniel Mirón

from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E
import results

# Events used by the policy
EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, "cpu_core/fp_arith_inst_retired.vector/", "cpu_core/fp_arith_inst_retired.scalar/"]

P_CORES = set(range(0, 15, 2))
E_CORES = set(range(24, 31, 2))
NEXT_EVAL = 10  # 10 quantums = 2 seconds
NUM_APPS = 8
simple = False
procesos_fp = []
procesos_int = []

### Comprueba para cada aplicaión si es INT o FLT
def obtener_ipc_float(processes, ipc, isFloatArray):

    for i, proc in enumerate(processes):

        es_P = True
        for c in proc.cores:
            if c > 16:
                es_P = False
                break

        if es_P:
            ipc[i] = proc.event_counts[INSTRUCTION_COUNT_P] / proc.event_counts[CYCLE_COUNT_P]

            vector = proc.event_counts["cpu_core/fp_arith_inst_retired.vector/"]
            scalar = proc.event_counts["cpu_core/fp_arith_inst_retired.scalar/"]
            isFloatArray[i] = (vector + scalar) / proc.event_counts[INSTRUCTION_COUNT_P] > 0.005
        else:
            ipc[i] = proc.event_counts[INSTRUCTION_COUNT_E] / proc.event_counts[CYCLE_COUNT_E] * (3.0/2.2)


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
            results.log_message(f"[Policy pol_FPint]:{quantum}:{sorted_procs[i].name}:{sorted_procs[i].cores}:{core}")
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
                    results.log_message(f"[Policy core movement]:{quantum}:{sorted_procs[pos_cambio].name}:{sorted_procs[pos_cambio].cores}:{sorted_procs[i].cores}")
                    results.log_message(f"[Policy core movement]:{quantum}:{sorted_procs[i].name}:{sorted_procs[i].cores}:{guarda}")
                    sorted_procs[pos_cambio].set_affinity(sorted_procs[i].cores)
                    sorted_procs[i].set_affinity(guarda)

# Ordena los procesos según la función dada en funcion del IPC o aplica round robin
def ordena(procesos, function, rr=False):
    if rr:
        return procesos.append(procesos.pop(0))
    else:
        return sorted(procesos, key=function)
    

# Procesos con mayot IPC se mueven a los P cores
def schedule(processes, quantum=0):
    global simple, procesos_fp, procesos_int
    
    ipc = [0] * len(processes)

    isFloatArray = [False] * len(processes)
    ipc = [0] * len(processes)

    ## Primera parte: designar quien es float o no
    if quantum % NEXT_EVAL == 0:
        medir_en_P(processes, quantum)
    else:
        obtener_ipc_float(processes, ipc, isFloatArray)

        procesos_fp = []
        procesos_int = []
        for i in range(len(processes)):
            if isFloatArray[i]:
                procesos_fp.append(i)
            else:
                procesos_int.append(i)

        move_P = []
        move_E = []

        ## Ordenamos los indices según 
        procesos_fp = ordena(procesos_fp, key=lambda index: ipc[index], rr=simple)
        procesos_int = ordena(procesos_int, key=lambda index: ipc[index], rr=simple)

        if len(procesos_fp) == len(procesos_int):
            move_P = procesos_fp[:3]
            move_E.append(procesos_fp[4])
            move_P.append(procesos_int[0])
            move_E.extend(procesos_int[1:])
        elif len(procesos_fp) > len(procesos_int):
            move_P = procesos_fp[:4]
            move_E.append(procesos_fp[4:8])
            move_E.extend(procesos_int)
        else:
            move_E = procesos_int[:4]
            move_P = procesos_fp
            move_P.extend(procesos_int[4:8])

        sorted_procs = []
        for i in move_P:
            sorted_procs.append(processes[i])

        for i in move_E:
            sorted_procs.append(processes[i])
        
        asignar_cores(sorted_procs, quantum, simple)
        simple = False



