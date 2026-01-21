# YouTube Channel Network Analysis

This Python script analyzes a YouTube channel's commenters and identifies the **most common channels** they are subscribed to. Essentially, it creates a "channel network" based on public subscriptions of commenters.

---

## What it does

- Fetches videos from a channel’s uploads playlist.
- Collects commenters who have **public subscriptions**.
- Aggregates the subscriptions of these commenters.
- Returns the **most common channels** among commenters.
- Outputs results as a **Pandas DataFrame**.

---

## Requirements

- Python 3.9+
- [Google API Python Client](https://pypi.org/project/google-api-python-client/)
- [Pandas](https://pypi.org/project/pandas/)
- A youtube api key you set in your inviroment via : 

 **Linux/macOS:**
```
export YT_API_KEY="YOUR_API_KEY_HERE"
```
**Windows (PowerShell)**
```
setx YT_API_KEY "YOUR_API_KEY_HERE"
```

Install dependencies via pip:

```bash
pip install -r requirements.txt

```

### Note

Currently, the script outputs the most common channels in a table (Pandas DataFrame).  
In a future version, a **graph/network visualization** will be added to show the relationships between channels.
