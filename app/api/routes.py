from fastapi import APIRouter, HTTPException
import networkx as nx

from app.schemas.route import (
    RouteRequest,
    RouteAnalysis
)

from app.services import graph_service


router = APIRouter(
    prefix="/route",
    tags=["Route Intelligence"]
)


@router.post(
    "/analyze",
    response_model=RouteAnalysis
)
def analyze_route(data: RouteRequest):

    origin = graph_service.normalize_location(data.origin)
    destination = graph_service.normalize_location(data.destination)

    if not origin or not destination:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unknown location. Valid stops are: "
                + ", ".join(graph_service.list_locations())
            ),
        )

    try:
        path = graph_service.find_route(
            graph_service.G, origin, destination
        )

        distance, time, risk = graph_service.route_details(
            graph_service.G, path
        )

    except nx.NetworkXNoPath:
        raise HTTPException(
            status_code=404,
            detail="No route exists between these two locations.",
        )

    hop_count = max(len(path) - 1, 1)
    avg_risk = risk / hop_count
    risk_level = graph_service.risk_to_level(avg_risk)

    route_status = {
        "stable": "clear",
        "watch": "monitored",
        "critical": "high alert",
    }[risk_level]

    # An alternate exists if there is more than one simple path
    # between origin and destination in the graph.
    alternate_available = False
    try:
        paths_iter = nx.shortest_simple_paths(
            graph_service.G, origin, destination, weight="cost"
        )
        next(paths_iter)
        next(paths_iter)
        alternate_available = True
    except (StopIteration, nx.NetworkXNoPath):
        alternate_available = False

    recommended_action = {
        "stable": "Corridor is clear. Proceed as planned.",
        "watch": "Continue with caution. Monitor corridor conditions.",
        "critical": (
            "High risk corridor. Consider rerouting or "
            "delaying departure until conditions improve."
        ),
    }[risk_level]

    return RouteAnalysis(
        origin=origin,
        destination=destination,
        path=path,
        distance_km=round(distance, 1),
        estimated_minutes=round(time),
        risk_level=risk_level,
        route_status=route_status,
        alternate_available=alternate_available,
        recommended_action=recommended_action,
    )


@router.post("/reroute")
def reroute(data: RouteRequest):

    return {
        "status": "rerouting",
        "origin": data.origin,
        "destination": data.destination,
        "message": (
            "Alternate route calculation "
            "has been requested."
        )
    }