import json, re, math

h = open("site/analyseren.html", encoding="utf-8").read()
sc = [json.loads(s) for s in re.findall(r"data-scene='(\{.*?)'>", h) if '"prism"' in s][0]
P, pr = sc["params"], sc["prism"]
C = sc["center"]

def rot(p, a):
    x, y, z = p[0] - C[0], p[1] - C[1], p[2] - C[2]
    return [x * math.cos(a) + z * math.sin(a) + C[0], y + C[1], -x * math.sin(a) + z * math.cos(a) + C[2]]

def proj(p, cam):
    rz = p[2] - cam[2]
    if rz <= 0.02:
        return None
    return (P["CX"] + P["F"] * (p[0] - cam[0]) / rz * P["S"], P["CY"] - P["F"] * (p[1] - cam[1]) / rz * P["S"])

names = ["voor", "rechts", "achter", "links", "boven"]
for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
    vis = []
    for i, f in enumerate(pr["faces"]):
        lp = [[pr["c"][0] + p[0] * pr["hx"], pr["c"][1] + p[1] * pr["height"], pr["c"][2] + p[2] * pr["hz"]] for p in f["pts"]]
        rp = [rot(p, a) for p in lp]
        fc = [sum(p[0] for p in rp) / 4, sum(p[1] for p in rp) / 4, sum(p[2] for p in rp) / 4]
        nr = [f["n"][0] * math.cos(a) + f["n"][2] * math.sin(a), f["n"][1], -f["n"][0] * math.sin(a) + f["n"][2] * math.cos(a)]
        d = nr[0] * (P["camL"][0] - fc[0]) + nr[1] * (P["camL"][1] - fc[1]) + nr[2] * (P["camL"][2] - fc[2])
        if d > 0:
            O = proj(fc, P["camL"])
            def basis(ax):
                r = [ax[0]*math.cos(a) + ax[2]*math.sin(a), ax[1], -ax[0]*math.sin(a) + ax[2]*math.cos(a)]
                q = proj([fc[0] + r[0], fc[1] + r[1], fc[2] + r[2]], P["camL"])
                dx, dy = q[0] - O[0], q[1] - O[1]
                m = math.sqrt(dx * dx + dy * dy) or 1
                return (dx / m, dy / m)
            U, V = basis(f["u"]), basis(f["v"])
            vis.append((names[i], round(U[0], 2), round(U[1], 2), round(V[0], 2), round(V[1], 2)))
    print(f"hoek {round(math.degrees(a))}°: zichtbaar = {[v[0] for v in vis]}")
    for v in vis:
        ok = "U rechts + V omlaag" if v[1] > 0.9 and v[4] > 0.9 else "FOUT"
        print(f"   {v[0]:<7} U=({v[1]},{v[2]}) V=({v[3]},{v[4]})  {ok}")

xs, ys = [], []
for f in pr["faces"]:
    for p in f["pts"]:
        q = proj([pr["c"][0] + p[0] * pr["hx"], pr["c"][1] + p[1] * pr["height"], pr["c"][2] + p[2] * pr["hz"]], P["camL"])
        xs.append(q[0]); ys.append(q[1])
print("\nx", round(min(xs), 1), "->", round(max(xs), 1), "| y", round(min(ys), 1), "->", round(max(ys), 1), "| viewBox 0-600 / 0-300")
print("voor/achter", round(2 * pr["hx"] * P["F"] * P["S"] / 2.1), "px breed | zijkanten", round(2 * pr["hz"] * P["F"] * P["S"] / 2.1), "px | hoogte", round(pr["height"] * P["F"] * P["S"] / 2.1), "px")
