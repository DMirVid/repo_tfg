#!/usr/bin/env python3

import ctypes
from dataclasses import dataclass
import os
import signal
import subprocess
from utils import Utils

from config import SPEC, TARGET_INSTRUCTIONS, DEFAULT_TARGET_INSTRUCTIONS, INSTRUCTION_COUNT, CYCLE_COUNT
# Import heterogeneous events if they exist
try:
    from config import INSTRUCTION_COUNT_P, INSTRUCTION_COUNT_E, CYCLE_COUNT_P, CYCLE_COUNT_E
except ImportError:
    INSTRUCTION_COUNT_P = INSTRUCTION_COUNT_E = CYCLE_COUNT_P = CYCLE_COUNT_E = None
import perf
import results
import shutil
from pathlib import Path




# Process type
@dataclass
class Process:
    name: str
    cores: set
    cores_prev: set  # Cores where events of current quantum were collected
    work_dir: str  # Working directory for this process
    python_proc: subprocess.Popen
    event_counts: dict
    event_totals: dict
    target_totals: dict  # Event totals at target completion (None if target not reached)
    
    def set_affinity(self, cores):
        """Set CPU affinity for this process."""
        pid = self.python_proc.pid
        os.sched_setaffinity(pid, cores)
        self.cores = cores


# Global process tracking (exposed for other modules)
processes = None  # List indexed by process number [0,1,2,3]
pid_to_index = None  # Dict for fast PID->index mapping {pid: index}
target_reached_count = 0


def launch_benchmark(name, cores, work_dir):
    """Launch a SPEC benchmark process.
    
    Args:
        name: Name of the benchmark from SPEC dictionary
        cores: Set of CPU cores to assign to the process
        work_dir: Working directory path for this process
        
    Returns:
        subprocess.Popen object for the benchmark process
    """
    results.log_message(f"Launching {name} on cores {','.join(map(str, sorted(cores)))} in {work_dir}")
    
    # Get command from SPEC config (just the command, no path prefix needed)
    # command = SPEC[name]
    reader = Utils("applications.mako")

    data = reader.render_mako()
    command = reader.obtain_benchmark_field(data, name, "cmd")
    stdin = reader.obtain_benchmark_field(data,name,"stdin")
    if(stdin):
        command += " <" + stdin

    results.log_message(f"[CMD] {command}")

    wd = Path(work_dir)
    wd.mkdir(parents=True, exist_ok=True)

    def _pdeathsig():
        libc = ctypes.CDLL("libc.so.6")
        PR_SET_PDEATHSIG = 1
        libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM)

    
    proc = subprocess.Popen(
        f"exec {command}",
        shell=True,
        cwd=str(work_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=lambda: ctypes.CDLL("libc.so.6").prctl(1, signal.SIGTERM)
    )

    os.sched_setaffinity(proc.pid, cores)
    return proc


def prepare_workdirs(args):
    """Create working directories and copy SPEC benchmarks.
    
    Args:
        args: List of dicts with 'name' and 'cores' keys
    """
    reader = Utils("applications.mako")

    data = reader.render_mako()

    for index, arg in enumerate(args):
        skel_paths = reader.obtain_benchmark_skel(data, arg["name"], "skel")
        work_dir = results.run_dir / str(index)
        print(work_dir)
        results.log_message(f"Preparing working directory {index} for {arg['name']}")

        # Recreate work_dir
        if work_dir.exists():
            shutil.rmtree(work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)

        for src in skel_paths:
            src_path = Path(src)
            if not src_path.exists():
                raise RuntimeError(f"SPEC directory not found: {src_path}")

            dst = work_dir / src_path.name
            shutil.copytree(src_path, work_dir, dirs_exist_ok=True)


def launch_processes(args):
    """Launch all benchmark processes from argument list.
    
    Args:
        args: List of dicts with 'name' and 'cores' keys
    """
    global processes, pid_to_index, target_reached_count
    
    processes = []
    pid_to_index = {}
    target_reached_count = 0
    
    for index, arg in enumerate(args):
        work_dir = str(results.run_dir / str(index))
        proc = launch_benchmark(arg['name'], arg['cores'], work_dir)
        
        process_obj = Process(
            name=arg['name'],
            cores=arg['cores'],
            cores_prev=arg['cores'],
            work_dir=work_dir,
            python_proc=proc,
            event_counts=dict(),
            event_totals=dict(),
            target_totals=None
        )
        
        processes.append(process_obj)
        pid_to_index[proc.pid] = index


def update_cores_prev():
    """Update cores_prev to current cores for all processes.
    
    Should be called at the end of each quantum after results are written,
    to prepare for the next quantum's event collection.
    """
    for proc in processes:
        proc.cores_prev = proc.cores.copy()


def get_total_instructions(event_totals):
    """Get total instructions from event totals, handling heterogeneous systems.
    
    Args:
        event_totals: Dictionary of event totals
        
    Returns:
        int: Total instruction count
    """
    if INSTRUCTION_COUNT is None:
        # Heterogeneous system: sum P-core and E-core instructions
        return event_totals[INSTRUCTION_COUNT_P] + event_totals[INSTRUCTION_COUNT_E]
    else:
        # Homogeneous system: use single instruction count
        return event_totals[INSTRUCTION_COUNT]


def get_total_cycles(event_totals):
    """Get total cycles from event totals, handling heterogeneous systems.
    
    Args:
        event_totals: Dictionary of event totals
        
    Returns:
        int: Total cycle count
    """
    if CYCLE_COUNT is None:
        # Heterogeneous system: sum P-core and E-core cycles
        return event_totals[CYCLE_COUNT_P] + event_totals[CYCLE_COUNT_E]
    else:
        # Homogeneous system: use single cycle count
        return event_totals[CYCLE_COUNT]


def mark_target_completion():
    """Check if any processes have reached target instructions and mark target completion."""
    global processes, target_reached_count
    
    for proc in processes:
        if proc.target_totals is None:
            target = TARGET_INSTRUCTIONS.get(proc.name, DEFAULT_TARGET_INSTRUCTIONS)
            
            # Calculate total instructions for heterogeneous systems
            total_instructions = get_total_instructions(proc.event_totals)
            
            if target is not None and total_instructions >= target:
                pid = proc.python_proc.pid
                results.log_message(f"Process {pid} ({proc.name}) reached target instructions ({target:,}), marking target completion")
                proc.target_totals = proc.event_totals.copy()
                target_reached_count += 1


def restart_finished_processes():
    """Check if any processes have terminated naturally and restart them.
    
    Returns:
        bool: True if any process was restarted, False otherwise
    """
    global processes, pid_to_index
    
    any_restarted = False
    
    # Check and restart finished processes
    for index, proc in enumerate(processes):
        if proc.python_proc.poll() is not None:
            old_pid = proc.python_proc.pid
            results.log_message(f"Process {old_pid} ({proc.name}) finished naturally")
            
            # Launch new process with same name, cores, and working directory
            new_proc = launch_benchmark(proc.name, proc.cores, proc.work_dir)
            
            # Update PID mapping
            del pid_to_index[old_pid]
            pid_to_index[new_proc.pid] = index
            
            # Update process at same index
            processes[index] = Process(
                name=proc.name,
                cores=proc.cores,
                cores_prev=proc.cores_prev,
                work_dir=proc.work_dir,
                python_proc=new_proc,
                event_counts=dict(),
                event_totals=proc.event_totals,
                target_totals=proc.target_totals
            )
            
            any_restarted = True
    
    return any_restarted

def finished_processes():
    """Check if any processes have terminated naturally and restart them.
    
    Returns:
        bool: True if any process was restarted, False otherwise
    """
    global processes, pid_to_index
    
    finished = 0
    
    # Check and restart finished processes
    for index, proc in enumerate(processes):
        if proc.python_proc.poll() is not None:
            old_pid = proc.python_proc.pid
            results.log_message(f"Process {old_pid} ({proc.name}) finished naturally")
            finished +=1

    return finished
def finalize_target_totals():
    """Set target_totals to current event_totals for all processes (time-driven mode).
    
    Used when MAX_QUANTUMS is defined to generate summary data without
    having tracked target completion during execution.
    """
    global processes
    
    for proc in processes:
        if proc.target_totals is None:
            proc.target_totals = proc.event_totals.copy()


def cleanup_workdirs():
    """Remove working directories to save disk space.
    
    Should be called at the end of the experiment to clean up
    the copied SPEC benchmark directories.
    """
    results.log_message("Cleaning up working directories to save disk space")
    
    # Get the number of working directories from when they were created
    num_workdirs = len(processes)
    
    for index in range(num_workdirs):
        work_dir = results.run_dir / str(index)
        try:
            shutil.rmtree(work_dir)
            results.log_message(f"Removed working directory {index}")
        except Exception as e:
            results.log_message(f"Failed to remove working directory {index}: {e}")
