# YouTube Channel Network Analysis

This Python script analyzes a YouTube channel's commenters and identifies the **most common channels** they are subscribed to. Essentially, it creates a "channel network" based on public subscriptions of commenters.

---
![Graph](images/graph.png)
## What it does

- Fetches videos from a channel’s uploads playlist.
- Collects commenters who have **public subscriptions**.
- Aggregates the subscriptions of these commenters.
- Returns the **most common channels** among commenters.
- Outputs results as a **Pandas DataFrame**.
- takes the data and makes a visual graph network

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

to do next:
In a future version, a GUI will be added to the app and more extensive visualization options.
