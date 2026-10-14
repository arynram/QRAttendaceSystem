"""
scheduler.py
Real-time CPU Scheduling Engine for Attendance Request Processing.
Executes FCFS or Round Robin algorithm whenever a student marks attendance.
"""

import random                                             # for realistic verification burst times


def schedule_request(algo, roll_number, queue_history, quantum=2):
    arrival_t = len(queue_history) * 2                   # simulated relative arrival timestamp (ms)
    burst_t = random.randint(3, 7)                        # token check + csv disk write time (ms)

    if algo == "FCFS":                                    # First-Come First-Served algorithm
        if not queue_history:                             # if first process in queue
            start_t = arrival_t                           # starts immediately
            waiting_t = 0                                 # zero waiting time
        else:                                             # subsequent process in queue
            prev = queue_history[-1]                      # last processed request
            start_t = max(arrival_t, prev["completion"])  # wait until previous finishes (non-preemptive)
            waiting_t = max(0, start_t - arrival_t)       # queue delay

        completion_t = start_t + burst_t                  # completion time
        turnaround_t = completion_t - arrival_t           # turnaround time = CT - AT

    else:                                                 # Round Robin algorithm
        q = max(1, int(quantum))                          # time quantum slice in ms
        if not queue_history:                             # if first process in queue
            start_t = arrival_t                           # starts immediately
            waiting_t = 0                                 # zero waiting time
        else:                                             # round robin time-sliced execution
            prev = queue_history[-1]                      # previous process
            start_t = max(arrival_t, prev["completion"])  # dispatch time
            slices = (burst_t + q - 1) // q               # number of quantum passes required
            waiting_t = max(0, (start_t - arrival_t) + (slices - 1)) # fair interleaved wait

        completion_t = start_t + burst_t                  # completion time
        turnaround_t = completion_t - arrival_t           # turnaround time = CT - AT

    colors = ["#A594F9", "#CCF631", "#1E1F24", "#FF8A65", "#4DD0E1", "#81C784"] # pastel slice colors
    color = colors[len(queue_history) % len(colors)]      # pick color for gantt slice

    return {                                              # return process metrics
        "roll": roll_number,                              # student roll number
        "arrival": arrival_t,                             # arrival time (ms)
        "burst": burst_t,                                 # burst time (ms)
        "start": start_t,                                 # execution start time (ms)
        "completion": completion_t,                       # execution completion time (ms)
        "wt": waiting_t,                                  # waiting time (ms)
        "tat": turnaround_t,                              # turnaround time (ms)
        "algo": algo,                                     # algorithm name
        "color": color                                    # gantt chart color
    }                                                     # end return
