## Política de asignación de cores basado en IPC
## Daniel Mirón

from config import CPUS, QUANTUM_SIZE, INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E
import results

# Events used by the policy
EVENTS = [INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E, "cpu_core/fp_arith_inst_retired.vector/", "cpu_core/fp_arith_inst_retired.scalar/"]

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

                
            except ZeroDivisionError:
                ipc[i] = 1
        else:
            try:

                ipc[i] = proc.event_counts[INSTRUCTION_COUNT_E] / proc.event_counts[CYCLE_COUNT_E] * (3.0/2.2)
            except ZeroDivisionError:
                ipc[i] = 1

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
                    results.log_message(f"[Policy pol_FPint]:{quantum}:{sorted_procs[pos_cambio].name}:{sorted_procs[pos_cambio].cores}:{sorted_procs[i].cores}")
                    results.log_message(f"[Policy pol_FPint]:{quantum}:{sorted_procs[i].name}:{sorted_procs[i].cores}:{guarda}")
                    sorted_procs[pos_cambio].set_affinity(sorted_procs[i].cores)
                    sorted_procs[i].set_affinity(guarda)

def schedule(processes, quantum=0):
    pass