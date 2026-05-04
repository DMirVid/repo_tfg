#!/usr/bin/env python3

from importlib import import_module
import os
import signal
import subprocess
import sys

from config import QUANTUM_SIZE, MAX_QUANTUMS, SPEC, MANAGER_CPUS, TARGET_INSTRUCTIONS
import sudo
import frequency
import perf
import process
import results
import timing
import yaml
import argparse

# Global flag for Ctrl+C interruption
interrupted = False

def signal_handler(sig, frame):
    """Mark interruption flag when Ctrl+C is pressed."""
    global interrupted
    interrupted = True
    print(f"\n# Ctrl+C detected. Will stop after current quantum...")

def build_args(tasks):
    args = []
    for name, cores in tasks:
        # Handle different input types for cores
        if isinstance(cores, str):
            # Parse comma-separated string: "2,4" -> [2, 4]
            cores = [int(c.strip()) for c in cores.split(",") if c.strip()]
        elif isinstance(cores, int):
            cores = [cores]
        elif isinstance(cores, (list, tuple)):
            cores = list(cores)

        if name not in SPEC:
            print(f"Error: Application {name} is not in the SPEC list.")
            sys.exit(1)
        args.append({
            "name": name,
            "cores": set(cores)
        })
    return args

### MAIN ###

if __name__ == "__main__":
    try:
        
        # Set CPU affinity for the manager process
        if MANAGER_CPUS is not None:
            os.sched_setaffinity(0, MANAGER_CPUS)

        parser = argparse.ArgumentParser()

        parser.add_argument("--config", help="YAML config file")
        parser.add_argument("policy", nargs="?", help="Policy name")
        parser.add_argument("tasks", nargs="*", help="Tasks as name:core1,core2")

        args_ns = parser.parse_args()

        # ./manager.py --config <file>
        if args_ns.config:
            with open(args_ns.config) as f:
                config = yaml.safe_load(f)

            policy_name = config["policy"]
            iteration = config["rep"]
            max_instructions = config["max_instr"]
            tasks = [
                (t["app"], t["cpu"])
                for t in config.get("tasks", [])
            ]
            cmd_cfg = config.get("cmd", {})
            QUANTUM_SIZE = cmd_cfg.get("ti"*1000, QUANTUM_SIZE) # seconds to milliseconds
            MAX_QUANTUMS = cmd_cfg.get("mi", MAX_QUANTUMS)

            EVENTS = []
            raw_events = cmd_cfg.get("event", [])
            if raw_events and isinstance(raw_events, list) and len(raw_events) == 1:
                EVENTS = [e.strip() for e in raw_events[0].split(",")]
            
            if not max_instructions:
                TARGET_INSTRUCTIONS.clear()
            
        # ./manager.py policy <name:core_1,...,core_n> ...
        elif args_ns.policy and args_ns.tasks:
            policy_name = args_ns.policy
            iteration = 0
            tasks = []
            for arg in args_ns.tasks:
                name, core_set = arg.split(":")
                # Remover paréntesis si existen para varios núcleos
                core_set = core_set.strip().strip("()")
                cores = [int(c.strip()) for c in core_set.split(",") if c.strip()]
                tasks.append((name, cores))
        else:
            parser.error("Invalid arguments, Usage: --help")

        args = build_args(tasks)
        policy = import_module("policies." + policy_name)
        policy.EVENTS = EVENTS
       
        # Validate sudo credentials for the run
        sudo.validate_sudo()

        # Validate that perf supports the required events for this policy
        perf.validate_perf(policy)

        # Initialize results output
        results.init_results(args, iteration)

        # Adjust system frequency based on configuration
        frequency.adjust()

        # Prepare working directories for each process
        process.prepare_workdirs(args)

        # Launch monitored processes
        process.launch_processes(args)

        # Launch perf
        perf.launch_perf()

        # Set up Ctrl+C handler for graceful interruption
        signal.signal(signal.SIGINT, signal_handler)

        # Iterate over quantums
        quantum = 0
        while True:
            # Read event lines from perf for this quantum
            perf.read_perf_output()
            
            # Start timing manager processing
            timing.start_processing()
            
            # Process event lines and update counts
            perf.obtain_event_counts()

            # Policy schedules (execute immediately after reading events)
            timing.start_policy()
            policy.schedule(process.processes)
            timing.end_policy()

            # Write quantum information to results files (before restart resets counts)
            results.update_results(quantum)

            # Update cores_prev for next quantum
            process.update_cores_prev()

            # Check if any process reached target instructions (only in target-driven mode)
            if MAX_QUANTUMS is None:
                process.mark_target_completion()

            quantum += 1
            
            # Check termination conditions
            if interrupted:
                print(f"\n# Experiment interrupted by user. Stopping at quantum {quantum}.")
                break
            if MAX_QUANTUMS is None:
                # Target-driven mode: stop when all targets reached
                if process.target_reached_count == len(process.processes):
                    print(f"\n# All processes have reached target. Stopping at quantum {quantum}.")
                    break
            elif quantum == MAX_QUANTUMS:
                # Time-driven mode: stop at quantum limit
                print(f"\n# Reached maximum number of quantums ({MAX_QUANTUMS}). Stopping.")
                break
            
            if process.finished_processes() == len(process.processes):
                break
            # Check for terminated processes and restart if needed
#            if process.restart_finished_processes():
#               perf.launch_perf()
            
            # Mark end of total processing time (before next readline blocks)
            timing.end_processing()
        
        # Ensure final processing time is recorded
        timing.end_processing()
        
        # Report timing statistics
        timing.report_timing()

        # Clean up working directories to save disk space
        process.cleanup_workdirs()
        
        # Finalize target totals for time-driven mode
        if MAX_QUANTUMS is not None:
            process.finalize_target_totals()
        
        # Print summary statistics
        results.generate_summary(quantum)
        
    finally:
        # Ensure files are closed even if there's an error or Ctrl+C
        results.close_results()
