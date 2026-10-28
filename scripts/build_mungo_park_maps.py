#!/usr/bin/env python3
"""Render maps of Mungo Park's two Niger expeditions for the Water Music post.

Needs matplotlib and a directory with these Natural Earth GeoJSON files
(github.com/nvkelso/natural-earth-vector/tree/master/geojson):
ne_50m_land, ne_50m_lakes, ne_50m_admin_0_boundary_lines_land,
ne_10m_rivers_lake_centerlines.

Usage: python3 scripts/build_mungo_park_maps.py <natural-earth-dir>
"""

import heapq
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

OUT_DIR = Path(__file__).resolve().parent.parent / "content/blog/2026-10-28-water-music/images"

# Flexoki-inspired palette, matching themes/minimal/static/css/style.css
SEA = "#E4ECE9"
LAND = "#F2F0E5"
BORDER = "#B7B5AC"
RIVER = "#4385BE"
TEXT = "#100F0F"
TEXT_SECONDARY = "#6F6E69"
ROUTE_OUT = "#AF3029"
ROUTE_BACK = "#BC5215"

FONT = "Georgia"

# Approximate (lat, lon) of the places Park mentions. Several of the
# 18th-century settlements no longer exist, so these are best guesses.
PLACES = {
    "Kayee": (13.55, -15.25),
    "Pisania": (13.67, -14.90),
    "Medina": (13.75, -13.80),
    "Fatteconda": (14.35, -12.25),
    "Koniakary": (14.58, -10.89),
    "Kemmoo": (14.45, -9.60),
    "Jarra": (15.20, -8.70),
    "Benowm": (15.55, -7.60),
    "Ségou": (13.43, -6.26),
    "Silla": (13.86, -5.55),
    "Bamako": (12.64, -7.99),
    "Kamalia": (12.80, -9.30),
    "Badoo": (13.77, -13.67),
    "Bambouk": (12.90, -11.30),
    "Sansanding": (13.72, -6.00),
    "Timbuktu": (16.77, -3.00),
    "Gao": (16.27, -0.04),
    "Yauri": (10.88, 4.70),
    "Bussa": (10.22, 4.47),
}

COUNTRIES_FIRST = {
    "SENEGAL": (15.2, -15.3),
    "THE GAMBIA": (13.05, -16.2),
    "MAURITANIA": (17.4, -9.5),
    "MALI": (16.6, -5.2),
    "GUINEA": (10.6, -11.6),
    "BURKINA FASO": (11.9, -4.4),
}

COUNTRIES_SECOND = {
    "SENEGAL": (15.0, -15.2),
    "MAURITANIA": (19.5, -11.0),
    "MALI": (19.3, -4.0),
    "NIGER": (17.6, 4.0),
    "GUINEA": (10.0, -11.5),
    "BURKINA FASO": (12.6, -1.5),
    "NIGERIA": (8.6, 7.0),
    "ALGERIA": (23.5, 1.5),
}


def load(ne_dir, name):
    return json.loads((ne_dir / f"{name}.geojson").read_text())["features"]


def lines_of(geometry):
    if geometry["type"] == "LineString":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiLineString":
        return geometry["coordinates"]
    return []


def rings_of(geometry):
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"][0]]
    if geometry["type"] == "MultiPolygon":
        return [poly[0] for poly in geometry["coordinates"]]
    return []


def build_river_graph(rivers, name):
    """Adjacency map over all vertices of a named river."""
    graph = {}
    segments = []
    for feature in rivers:
        if feature["properties"].get("name") != name:
            continue
        for line in lines_of(feature["geometry"]):
            points = [(round(x, 5), round(y, 5)) for x, y in line]
            segments.append(points)
            for a, b in zip(points, points[1:]):
                dist = math.dist(a, b)
                graph.setdefault(a, []).append((b, dist))
                graph.setdefault(b, []).append((a, dist))
    # Natural Earth splits rivers at lakes and reservoirs; bridge those gaps
    for i, points in enumerate(segments):
        others = [p for j, seg in enumerate(segments) if j != i for p in seg]
        for end in (points[0], points[-1]):
            closest = min(others, key=lambda p: math.dist(p, end))
            dist = math.dist(closest, end)
            if dist < 0.5:
                graph[end].append((closest, dist))
                graph[closest].append((end, dist))
    return graph


def river_path(graph, start, end):
    """Shortest path along the river between the vertices nearest two places."""
    def nearest(place):
        lat, lon = PLACES[place]
        return min(graph, key=lambda p: math.dist(p, (lon, lat)))

    source, target = nearest(start), nearest(end)
    best = {source: 0.0}
    previous = {}
    queue = [(0.0, source)]
    while queue:
        dist, node = heapq.heappop(queue)
        if node == target:
            break
        if dist > best[node]:
            continue
        for neighbour, step in graph[node]:
            candidate = dist + step
            if candidate < best.get(neighbour, math.inf):
                best[neighbour] = candidate
                previous[neighbour] = node
                heapq.heappush(queue, (candidate, neighbour))
    path = [target]
    while path[-1] != source:
        path.append(previous[path[-1]])
    return [(lat, lon) for lon, lat in reversed(path)]


def via(*places):
    return [PLACES[p] if isinstance(p, str) else p for p in places]


def offset(points, distance):
    """Shift a polyline sideways so two routes on the same river stay visible."""
    shifted = []
    for i, (lat, lon) in enumerate(points):
        a = points[max(i - 1, 0)]
        b = points[min(i + 1, len(points) - 1)]
        dx, dy = b[1] - a[1], b[0] - a[0]
        length = math.hypot(dx, dy) or 1.0
        shifted.append((lat - dx / length * distance, lon + dy / length * distance))
    return shifted


def base_map(ne_dir, extent, countries):
    west, east, south, north = extent
    fig = plt.figure(figsize=(8, 6), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(west, east)
    ax.set_ylim(south, north)
    ax.set_aspect("equal")
    ax.set_facecolor(SEA)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    for feature in load(ne_dir, "ne_50m_land"):
        for ring in rings_of(feature["geometry"]):
            ax.add_patch(Polygon(ring, closed=True, facecolor=LAND, edgecolor="#CECDC3", linewidth=0.5))
    for feature in load(ne_dir, "ne_50m_admin_0_boundary_lines_land"):
        for line in lines_of(feature["geometry"]):
            xs, ys = zip(*line)
            ax.plot(xs, ys, color=BORDER, linewidth=0.5, linestyle=(0, (3, 2)))
    rivers = load(ne_dir, "ne_10m_rivers_lake_centerlines")
    for feature in rivers:
        if feature["properties"].get("scalerank", 99) > 7:
            continue
        for line in lines_of(feature["geometry"]):
            xs, ys = zip(*line)
            ax.plot(xs, ys, color=RIVER, linewidth=0.9, alpha=0.75, solid_capstyle="round")
    for feature in load(ne_dir, "ne_50m_lakes"):
        for ring in rings_of(feature["geometry"]):
            ax.add_patch(Polygon(ring, closed=True, facecolor=SEA, edgecolor=RIVER, linewidth=0.4))

    for name, (lat, lon) in countries.items():
        ax.text(lon, lat, name, fontsize=7, color=BORDER, ha="center", va="center",
                fontfamily=FONT, fontweight="bold")
    return fig, ax, rivers


def draw_route(ax, points, color, dashed=False):
    lats, lons = zip(*points)
    ax.plot(lons, lats, color=color, linewidth=2.2, linestyle=(0, (4, 2.5)) if dashed else "-",
            solid_capstyle="round", solid_joinstyle="round", zorder=5)


def label(ax, place, text, dx=0.25, dy=0.25, ha="left", bold=False):
    lat, lon = PLACES[place]
    ax.plot(lon, lat, "o", markersize=4.5, color=TEXT, markeredgecolor=LAND,
            markeredgewidth=1.0, zorder=6)
    ax.text(lon + dx, lat + dy, text, fontsize=7.5, color=TEXT, ha=ha, va="center",
            fontfamily=FONT, fontweight="bold" if bold else "normal", zorder=7,
            linespacing=1.15,
            bbox=dict(boxstyle="round,pad=0.15", facecolor=LAND, edgecolor="none", alpha=0.8))


def title_block(ax, x, y, title, subtitle):
    ax.text(x, y, title, fontsize=14, color=TEXT, fontfamily=FONT, fontweight="bold",
            ha="left", va="top", transform=ax.transAxes)
    ax.text(x, y - 0.055, subtitle, fontsize=8.5, color=TEXT_SECONDARY, fontfamily=FONT,
            ha="left", va="top", transform=ax.transAxes)


def footer(ax):
    ax.text(0.99, 0.012, "Positions of historic places approximate · Map data: Natural Earth",
            fontsize=6, color=TEXT_SECONDARY, fontfamily=FONT, ha="right", va="bottom",
            transform=ax.transAxes)


def legend(ax, entries, loc):
    handles = [Line2D([], [], color=c, linewidth=2.2, linestyle=(0, (4, 2.5)) if d else "-")
               for _, c, d in entries]
    handles.append(Line2D([], [], color=RIVER, linewidth=0.9))
    names = [n for n, _, _ in entries] + ["Rivers (Niger, Gambia, Senegal)"]
    leg = ax.legend(handles, names, loc=loc, frameon=True, fontsize=7.5,
                    prop={"family": FONT, "size": 7.5}, borderpad=0.8, handlelength=3)
    leg.get_frame().set_facecolor(LAND)
    leg.get_frame().set_edgecolor(BORDER)
    leg.get_frame().set_linewidth(0.6)


def first_journey(ne_dir):
    fig, ax, rivers = base_map(ne_dir, (-17.5, -3.5, 9.0, 19.5), COUNTRIES_FIRST)
    niger = build_river_graph(rivers, "Niger")

    outward = via("Pisania", "Medina", "Fatteconda", "Koniakary", "Kemmoo", "Jarra",
                  "Benowm", (14.9, -7.1), (14.0, -6.6), "Ségou")
    outward += river_path(niger, "Ségou", "Silla")[1:]
    back = offset(river_path(niger, "Silla", "Bamako"), -0.12)
    back += via("Kamalia", (12.9, -10.9), (12.95, -12.3), (13.4, -13.6), "Pisania")
    draw_route(ax, back, ROUTE_BACK, dashed=True)
    draw_route(ax, outward, ROUTE_OUT)

    label(ax, "Pisania", "Pisania\nDec 1795 / Jun 1797", dx=0.0, dy=0.55, ha="center", bold=True)
    label(ax, "Medina", "Medina", dy=0.3)
    label(ax, "Fatteconda", "Fatteconda", dy=0.3)
    label(ax, "Koniakary", "Koniakary", dy=0.3)
    label(ax, "Kemmoo", "Kemmoo", dy=-0.35)
    label(ax, "Jarra", "Jarra", dx=-0.25, ha="right", dy=0.25)
    label(ax, "Benowm", "Benowm\ncaptive of the Moors\nMar–Jun 1796", dx=0.3, dy=0.45)
    label(ax, "Ségou", "Ségou\nfirst sight of the Niger\n20 Jul 1796", dx=0.15, dy=-0.6)
    label(ax, "Silla", "Silla\nturned back\nJul 1796", dx=0.3, dy=0.45)
    label(ax, "Bamako", "Bamako", dx=0.25, dy=-0.3)
    label(ax, "Kamalia", "Kamalia\nill for seven months\nwith Karfa Taura", dx=-0.25, dy=-0.7, ha="right")

    title_block(ax, 0.025, 0.975, "The first journey, 1795–1797",
                "Mungo Park's search for the Niger, from the Gambia to Silla and back")
    legend(ax, [("Outward, Dec 1795 – Jul 1796", ROUTE_OUT, False),
                ("Return, Jul 1796 – Jun 1797", ROUTE_BACK, True)], "lower left")
    footer(ax)
    fig.savefig(OUT_DIR / "first-journey.png", facecolor=SEA)
    plt.close(fig)


def second_journey(ne_dir):
    fig, ax, rivers = base_map(ne_dir, (-18.0, 8.0, 4.5, 24.0), COUNTRIES_SECOND)
    niger = build_river_graph(rivers, "Niger")

    overland = via("Kayee", "Pisania", "Badoo", (13.1, -12.2), "Bambouk", (12.95, -10.75),
                   (13.05, -9.5), "Bamako")
    on_river = river_path(niger, "Bamako", "Bussa")
    draw_route(ax, overland, ROUTE_BACK, dashed=True)
    draw_route(ax, on_river, ROUTE_OUT)

    label(ax, "Kayee", "Kayee\n27 Apr 1805", dx=0.1, dy=-0.85, bold=True)
    label(ax, "Bambouk", "Bambouk", dy=-0.45)
    label(ax, "Bamako", "Bamako\nback on the Niger\n19 Aug 1805", dx=-0.3, dy=-1.0, ha="right")
    label(ax, "Sansanding", "Sansanding\nHMS Joliba sets off\n19 Nov 1805", dx=-0.4, dy=1.0, ha="right")
    label(ax, "Timbuktu", "Timbuktu", dx=-0.3, dy=0.4, ha="right")
    label(ax, "Gao", "Gao", dy=0.35)
    label(ax, "Yauri", "Yauri", dx=0.35, dy=0.15)
    label(ax, "Bussa", "Bussa rapids\nPark drowns, early 1806", dx=-0.35, dy=-0.7, ha="right", bold=True)

    title_block(ax, 0.025, 0.975, "The second journey, 1805–1806",
                "From the Gambia overland to the Niger, then 1,500 miles downriver")
    legend(ax, [("Overland, Apr – Aug 1805", ROUTE_BACK, True),
                ("By canoe and HMS Joliba, Aug 1805 – 1806", ROUTE_OUT, False)], "lower left")
    footer(ax)
    fig.savefig(OUT_DIR / "second-journey.png", facecolor=SEA)
    plt.close(fig)


if __name__ == "__main__":
    ne_dir = Path(sys.argv[1])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    first_journey(ne_dir)
    second_journey(ne_dir)
