## Política de asignación de cores basado en IPC
## Daniel Mirón

from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E
import results

# Events used by the policy
EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, "cpu_core/fp_arith_inst_retired.vector/", "cpu_core/fp_arith_inst_retired.scalar/"]

P_CORES = set(range(0, 7, 2))
E_CORES = set(range(24, 31, 2))
NEXT_EVAL = 10  # 10 quantums = 2 seconds
EVALUATING = False

## Listas para guardar valores anteriores
procesos_fp = []
procesos_int = []
last_int_in_P = []
last_fp_in_E = []

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


### Mide durante un quantum las prestaciones en los nucleos P
### Devuelve True si es momento de aplicar cambios 
def medir_en_P(processes, quantum, ipc, isFloatArray, EVALUATING):
    if quantum % NEXT_EVAL == 0:
        results.log_message(f"[Policy core movement]:{quantum}:Movement to P cores")
        for i, proc in enumerate(processes):
            results.log_message(f"[Policy core movement]:{quantum}:{proc.name}:{proc.cores}:{i*2}")
            proc.set_affinity(i*2)
        EVALUATING = True
        return False
    elif EVALUATING: 
        obtener_ipc_float(processes, ipc, isFloatArray)
        EVALUATING = False
        return True
    return False


def asignar_cores(sorted_procs, quantum):

    cambio = []
    for i in range(len(sorted_procs)):
        core = {}
        if i < 4:
            core = {i * 2}
        else:
            core = {16+i*2}
       
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

    

# Procesos con mayot IPC se mueven a los P cores
def schedule(processes, quantum=0):

    ipc = [0] * len(processes)
    isFloatArray = [False] * len(processes)

    ## Primera parte: designar quien es float o no
    if medir_en_P(processes, quantum, ipc, isFloatArray, EVALUATING):
   
        # obtener_ipc_float(processes, ipc, isFloatArray)
        move_P = []
        move_E = []
        for i in range(len(processes)):
            if isFloatArray[i]:
                procesos_fp.append(i)
            else:
                procesos_int.append(i)

        indice_a_E = quantum % len(procesos_fp)
        indice_a_P = quantum % len(procesos_int)

        pasar = False
        ## Mover de E a P las aplicaciones de FP
        if last_fp_in_E:
            move_P.append(last_fp_in_E.pop(0))
            move_E.append(indice_a_E) 
            last_fp_in_E.append(indice_a_E)
            pasar = True

        for i in procesos_fp:
            if i == indice_a_E and pasar:
                pass
            if len(move_P) < 4:                  
                move_P.append(i)
            else:
                move_E.append(i)
                last_fp_in_E.append(i)
    
        pasar = False

        if last_int_in_P:
            move_E.append(last_int_in_P.pop(0))
            move_P.append(indice_a_P)
            last_int_in_P.append(indice_a_P)
            pasar = True

        for i in procesos_int:
            if i == indice_a_P and pasar:
                pass
            if len(move_E) < 4:
                move_E.append(i)
            else:
                move_P.append(i)
                last_int_in_P.append(i)

        ## PArte final: Apartir de aqui ya se debe de saber la asignación final de los procesos
        sorted_procs = []
        for i in move_P:
            sorted_procs.append(processes[i])

        for i in move_E:
            sorted_procs.append(processes[i])
        
        asignar_cores(sorted_procs, quantum)


