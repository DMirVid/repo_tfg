from config import CPUS, QUANTUM_SIZE

# Events used by the policy
EVENTS = ["instructions, cycles, retiring, bad_speculation, frontend_bound, backend_bound"]


def asignacion_core(nucleo):
    

def schedule(processes):
    # WARNING: ONLY WORKS WITH 4 PROCESSES
    
    # inatrucciones por quantum
    ips = []
    for proc in processes:
        ips.append(proc.event_counts['instructions'] / QUANTUM_SIZE)

    # Sort processes by memory load count (lowest to highest)
    sorted_procs = sorted(processes, key=lambda proc: proc.event_counts[''])

    # Set affinity balancing load number
    sorted_procs[0].set_affinity({CPUS[0][0]})  # Lowest #loads in core 0, context 0
    sorted_procs[3].set_affinity({CPUS[0][1]})  # Highest #loads in core 0, context 1
    sorted_procs[1].set_affinity({CPUS[1][0]})  # Next-to-lowest in core 1, context 0
    sorted_procs[2].set_affinity({CPUS[1][1]})  # Next-to-highest in core 1, context 1