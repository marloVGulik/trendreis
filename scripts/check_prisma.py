import json, re, math

h = open("site/ordenen.html", encoding="utf-8").read()
sc = [json.loads(s) for s in re.findall(r"data-scene='(\{.*?)'>", h) if '"prism"' in s][0]
P, pr = sc["params"], sc["prism"]
C = sc["center"]
names = ["voor", "rechts", "achter", "links", "boven"]

def rotv(ax, a):
    return [ax[0] * math.cos(a) + ax[2] * math.sin(a), ax[1], -ax[0] * math.sin(a) + ax[2] * math.cos(a)]

def rot(p, a):
    x, y, z = p[0] - C[0], p[1] - C[1], p[2] - C[2]
    return [x * math.cos(a) + z * math.sin(a) + C[0], y + C[1], -x * math.sin(a) + z * math.cos(a) + C[2]]

for deg in (0, 45, 90, 135, 180, 225, 270, 315):
    a = math.radians(deg)
    vis = []
    for i, f in enumerate(pr["faces"]):
        lp = [[pr["c"][0] + p[0] * pr["hx"], pr["c"][1] + p[1] * pr["height"], pr["c"][2] + p[2] * pr["hz"]] for p in f["pts"]]
        rp = [rot(p, a) for p in lp]
        fc = [sum(p[0] for p in rp) / 4, sum(p[1] for p in rp) / 4, sum(p[2] for p in rp) / 4]
        nr = rotv(f["n"], a)
        if nr[0] * (P["camL"][0] - fc[0]) + nr[1] * (P["camL"][1] - fc[1]) + nr[2] * (P["camL"][2] - fc[2]) <= 0:
            continue
        U = (round(rotv(f["u"], a)[0], 3), round(-rotv(f["u"], a)[1], 3))
        V = (round(rotv(f["v"], a)[0], 3), round(-rotv(f["v"], a)[1], 3))
        ok = "ok" if U[0] > 0.01 and V[1] > 0.01 else "ONLEESBAAR"
        vis.append(f"{names[i]:<6} U={U} V={V} {ok}")
    print(f"{deg:>3}°: " + (" | ".join(vis) if vis else "geen"))

print("\nverhouding vlakken:", round(pr["hx"] / pr["hz"], 2), ": 1 (kubus = 1.0)")
print("vlakbreedtes:", round(2 * pr["hx"] * P["F"] * P["S"] / 2.1), "px (voor/achter),",
      round(2 * pr["hz"] * P["F"] * P["S"] / 2.1), "px (zijkanten), hoogte", round(pr["height"] * P["F"] * P["S"] / 2.1), "px")
