from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E

# Events used by the policy
EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E]

# Procesos con mayot IPC se mueven a los P cores
def schedule(processes):
    
    ipc = {}
    for proc in processes:
        ipc[proc] = 0
        if proc.cores < 16:
            ipc[proc] = proc.event_counts[INSTRUCTION_COUNT_P] / proc.event_counts[CYCLE_COUNT_P]
        else:
            ipc[proc] = proc.event_counts[INSTRUCTION_COUNT_E] / proc.event_counts[CYCLE_COUNT_E]

    sorted_procs = sorted(processes, key=lambda proc: ipc[proc])

    for i in range(len(sorted_procs)):
        if i < 4:
            sorted_procs[i].set_affinity({CPUS[i][0]}) 
        else:
            sorted_procs[i].set_affinity({CPUS[8+i*2][0]})
   