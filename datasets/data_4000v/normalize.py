import csv

dataset = csv.DictReader(open("env_vital_signals.csv", "r"))
signals = [dict(row) for row in dataset]

for s in signals:
    del s["pSist"]
    del s["pDiast"]

    s["qPA"] = float(s["qPA"])
    s["pulso"] = float(s["pulso"])
    s["fResp"] = float(s["fResp"])
    s["grav"] = float(s["grav"])

s = signals[0]

maximums = {"qPA": 0, "pulso": 0, "fResp": 0}
minimums = {"qPA": s["qPA"], "pulso": s["pulso"], "fResp": s["fResp"]}

for s in signals:
    for k, v in s.items():
        if k in ("id", "label", "grav"):
            continue
        if v > maximums[k]:
            maximums[k] = v
        if v < minimums[k]:
            minimums[k] = v

print(maximums, minimums)

for s in signals:
    for k, v in s.items():
        if k in ("id", "label", "grav"):
            continue
        s[k] = (v - minimums[k]) / (maximums[k] - minimums[k])
    s["grav"] = s["grav"] / 100

with open("normalized_env_vital_signals.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=signals[0].keys())
    writer.writeheader()
    writer.writerows(signals)
