"""
Route graph + disruption simulation service.

This is Member 6's NetworkX logic (previously stuck in a standalone
backend/main.py CLI script), ported into an importable service so the
FastAPI app can actually call it.
"""

import heapq

import networkx as nx

# ------------------------------------------------------------------
# GRAPH DEFINITION
# ------------------------------------------------------------------

G = nx.Graph()

G.add_nodes_from([
    "Guwahati",
    "Shillong",
    "Silchar",
    "Aizawl",
    "Agartala",
    "Imphal",
])

G.add_edge("Guwahati", "Shillong", distance=100, time=180, risk=2)
G.add_edge("Guwahati", "Silchar", distance=300, time=360, risk=3)
G.add_edge("Shillong", "Silchar", distance=320, time=420, risk=4)
G.add_edge("Silchar", "Aizawl", distance=180, time=200, risk=1)
G.add_edge("Silchar", "Agartala", distance=400, time=500, risk=5)
G.add_edge("Aizawl", "Imphal", distance=400, time=600, risk=4)
G.add_edge("Agartala", "Imphal", distance=350, time=540, risk=3)

for _u, _v, _data in G.edges(data=True):
    _data["cost"] = _data["distance"] + _data["time"] + (_data["risk"] * 10)


NODE_LOOKUP = {name.lower(): name for name in G.nodes}


def normalize_location(name: str) -> str | None:
    """Case-insensitive lookup so 'guwahati' / 'GUWAHATI' both resolve."""
    return NODE_LOOKUP.get(name.strip().lower())


def list_locations() -> list[str]:
    return sorted(G.nodes)


# ------------------------------------------------------------------
# CORE GRAPH OPS
# ------------------------------------------------------------------

def find_route(graph: nx.Graph, start: str, destination: str) -> list[str]:
    return nx.shortest_path(graph, start, destination, weight="cost")


def route_details(graph: nx.Graph, route: list[str]) -> tuple[float, float, float]:
    distance = nx.path_weight(graph, route, weight="distance")
    time = nx.path_weight(graph, route, weight="time")

    risk = sum(
        graph[route[i]][route[i + 1]]["risk"]
        for i in range(len(route) - 1)
    )

    return distance, time, risk


def road_is_blocked(route: list[str], blocked_road: tuple[str, str]) -> bool:
    for i in range(len(route) - 1):
        road = (route[i], route[i + 1])

        if road == blocked_road or road == blocked_road[::-1]:
            return True

    return False


def risk_to_level(avg_risk: float) -> str:
    if avg_risk >= 4:
        return "critical"
    if avg_risk >= 2:
        return "watch"
    return "stable"


# ------------------------------------------------------------------
# DEMO FLEET (used by the disruption simulator)
# ------------------------------------------------------------------

TRUCKS = [
    {"id": "Truck-1", "start": "Guwahati", "destination": "Imphal"},
    {"id": "Truck-2", "start": "Shillong", "destination": "Imphal"},
    {"id": "Truck-3", "start": "Guwahati", "destination": "Agartala"},
]


def simulate_blockage(blocked_start: str, blocked_end: str) -> dict:
    blocked_road = (blocked_start, blocked_end)

    temp_graph = G.copy()

    if not temp_graph.has_edge(blocked_start, blocked_end):
        return {"success": False, "error": "Blocked road does not exist"}

    temp_graph.remove_edge(blocked_start, blocked_end)

    results = []
    priority_queue: list[tuple[int, str]] = []

    for truck in TRUCKS:
        original_route = find_route(G, truck["start"], truck["destination"])
        original_distance, original_time, original_risk = route_details(G, original_route)

        affected = road_is_blocked(original_route, blocked_road)

        if not affected:
            results.append({
                "id": truck["id"],
                "affected": False,
                "originalRoute": original_route,
                "reroutedRoute": original_route,
                "distance": original_distance,
                "time": original_time,
                "risk": original_risk,
                "delay": 0,
                "priority": 0,
            })
            continue

        try:
            new_route = find_route(temp_graph, truck["start"], truck["destination"])
            new_distance, new_time, new_risk = route_details(temp_graph, new_route)

            delay = new_time - original_time
            priority = delay + (new_risk * 10)

            heapq.heappush(priority_queue, (-priority, truck["id"]))

            results.append({
                "id": truck["id"],
                "affected": True,
                "originalRoute": original_route,
                "reroutedRoute": new_route,
                "distance": new_distance,
                "time": new_time,
                "risk": new_risk,
                "delay": delay,
                "priority": priority,
            })

        except nx.NetworkXNoPath:
            heapq.heappush(priority_queue, (-9999, truck["id"]))

            results.append({
                "id": truck["id"],
                "affected": True,
                "originalRoute": original_route,
                "reroutedRoute": None,
                "distance": None,
                "time": None,
                "risk": None,
                "delay": None,
                "priority": 9999,
            })

    priority_order = []

    while priority_queue:
        priority, truck_id = heapq.heappop(priority_queue)
        priority_order.append({"truck": truck_id, "priority": -priority})

    return {
        "success": True,
        "blockedRoad": [blocked_start, blocked_end],
        "trucks": results,
        "priorityQueue": priority_order,
    }


def get_route(
    start: str,
    destination: str,
    blocked_start: str | None = None,
    blocked_end: str | None = None,
) -> dict:
    try:
        if blocked_start and blocked_end:
            return simulate_blockage(blocked_start, blocked_end)

        route = find_route(G, start, destination)
        distance, time, risk = route_details(G, route)

        return {
            "success": True,
            "route": route,
            "distance": distance,
            "time": time,
            "risk": risk,
        }

    except nx.NetworkXNoPath:
        return {"success": False, "error": "No route available"}

    except nx.NodeNotFound:
        return {"success": False, "error": "Location not found"}