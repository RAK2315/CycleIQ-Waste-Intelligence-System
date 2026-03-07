import math
import random
from typing import List, Dict

def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def optimize_routes(collection_points: List[Dict], num_trucks: int = 3) -> List[Dict]:
    try:
        return _ortools_optimize(collection_points, num_trucks)
    except Exception as e:
        print(f"OR-Tools unavailable: {e}, using greedy routing")
        return _greedy_optimize(collection_points, num_trucks)

def _ortools_optimize(collection_points, num_trucks):
    from ortools.constraint_solver import routing_enums_pb2, pywrapcp

    # Prioritize high fill points, but include all active ones
    active = [p for p in collection_points if p.get("current_fill_level", 0) > 30]
    if len(active) < num_trucks * 2:
        active = collection_points

    # Cap to manageable size for speed
    active = sorted(active, key=lambda x: x.get("current_fill_level", 0), reverse=True)[:40]
    n = len(active)
    if n < 2:
        return _greedy_optimize(collection_points, num_trucks)

    dist_matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0)
            else:
                d = haversine(active[i]["latitude"], active[i]["longitude"],
                              active[j]["latitude"], active[j]["longitude"])
                row.append(int(d * 100))  # scaled
        dist_matrix.append(row)

    manager = pywrapcp.RoutingIndexManager(n, num_trucks, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_idx, to_idx):
        return dist_matrix[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]

    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    # Add distance dimension to balance routes across trucks
    routing.AddDimension(transit_idx, 0, 10000, True, "Distance")
    dist_dimension = routing.GetDimensionOrDie("Distance")
    dist_dimension.SetGlobalSpanCostCoefficient(100)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = 5

    solution = routing.SolveWithParameters(params)
    if not solution:
        return _greedy_optimize(collection_points, num_trucks)

    routes = []
    for truck_id in range(num_trucks):
        index = routing.Start(truck_id)
        route_points = []
        total_dist = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route_points.append(active[node])
            next_index = solution.Value(routing.NextVar(index))
            if not routing.IsEnd(next_index):
                next_node = manager.IndexToNode(next_index)
                total_dist += dist_matrix[node][next_node]
            index = next_index

        if route_points:
            dist_km = total_dist / 100
            routes.append({
                "truck_id": f"MCD-T{truck_id+1:02d}",
                "collection_sequence": route_points,
                "total_distance_km": round(dist_km, 2),
                "estimated_time_minutes": round(dist_km * 3 + len(route_points) * 7, 1),
                "estimated_emissions_kg": round(dist_km * 0.21, 3),
                "num_stops": len(route_points),
                "status": "planned"
            })
    return routes if routes else _greedy_optimize(collection_points, num_trucks)

def _greedy_optimize(collection_points, num_trucks):
    """Nearest-neighbor greedy routing — properly balanced across trucks."""
    active = [p for p in collection_points if p.get("current_fill_level", 0) > 30]
    if len(active) < num_trucks:
        active = list(collection_points)

    # Sort by fill level desc, then round-robin across trucks
    active = sorted(active, key=lambda x: x.get("current_fill_level", 0), reverse=True)
    truck_routes = [[] for _ in range(num_trucks)]
    for i, point in enumerate(active):
        truck_routes[i % num_trucks].append(point)

    routes = []
    for i, truck_points in enumerate(truck_routes):
        if not truck_points:
            continue
        # Nearest neighbor ordering within each truck's points
        ordered = _nearest_neighbor_order(truck_points)
        total_dist = sum(
            haversine(ordered[j]["latitude"], ordered[j]["longitude"],
                      ordered[j+1]["latitude"], ordered[j+1]["longitude"])
            for j in range(len(ordered)-1)
        )
        routes.append({
            "truck_id": f"MCD-T{i+1:02d}",
            "collection_sequence": ordered,
            "total_distance_km": round(total_dist, 2),
            "estimated_time_minutes": round(total_dist * 3 + len(ordered) * 7, 1),
            "estimated_emissions_kg": round(total_dist * 0.21, 3),
            "num_stops": len(ordered),
            "status": "planned"
        })
    return routes

def _nearest_neighbor_order(points):
    if len(points) <= 1:
        return points
    unvisited = list(points)
    ordered = [unvisited.pop(0)]
    while unvisited:
        last = ordered[-1]
        nearest = min(unvisited, key=lambda p: haversine(
            last["latitude"], last["longitude"],
            p["latitude"], p["longitude"]))
        ordered.append(nearest)
        unvisited.remove(nearest)
    return ordered