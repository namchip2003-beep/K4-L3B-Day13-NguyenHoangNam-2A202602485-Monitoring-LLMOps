import json
import pandas as pd
import matplotlib.pyplot as plt

def main():
    records = []
    try:
        with open('data/logs.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    except FileNotFoundError:
        print("Không tìm thấy data/logs.jsonl. Hãy chạy load_test trước.")
        return

    if not records:
        print("File log trống.")
        return

    df = pd.DataFrame(records)
    if 'ts' not in df.columns:
        print("Không có cột 'ts' trong log.")
        return

    df['ts'] = pd.to_datetime(df['ts'])
    df.set_index('ts', inplace=True)

    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('K4-L3B Day 13 Dashboard', fontsize=16)

    df_res = df[df['event'] == 'response_sent'].copy()
    df_req = df[df['event'] == 'request_received'].copy()
    df_err = df[df['event'] == 'request_failed'].copy()

    # Panel 1: Latency
    ax = axes[0, 0]
    if not df_res.empty and 'latency_ms' in df_res.columns:
        # Group into 10-second intervals to have smoother/more points, or 1min
        lat = df_res[['latency_ms', 'ttft_ms']].resample('10s').quantile([0.5, 0.95, 0.99]).unstack()
        if not lat.empty:
            ax.plot(lat.index, lat[('latency_ms', 0.5)], label='P50', color='green')
            ax.plot(lat.index, lat[('latency_ms', 0.95)], label='P95', color='orange')
            ax.plot(lat.index, lat[('latency_ms', 0.99)], label='P99', color='red')
            if 'ttft_ms' in df_res.columns:
                ax.plot(lat.index, lat[('ttft_ms', 0.95)], label='TTFT P95', color='purple', linestyle='-.')
            ax.axhline(y=3000, color='r', linestyle='--', label='Threshold (3000)')
            ax.set_title('Latency (ms)')
            ax.legend()

    # Panel 2: Traffic
    ax = axes[0, 1]
    if not df_req.empty:
        traffic = df_req.resample('1min').size()
        ax.plot(traffic.index, traffic.values, marker='o', color='blue', label='Requests/min')
        ax.axhline(y=1, color='r', linestyle='--', label='Threshold (1)')
        ax.set_title('Traffic')
        ax.legend()

    # Panel 3: Errors
    ax = axes[1, 0]
    if not df_req.empty:
        req_counts = df_req.resample('1min').size()
        err_counts = df_err.resample('1min').size() if not df_err.empty else pd.Series(0, index=req_counts.index)
        err_counts = err_counts.reindex(req_counts.index, fill_value=0)
        err_rate = (err_counts / req_counts * 100).fillna(0)
        ax.plot(err_rate.index, err_rate.values, marker='o', color='red', label='Error Rate (%)')
        ax.axhline(y=2, color='r', linestyle='--', label='Threshold (2%)')
        ax.set_title('Error Rate')
        ax.set_ylim(-1, 10)
        ax.legend()

    # Panel 4: Cost
    ax = axes[1, 1]
    if not df_res.empty and 'cost_usd' in df_res.columns:
        cost = df_res['cost_usd'].resample('1min').sum()
        ax.bar(cost.index, cost.values, width=0.001, color='green', label='Cost/min')
        ax.set_title('Cost (USD)')
        ax.legend()

    # Panel 5: Tokens
    ax = axes[2, 0]
    if not df_res.empty and 'tokens_in' in df_res.columns:
        t_in = df_res['tokens_in'].resample('10s').sum()
        t_out = df_res['tokens_out'].resample('10s').sum()
        ax.plot(t_in.index, t_in.values, label='Tokens In', color='blue')
        ax.plot(t_out.index, t_out.values, label='Tokens Out', color='purple')
        ax.set_title('Tokens')
        ax.legend()

    # Panel 6: Quality
    ax = axes[2, 1]
    if not df_res.empty and 'quality_score' in df_res.columns:
        qual = df_res['quality_score'].resample('10s').mean()
        ax.plot(qual.index, qual.values, marker='x', label='Avg Quality', color='teal')
        ax.axhline(y=0.75, color='r', linestyle='--', label='Threshold (0.75)')
        ax.set_title('Quality Score')
        ax.set_ylim(0, 1.1)
        ax.legend()

    plt.tight_layout()
    plt.savefig('dashboard_evidence.png')
    print("Done")

if __name__ == '__main__':
    main()
