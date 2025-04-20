#!/usr/bin/env python3
import sys
import time
import os
import csv

from mpi4py import MPI
import numpy as np

def parallel_sample_sort(local_data, comm):
    rank = comm.Get_rank()
    size = comm.Get_size()

    # 1) Local sort
    local_data.sort()

    # 2) Sample P points
    indices = np.linspace(0, len(local_data) - 1, size, dtype=int)
    samples = local_data[indices]

    # 3) Gather all samples to root
    all_samples = None
    if rank == 0:
        all_samples = np.empty(size * size, dtype=local_data.dtype)
    comm.Gather(samples, all_samples, root=0)

    # 4) Root picks P‑1 pivots
    pivots = np.empty(size - 1, dtype=local_data.dtype)
    if rank == 0:
        all_samples.sort()
        pivots[:] = all_samples[size::size][: size - 1]
    comm.Bcast(pivots, root=0)

    # 5) Partition around pivots
    split_indices = np.searchsorted(local_data, pivots)
    buckets = np.split(local_data, split_indices)

    # 6) All‑to‑all exchange
    send_counts = np.array([b.size for b in buckets], dtype=int)
    recv_counts = np.empty(size, dtype=int)
    comm.Alltoall(send_counts, recv_counts)

    sendbuf = np.concatenate(buckets) if size > 1 else local_data
    send_displs = np.insert(np.cumsum(send_counts), 0, 0)[:-1]
    recvbuf = np.empty(recv_counts.sum(), dtype=local_data.dtype)
    recv_displs = np.insert(np.cumsum(recv_counts), 0, 0)[:-1]

    comm.Alltoallv(
        [sendbuf, send_counts, send_displs, MPI.INT64_T],
        [recvbuf, recv_counts, recv_displs, MPI.INT64_T]
    )

    # 7) Final local sort
    recvbuf.sort()
    return recvbuf

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # parse optional location tag
    if len(sys.argv) not in (1, 2):
        if rank == 0:
            print("Usage: python3 parallel_sort.py [location]")
        sys.exit(1)
    location = sys.argv[1] if len(sys.argv) == 2 else "unknown"

    # absolute path for clarity
    csv_file = os.path.abspath("parallel_sort_results.csv")

    if rank == 0:
        print(f"[rank 0] Working directory: {os.getcwd()}")
        print(f"[rank 0] CSV path: {csv_file}")

        # create header if needed
        if not os.path.isfile(csv_file):
            print(f"[rank 0] Creating new CSV file")
            with open(csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["array_size", "time", "location"])
        else:
            print(f"[rank 0] CSV already exists; will append rows")

    # make sure everyone waits for header setup
    comm.Barrier()

    SIZES = [10_000_000, 100_000_000, 1_000_000_000]

    for N in SIZES:
        # split N among ranks
        base = N // size
        extras = N % size
        local_n = base + (1 if rank < extras else 0)

        np.random.seed(42 + rank)
        local_data = np.random.randint(0, 2**63, size=local_n, dtype=np.int64)

        comm.Barrier()
        t0 = time.time()
        _ = parallel_sample_sort(local_data, comm)
        comm.Barrier()
        t1 = time.time()

        local_time = t1 - t0
        times = comm.gather(local_time, root=0)

        if rank == 0:
            max_time = max(times)
            print(f"[rank 0] Size={N:,} • procs={size} • time={max_time:.6f}s")
            print(f"[rank 0] Appending row: {N}, {max_time:.6f}, {location}")

            with open(csv_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([N, f"{max_time:.6f}", location])
                f.flush()


if __name__ == "__main__":
    main()
