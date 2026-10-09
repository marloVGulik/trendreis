import json, re
h = open("site/analyseren.html", encoding="utf-8").read()
sc = [json.loads(s) for s in re.findall(r"data-scene='(\{.*?)'>", h) if '"prism"' in s][0]
P, pr = sc["params"], sc["prism"]

def proj(p, cam):
    rz = p[2] - cam[2]
    return (P["CX"] + P["F"] * (p[0] - cam[0]) / rz * P["S"], P["CY"] - P["F"] * (p[1] - cam[1]) / rz * P["S"])

xs, ys = [], []
for f in pr["faces"]:
    for p in f["pts"]:
        q = proj([pr["c"][0] + p[0] * pr["half"], pr["c"][1] + p[1] * pr["height"], pr["c"][2] + p[2] * pr["half"]], P["camL"])
        xs.append(q[0]); ys.append(q[1])
print("x", round(min(xs), 1), "->", round(max(xs), 1), "| y", round(min(ys), 1), "->", round(max(ys), 1), "| viewBox 0-600 / 0-300")
print("vlakbreedte op scherm:", round(2 * pr["half"] * P["F"] * P["S"] / 2.1), "px | vlakhoogte:", round(pr["height"] * P["F"] * P["S"] / 2.1), "px")
print("vlakken:", len(pr["faces"]))
print("tekst per vlak:", [ [l["t"] for l in f["lines"]] for f in pr["faces"] ])
