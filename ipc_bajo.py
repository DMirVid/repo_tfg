## Política de asignación de cores basado en IPC
## Daniel Mirón

from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E
import results

# Events used by the policy
EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E]
P_CORES = set(range(0, 7, 2))
E_CORES = set(range(24, 31, 2))
ipc_history=[0] * 8

# Procesos con mayot IPC se mueven a los P cores
def schedule(processes, quantum=0):
    ### FUNCIIONA PARA EJECUCIoNES QUE NO TERMINAN
    

    for i, proc in enumerate(processes):

        es_P = True
        for c in proc.cores:
            if c > 16:
                es_P = False
                break

        try:
            if es_P:
                ipc = proc.event_counts[INSTRUCTION_COUNT_P] / proc.event_counts[CYCLE_COUNT_P]
            else:
                ipc= proc.event_counts[INSTRUCTION_COUNT_E] / proc.event_counts[CYCLE_COUNT_E]

        except ZeroDivisionError:
            ipc_history[i] = 1

        ipc_change_significant = False
        if quantum > 0:
            percent_change = abs((ipc - ipc_history[i]) / ipc_history[i]) * 100
            ipc_change_significant = percent_change > 10
        
            # Actualizar IPC
            if ipc_change_significant and ipc > ipc_history[i]:
                ipc_history[i] = ipc
        # Iniciar el IPC
        else:
            ipc_history[i] = ipc

    sorted_procs = sorted(processes, key=lambda proc: ipc_history[processes.index(proc)])

    cambio = []

    for i in range(len(sorted_procs)):
        core = {}
        if i < 4:
            core = {i * 2}
        else:
            core = {16+i*2}

        ## No nos complicamos la vida en la primera ejecucion
        if quantum == 0:
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
                    results.log_message(f"[Policy core movement]:{quantum}:{sorted_procs[pos_cambio].name}:{sorted_procs[pos_cambio].cores}:{sorted_procs[i].cores}")
                    results.log_message(f"[Policy core movement]:{quantum}:{sorted_procs[i].name}:{sorted_procs[i].cores}:{guarda}")
                    sorted_procs[pos_cambio].set_affinity(sorted_procs[i].cores)
                    sorted_procs[i].set_affinity(guarda)

