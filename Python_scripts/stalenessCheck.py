import requests
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Configurations
API_URL = "https://exs.redenvelope.dev/polygon/rate/USD-AUD/100"
DURATION_SECONDS = 86400  # For testing; change to 86400 for 24 hours
INTERVAL = 1  # seconds

# Column constants
LATENCY_COLUMN = "Latency (ms)"
TIMESTAMP_COLUMN = "Timestamp"

# Storage
latencies = []
timestamps = []
success_count = 0
fail_count = 0

end_time = time.time() + DURATION_SECONDS
print("Starting API monitoring...")

try:
    while time.time() < end_time:
        start_request_time = time.time()
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
            latency = data.get("latency")
            if latency is not None:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"Request error at {datetime.datetime.now()}: {e}")
            latency = None
            fail_count += 1

        current_time = datetime.datetime.now()
        timestamps.append(current_time)
        latencies.append(latency)

        print(f"{current_time}: Latency={latency} ms")

        elapsed = time.time() - start_request_time
        time.sleep(max(0, INTERVAL - elapsed))

except KeyboardInterrupt:
    print("Monitoring interrupted.")

# Create DataFrame
df = pd.DataFrame({
    TIMESTAMP_COLUMN: timestamps,
    LATENCY_COLUMN: latencies
})

# Save all data to CSV before filtering
df.to_csv("api_latency_full_log.csv", index=False)

# Remove rows with missing latency
df_clean = df.dropna()

if df_clean.empty:
    print("No successful latency data available for plotting.")
else:
    avg_latency = df_clean[LATENCY_COLUMN].mean()
    print(f"\n✅ Average Latency over {len(df_clean)} samples: {avg_latency:.2f} ms")

    # Ensure datetime type
    df_clean[TIMESTAMP_COLUMN] = pd.to_datetime(df_clean[TIMESTAMP_COLUMN])

    # --- Line Graph ---
    plt.figure(figsize=(14, 6))
    plt.plot(
        df_clean[TIMESTAMP_COLUMN],
        df_clean[LATENCY_COLUMN],
        marker='o',
        linestyle='-',
        markersize=4
    )
    plt.title("📈 API Latency Over Time", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Latency (ms)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.tight_layout()
    plt.savefig("latency_line_graph.png")
    plt.show()

    # --- Pie Chart: Request Success vs Failure ---
    labels = ['Successful Requests', 'Failed Requests']
    values = [success_count, fail_count]
    colors = ['#4CAF50', '#F44336']

    plt.figure(figsize=(6, 6))
    plt.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 12}
    )
    plt.title("📊 Request Success vs Failure", fontsize=14)
    plt.tight_layout()
    plt.savefig("latency_pie_chart.png")
    plt.show()

    # --- Pie Chart: Top 4 Staleness Contributors ---
    top_stale = df_clean.sort_values(by=LATENCY_COLUMN, ascending=False).head(4)
    overall_total = df_clean[LATENCY_COLUMN].sum()

    plt.figure(figsize=(7, 7))
    plt.pie(
        top_stale[LATENCY_COLUMN],
        labels=[t.strftime('%H:%M:%S') for t in top_stale[TIMESTAMP_COLUMN]],
        autopct='%1.1f%%',
        startangle=140,
        colors=plt.cm.viridis_r(range(4)),
        textprops={'fontsize': 12}
    )
    plt.title("🔥 Top 4 Stale Requests by Latency %", fontsize=14)
    plt.tight_layout()
    plt.savefig("top_4_staleness_pie_chart.png")
    plt.show()
