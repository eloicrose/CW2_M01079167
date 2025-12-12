# ---------------------------------------------------------------
# First Come First Served (FCFS) CPU Scheduling Algorithm
# This program calculates and displays for each process:
# - Waiting Time (WT)
# - Turn Around Time (TAT)
# It also calculates the:
# - Average Waiting Time
# - Average Turn Around Time
# FCFS executes processes strictly in the order they arrive,
# without preemption or priority.
# ---------------------------------------------------------------

def fcfs_scheduling(processes):
    """
    FCFS Scheduling Function
    Input: processes -> list of tuples in the form (process_number, burst_time)
    Example: [(1, 5), (2, 8), (3, 12)]

    WHY: FCFS assigns the CPU to the first process that arrives and continues
    until completion before starting the next process.
    """

    waiting_times = []       # Stores Waiting Time (time a process waits before execution)
    turnaround_times = []    # Stores Turn Around Time (WT + Burst Time)

    waiting_times.append(0)  # The first process always starts immediately → WT = 0

    # Compute Waiting Time for each process
    for i in range(1, len(processes)):
        # Waiting Time = previous process’s waiting time + previous process’s burst time
        previous_burst_sum = waiting_times[i-1] + processes[i-1][1]
        waiting_times.append(previous_burst_sum)

    # Compute Turn Around Time for each process
    for i in range(len(processes)):
        tat = processes[i][1] + waiting_times[i]  # TAT = BT + WT
        turnaround_times.append(tat)

    # Compute averages for class requirements
    avg_waiting = sum(waiting_times) / len(processes)
    avg_turnaround = sum(turnaround_times) / len(processes)

    # Display results in a formatted table
    print("\n--- FCFS CPU Scheduling ---\n")
    print("Process\tBurst Time\tWaiting Time\tTurnaround Time")
    print("----------------------------------------------------------")
    for i in range(len(processes)):
        p, bt = processes[i]
        print(f"P{p}\t\t{bt}\t\t{waiting_times[i]}\t\t{turnaround_times[i]}")

    print("\nAverage Waiting Time:", round(avg_waiting, 2))
    print("Average Turnaround Time:", round(avg_turnaround, 2))
    print("\n----------------------------------------------------------\n")



# DEFAULT INPUT


default_processes = [
    (1, 5),
    (2, 8),
    (3, 12)
]

# Run FCFS using default values to satisfy assignment requirements
fcfs_scheduling(default_processes)



# USER INPUT FUNCTION

def user_input_fcfs():
    print("\n--- FCFS Scheduling (User Input Mode) ---")
    n = int(input("Enter number of processes: "))  # Number of processes to schedule

    processes = []
    for i in range(1, n+1):
        # Burst Time entered by the user → allows flexible testing
        bt = int(input(f"Enter Burst Time for Process P{i}: "))
        processes.append((i, bt))

    fcfs_scheduling(processes)  # Run the scheduling with user-provided data



user_input_fcfs()
