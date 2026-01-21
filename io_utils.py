# core/io_utils.py

import os
import json
import pandas as pd

def save_payload(path, workflow):
    with open(path, "w") as f:
        json.dump(workflow, f, indent=2)

def load_payload(path):
    with open(path, "r") as f:
        return json.load(f)

def save_log_entry(log_file, entry):
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    else:
        df = pd.DataFrame([entry])
    df.to_csv(log_file, index=False)

def load_log(log_file):
    if os.path.exists(log_file):
        return pd.read_csv(log_file)
    else:
        return pd.DataFrame()

def update_log_score(log_file, timestamp, score):
    df = pd.read_csv(log_file)
    if timestamp not in df["timestamp"].values:
        return False
    df.loc[df["timestamp"] == timestamp, "auto_score"] = score
    df.to_csv(log_file, index=False)
    return True
