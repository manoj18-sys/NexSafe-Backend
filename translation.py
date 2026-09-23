import sys
import json

# Import routing functions
from main import get_route


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(text):

    text = text.lower().strip()

    if any(word in text for word in [
        "emergency",
        "accident",
        "help",
        "danger",
        "injured"
    ]):
        return "EMERGENCY"

    if any(word in text for word in [
        "road blocked",
        "road is blocked",
        "blocked road",
        "road closed",
        "cannot pass",
        "can't pass"
    ]):
        return "ROAD_BLOCKED"

    if any(word in text for word in [
        "landslide",
        "mudslide",
        "rockfall",
        "debris"
    ]):
        return "LANDSLIDE"

    if any(word in text for word in [
        "flood",
        "flooded",
        "water on road",
        "waterlogging"
    ]):
        return "FLOOD_ALERT"

    if any(word in text for word in [
        "eta",
        "how long",
        "when will i reach",
        "arrival time"
    ]):
        return "ETA_QUERY"

    if any(word in text for word in [
        "which route",
        "which road",
        "alternate route",
        "alternative route",
        "where should i go",
        "which way"
    ]):
        return "ROUTE_QUERY"

    if any(word in text for word in [
        "delivery",
        "shipment",
        "cargo",
        "commodity"
    ]):
        return "DELIVERY_STATUS"

    if any(word in text for word in [
        "weather",
        "rain",
        "rainfall",
        "storm"
    ]):
        return "WEATHER_QUERY"

    return "UNKNOWN"


# ============================================================
# PRIORITY
# ============================================================

def get_priority(intent):

    if intent == "EMERGENCY":
        return "CRITICAL"

    if intent in [
        "LANDSLIDE",
        "FLOOD_ALERT"
    ]:
        return "CRITICAL"

    if intent == "ROAD_BLOCKED":
        return "HIGH"

    if intent == "ROUTE_QUERY":
        return "HIGH"

    if intent in [
        "ETA_QUERY",
        "DELIVERY_STATUS",
        "WEATHER_QUERY"
    ]:
        return "MEDIUM"

    return "LOW"


# ============================================================
# ROUTE FORMATTER
# ============================================================

def format_route(route):

    if not route:
        return "No route available"

    return " → ".join(route)


# ============================================================
# MEMBER 6 ROUTE INTEGRATION
# ============================================================

def get_reroute_information(
    start,
    destination,
    blocked_start,
    blocked_end
):

    result = get_route(
        start,
        destination,
        blocked_start,
        blocked_end
    )

    return result


# ============================================================
# DRIVER RESPONSE
# ============================================================

def generate_driver_response(
    intent,
    route_result
):

    # --------------------------------------------------------
    # EMERGENCY
    # --------------------------------------------------------

    if intent == "EMERGENCY":

        return {
            "action": "EMERGENCY",
            "response":
                "Emergency detected. Stop at a safe location "
                "and contact emergency services."
        }


    # --------------------------------------------------------
    # ROAD BLOCKED / LANDSLIDE / FLOOD
    # --------------------------------------------------------

    if intent in [
        "ROAD_BLOCKED",
        "LANDSLIDE",
        "FLOOD_ALERT"
    ]:

        if not route_result.get("success"):

            return {
                "action": "STOP",
                "response":
                    "No alternate route is currently available. "
                    "Please stop at a safe location."
            }

        trucks = route_result.get("trucks", [])

        if not trucks:

            return {
                "action": "STOP",
                "response":
                    "No affected vehicles were found."
            }

        # For demonstration, use the first affected truck
        affected_truck = None

        for truck in trucks:

            if truck.get("affected"):

                affected_truck = truck
                break

        if affected_truck is None:

            return {
                "action": "CONTINUE",
                "response":
                    "Your current route is not affected. "
                    "You may continue."
            }

        rerouted_route = affected_truck.get(
            "reroutedRoute"
        )

        delay = affected_truck.get(
            "delay",
            0
        )

        priority = affected_truck.get(
            "priority",
            0
        )

        # No alternate route
        if not rerouted_route:

            return {
                "action": "STOP",
                "response":
                    "The road is blocked and no alternate "
                    "route is available. Please stop safely.",
                "priority": priority
            }

        route_text = format_route(
            rerouted_route
        )

        return {
            "action": "REROUTE",
            "response":
                f"Road disruption detected. "
                f"Take the alternate route: {route_text}. "
                f"Expected additional delay: {delay} minutes.",
            "reroutedRoute": rerouted_route,
            "delay": delay,
            "priority": priority
        }


    # --------------------------------------------------------
    # ETA
    # --------------------------------------------------------

    if intent == "ETA_QUERY":

        if route_result.get("success"):

            trucks = route_result.get("trucks", [])

            if trucks:

                truck = trucks[0]

                time = truck.get(
                    "time"
                )

                delay = truck.get(
                    "delay",
                    0
                )

                return {
                    "action": "ETA",
                    "response":
                        f"Estimated travel time is "
                        f"{time} minutes. "
                        f"Current additional delay is "
                        f"{delay} minutes."
                }

        return {
            "action": "ETA",
            "response":
                "Estimated arrival time is currently unavailable."
        }


    # --------------------------------------------------------
    # ROUTE QUERY
    # --------------------------------------------------------

    if intent == "ROUTE_QUERY":

        if route_result.get("success"):

            trucks = route_result.get("trucks", [])

            if trucks:

                truck = trucks[0]

                route = truck.get(
                    "reroutedRoute"
                )

                if route:

                    return {
                        "action": "ROUTE",
                        "response":
                            f"Recommended route: "
                            f"{format_route(route)}."
                    }

        return {
            "action": "ROUTE",
            "response":
                "A route could not be calculated."
        }


    # --------------------------------------------------------
    # DELIVERY
    # --------------------------------------------------------

    if intent == "DELIVERY_STATUS":

        return {
            "action": "DELIVERY_STATUS",
            "response":
                "Your delivery status is being processed."
        }


    # --------------------------------------------------------
    # WEATHER
    # --------------------------------------------------------

    if intent == "WEATHER_QUERY":

        return {
            "action": "WEATHER",
            "response":
                "Current weather information is being retrieved."
        }


    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return {
        "action": "CLARIFY",
        "response":
            "Please describe the road, route, "
            "or delivery issue."
    }


# ============================================================
# MAIN MEMBER 5 PIPELINE
# ============================================================

def process_driver_message(
    text,
    start,
    destination,
    blocked_start=None,
    blocked_end=None
):

    # STEP 1
    # Understand what the driver said

    intent = detect_intent(text)


    # STEP 2
    # Determine urgency

    priority = get_priority(intent)


    # STEP 3
    # Get verified route information
    # from Member 6

    route_result = get_reroute_information(
        start,
        destination,
        blocked_start,
        blocked_end
    )


    # STEP 4
    # Convert route information into
    # driver-friendly response

    response = generate_driver_response(
        intent,
        route_result
    )


    # STEP 5
    # Return combined result

    return {
        "success": True,
        "intent": intent,
        "priorityLevel": priority,
        "driverResponse": response,
        "routingData": route_result
    }


# ============================================================
# COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":

    # Example:
    #
    # python member5_ai.py
    #
    # It will run the demonstration below.

    text = "The road ahead is blocked. Where should I go?"

    start = "Guwahati"
    destination = "Imphal"

    blocked_start = "Guwahati"
    blocked_end = "Shillong"


    result = process_driver_message(
        text=text,
        start=start,
        destination=destination,
        blocked_start=blocked_start,
        blocked_end=blocked_end
    )


    print(
        json.dumps(
            result,
            indent=4
        )
    )