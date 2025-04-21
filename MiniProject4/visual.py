import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('parallel_sort_results.csv')

plt.figure(figsize=(8, 6))
for location, group in df.groupby('location'):
    plt.plot(
        group['array_size'],
        group['time'],
        marker='o',
        linestyle='-',
        label=location
    )

plt.xlabel('Array size')
plt.ylabel('Time (seconds)')
plt.title('Parallel Sort Performance')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
