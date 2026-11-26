#!/usr/bin/env python3
"""Build qamchiq/route.json from OpenStreetMap (road geometry) and NASA SRTM (relief).

Usage:
  python3 build_route.py --osm osm.json --dem DIR --out ../route.json

  osm.json  Overpass answer (out geom) with the A373 ways, see OVERPASS_QUERY below.
  DIR       folder with SRTM 1" tiles: N40E070.hgt, N40E071.hgt, N40E072.hgt, N41E070.hgt, N41E071.hgt
            (free: https://s3.amazonaws.com/elevation-tiles-prod/skadi/N40/N40E071.hgt.gz)

The game uses two real 1:1 pieces of the road:
  A  — leaving Andijon to the west (flat Fergana valley),
  B  — the last climb to the Qamchiq (Kamchik) pass, ending at its highest point.
Between them the game shows a short "... km later" transition.
"""
import argparse, base64, heapq, json, math, os, struct
import numpy as np

OVERPASS_QUERY = """[out:json][timeout:180];
way["highway"~"^(trunk|primary|motorway|trunk_link)$"]["ref"~"373"](40.3,70.2,41.3,72.6);
out geom tags;"""

ANDIJON = (40.7829, 72.3442)       # city centre (lat, lon)
R_EARTH = 6371000.0

# ---------------------------------------------------------------- DEM
class DEM:
    def __init__(self, folder):
        self.folder = folder; self.tiles = {}
    def tile(self, la, lo):
        key = (la, lo)
        if key not in self.tiles:
            name = f"N{la:02d}E{lo:03d}.hgt"
            path = os.path.join(self.folder, name)
            if not os.path.exists(path):
                self.tiles[key] = None
            else:
                a = np.fromfile(path, dtype='>i2').reshape(3601, 3601).astype(np.float32)
                a[a < -1000] = np.nan
                self.tiles[key] = a
        return self.tiles[key]
    def h(self, lat, lon):
        la, lo = int(math.floor(lat)), int(math.floor(lon))
        t = self.tile(la, lo)
        if t is None: return float('nan')
        y = (la + 1 - lat) * 3600.0; x = (lon - lo) * 3600.0
        x0, y0 = int(x), int(y); fx, fy = x - x0, y - y0
        x1, y1 = min(x0 + 1, 3600), min(y0 + 1, 3600)
        v = (t[y0, x0] * (1 - fx) * (1 - fy) + t[y0, x1] * fx * (1 - fy) + t[y1, x0] * (1 - fx) * fy + t[y1, x1] * fx * fy)
        return float(v)

def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h))

# ---------------------------------------------------------------- graph
def build_graph(osm):
    adj = {}; coord = {}; tunnel_edge = set(); bridge_edge = set()
    for w in osm['elements']:
        if w.get('type') != 'way' or 'geometry' not in w: continue
        tags = w.get('tags', {})
        nodes = w['nodes']; geom = w['geometry']
        ow = tags.get('oneway', 'no'); hw = tags.get('highway', '')
        oneway = ow in ('yes', '1', 'true') or hw == 'motorway'
        rev = ow == '-1'
        for n, g in zip(nodes, geom): coord[n] = (g['lat'], g['lon'])
        for a, b in zip(nodes[:-1], nodes[1:]):
            d = hav(coord[a], coord[b])
            pairs = [(b, a)] if rev else ([(a, b)] if oneway else [(a, b), (b, a)])
            for u, v in pairs:
                adj.setdefault(u, []).append((v, d))
                if tags.get('tunnel') in ('yes', 'building_passage'): tunnel_edge.add((u, v))
                if tags.get('bridge') == 'yes': bridge_edge.add((u, v))
    return adj, coord, tunnel_edge, bridge_edge

def dijkstra(adj, src, dst):
    dist = {src: 0.0}; prev = {}; pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst: break
        if d > dist.get(u, 1e18): continue
        for v, w in adj.get(u, []):
            nd = d + w
            if nd < dist.get(v, 1e18): dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if dst not in dist: return None
    path = [dst]
    while path[-1] != src: path.append(prev[path[-1]])
    return path[::-1]

def nearest(coord, adj, p):
    return min((n for n in coord if n in adj), key=lambda n: hav(coord[n], p))

# ---------------------------------------------------------------- geometry helpers
def resample(latlon, flags, step):
    """latlon: list of (lat,lon); flags: per-edge (tunnel, bridge). Returns arrays every `step` m."""
    cum = [0.0]
    for a, b in zip(latlon[:-1], latlon[1:]): cum.append(cum[-1] + hav(a, b))
    total = cum[-1]; n = int(total // step) + 1
    out, fl = [], []; j = 0
    for i in range(n):
        s = i * step
        while j < len(cum) - 2 and cum[j + 1] < s: j += 1
        seg = max(cum[j + 1] - cum[j], 1e-6); f = (s - cum[j]) / seg
        a, b = latlon[j], latlon[j + 1]
        out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)); fl.append(flags[j])
    return out, fl, total

def smooth(arr, win):
    if win <= 1: return arr
    k = np.ones(win) / win; pad = win // 2
    a = np.pad(arr, (pad, win - 1 - pad), mode='edge')
    return np.convolve(a, k, mode='valid')

def b64(arr, dtype):
    return base64.b64encode(np.asarray(arr, dtype=dtype).tobytes()).decode()

def make_segment(name, pts, flags, dem, labels, step=2.0, margin=1400.0, cell=20.0):
    pts, flags, total = resample(pts, flags, step)
    lat0, lon0 = pts[0]
    kx = math.cos(math.radians(lat0)) * math.pi / 180 * R_EARTH; kz = math.pi / 180 * R_EARTH
    X = np.array([(p[1] - lon0) * kx for p in pts]); Z = np.array([-(p[0] - lat0) * kz for p in pts])
    # smooth the polyline (OSM nodes are polygonal) — ~16 m window keeps real hairpins
    X = smooth(X, 9); Z = smooth(Z, 9)
    H = np.array([dem.h(p[0], p[1]) for p in pts])
    H = np.where(np.isnan(H), np.nanmean(H), H)
    tun = np.array([f[0] for f in flags]); bri = np.array([f[1] for f in flags])
    # road elevation: DEM is noisy and sees mountain tops over tunnels / valleys under bridges
    Y = smooth(H, 41)
    for mask in (tun, bri):
        i = 0
        while i < len(mask):
            if mask[i]:
                j = i
                while j < len(mask) and mask[j]: j += 1
                a, b = max(i - 3, 0), min(j + 3, len(mask) - 1)
                Y[a:b + 1] = np.linspace(Y[a], Y[b], b - a + 1)
                i = j
            else: i += 1
    Y = smooth(Y, 61)
    # real highways stay under ~10 % grade: clip DEM noise (cuts, embankments) that the smoothing left
    g = 0.10 * step
    for _ in range(3):
        for i in range(1, len(Y)): Y[i] = min(max(Y[i], Y[i - 1] - g), Y[i - 1] + g)
        for i in range(len(Y) - 2, -1, -1): Y[i] = min(max(Y[i], Y[i + 1] - g), Y[i + 1] + g)
    base = float(Y[0])
    # DEM patch around the segment (world metres, y relative to base)
    x0, x1 = X.min() - margin, X.max() + margin; z0, z1 = Z.min() - margin, Z.max() + margin
    nx = int((x1 - x0) // cell) + 1; nz = int((z1 - z0) // cell) + 1
    grid = np.zeros((nz, nx), dtype=np.float32)
    for iz in range(nz):
        lat = lat0 - (z0 + iz * cell) / kz
        for ix in range(nx):
            lon = lon0 + (x0 + ix * cell) / kx
            grid[iz, ix] = dem.h(lat, lon)
    grid = np.where(np.isnan(grid), np.nanmean(grid), grid)
    tunnels = []
    i = 0
    while i < len(tun):
        if tun[i]:
            j = i
            while j < len(tun) and tun[j]: j += 1
            tunnels.append([round(i * step, 1), round(j * step, 1)]); i = j
        else: i += 1
    return {
        'name': name, 'step': step, 'n': len(pts), 'length': round(total, 1), 'base': round(base, 1),
        'lat0': lat0, 'lon0': lon0,
        'x': b64(X, '<f4'), 'z': b64(Z, '<f4'), 'y': b64(Y - base, '<f4'),
        'tunnels': tunnels, 'labels': labels,
        'dem': {'x0': x0, 'z0': z0, 'cell': cell, 'nx': nx, 'nz': nz, 'h': b64(np.clip(grid, 0, 65535), '<u2')},
        'alt_start': round(float(Y[0]), 0), 'alt_end': round(float(Y[-1]), 0),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--osm', required=True); ap.add_argument('--dem', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--lenA', type=float, default=5000); ap.add_argument('--lenB', type=float, default=14000)
    a = ap.parse_args()
    osm = json.load(open(a.osm)); dem = DEM(a.dem)
    adj, coord, tun_e, bri_e = build_graph(osm)
    # Pass = highest node of the A373 network west of 71.0E
    cand = [n for n in coord if n in adj and coord[n][1] < 71.0]
    top = max(cand, key=lambda n: dem.h(*coord[n]))
    src = nearest(coord, adj, ANDIJON)
    path = dijkstra(adj, src, top)
    if not path: raise SystemExit('no path Andijon → pass in this OSM extract')
    latlon = [coord[n] for n in path]
    flags = [((u, v) in tun_e, (u, v) in bri_e) for u, v in zip(path[:-1], path[1:])]
    cum = [0.0]
    for p, q in zip(latlon[:-1], latlon[1:]): cum.append(cum[-1] + hav(p, q))
    total = cum[-1]
    print(f'route Andijon → pass: {total/1000:.1f} km, pass at {coord[top]}, {dem.h(*coord[top]):.0f} m')
    def cut(s0, s1):
        i0 = next(i for i, c in enumerate(cum) if c >= s0); i1 = next((i for i, c in enumerate(cum) if c >= s1), len(cum) - 1)
        return latlon[i0:i1 + 1], flags[i0:i1], cum[i0], cum[i1]
    pA, fA, a0, a1 = cut(1500, 1500 + a.lenA)
    pB, fB, b0, b1 = cut(total - a.lenB, total)
    segA = make_segment('A', pA, fA, dem, [[0, 'ANDIJON']])
    segB = make_segment('B', pB, fB, dem, [[0, 'DOVON YO\'LI'], [round(b1 - b0 - 1, 0), 'QAMCHIQ DOVONI']])
    out = {'source': 'OpenStreetMap contributors (ODbL); NASA SRTM 1 arc-second',
           'real_total_km': round(total / 1000, 1),
           'real_a': [round(a0 / 1000, 2), round(a1 / 1000, 2)], 'real_b': [round(b0 / 1000, 2), round(b1 / 1000, 2)],
           'pass_alt': round(dem.h(*coord[top])), 'segments': [segA, segB]}
    json.dump(out, open(a.out, 'w'), separators=(',', ':'))
    print('wrote', a.out, os.path.getsize(a.out) // 1024, 'KB', {k: (s['length'], s['alt_start'], s['alt_end'], s['tunnels']) for k, s in zip('AB', out['segments'])})

if __name__ == '__main__':
    main()
