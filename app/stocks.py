import json
import pandas as pd
import yfinance as yf

# get major movements of a stock between start and end date, with a threshold for percentage change
def get_major_movements(ticker, start_date, end_date, threshold=2.0):
    ticker = ticker.strip().upper() # make it caps
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True, multi_level_index = False, progress=False)
    if data is None or data.empty:
        raise ValueError(f"No data found for ticker {ticker} between {start_date} and {end_date}.")

    # calculate percentage change and filter for major movements
    data['Percentage Change'] = data['Close'].pct_change() * 100 # calculate percentage change
    major_movements = data[abs(data['Percentage Change']) >= threshold] # filter for major movements

    # print(data)
    # print(major_movements)
    results = []
    # print(results)

    # iterate through the major movements and format the results
    for data, row in major_movements.iterrows():
        changes = float(row['Percentage Change'])

        results.append({
            "date": pd.Timestamp(str(data)).strftime("%m/%d/%Y"),
            "open": round(float(row['Open']),2),
            "close": round(float(row['Close']),2),
            "high": round(float(row['High']),2),
            "low": round(float(row['Low']),2),
            "volume": int(row['Volume']),
            "percentage_change": round(changes, 2),
        })

    return results

#Testing the function for nvidia from 22 april to 22 may 2026 with treshold of 2%
if __name__ == "__main__":
    movements = get_major_movements(
        ticker="NVDA",
        start_date="2026-04-22",
        end_date="2026-05-22",
        threshold=2.0,
    )

    print(json.dumps(movements, indent=2))
