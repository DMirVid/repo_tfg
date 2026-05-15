from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E
import results

# Events used by the policy
EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E]
P_CORES = set(range(0, 16, 2))
E_CORES = set(range(16, 32, 2))

# Procesos con mayot IPC se mueven a los P cores
def schedule(processes):
    
    ipc = [0] * len(processes)
    for i, proc in enumerate(processes):

        es_P = True
        for c in proc.cores:
            if c > 16:
                es_P = False
                break

        if es_P:
            ipc[i] = proc.event_counts[INSTRUCTION_COUNT_P] / proc.event_counts[CYCLE_COUNT_P]
        else:
            ipc[i] = proc.event_counts[INSTRUCTION_COUNT_E] / proc.event_counts[CYCLE_COUNT_E]

    sorted_procs = sorted(processes, key=lambda proc: ipc[processes.index(proc)], reverse=True)

    for i in range(len(sorted_procs)):
        core = {}
        if i < 4:
            core = {i * 2}
        else:
            core = {16+i*2}

        # Si ya esta en el núcleo correcto, no hacer nada
        if sorted_procs[i].cores in P_CORES and core in P_CORES or sorted_procs[i].cores in E_CORES and core in E_CORES:
            continue
        else:
            sorted_procs[i].set_affinity(core)
            results.log_message(f"{sorted_procs[i].name} is in core: \t{core}")
