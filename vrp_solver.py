import pandas as pd
import math
import folium
import matplotlib.pyplot as plt
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# 1. Haversine Formula for Distance
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return int(round(R * c)) 

def create_data_model():
    data = {}
    df = pd.read_csv("data.csv")
    df['Node ID (Team adds)'] = pd.to_numeric(df['Node ID (Team adds)'], errors='coerce')
    df = df.sort_values('Node ID (Team adds)').reset_index(drop=True)
    
    data['lats'] = df['Latitude (Team adds)'].tolist()
    data['lons'] = df['Longitude (Team adds)'].tolist()
    data['demands'] = pd.to_numeric(df['Gallons Ordered (Auto)'], errors='coerce').fillna(0).astype(int).tolist()
    
    distance_matrix = []
    for i in range(len(data['lats'])):
        row = []
        for j in range(len(data['lats'])):
            if i == j:
                row.append(0)
            else:
                row.append(calculate_distance(data['lats'][i], data['lons'][i], data['lats'][j], data['lons'][j]))
        distance_matrix.append(row)
        
    data['distance_matrix'] = distance_matrix
    data['vehicle_capacities'] = [8] * 25 
    data['num_vehicles'] = 25
    data['depot'] = 0
    return data

def print_solution_and_visuals(data, manager, routing, solution):
    # Setup for Table and Plot
    table_data = []
    plt.figure(figsize=(10, 8))
    
    # Plot all customer nodes as small gray dots first
    plt.scatter(data['lons'], data['lats'], c='lightgray', zorder=1, label='Customers')
    # Plot the Depot as a big red square
    plt.plot(data['lons'][data['depot']], data['lats'][data['depot']], 'rs', markersize=12, zorder=3, label='Depot')

    colors = ['blue', 'green', 'purple', 'orange', 'brown', 'c', 'm', 'y', 'k', 'teal']
    total_distance = 0
    total_load = 0
    trip_number = 1
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        if not routing.IsEnd(solution.Value(routing.NextVar(index))):
            route_color = colors[trip_number % len(colors)]
            route_distance = 0
            route_load = 0
            
            # String for the table and lists for the map lines
            route_str = "0"
            route_lons = [data['lons'][data['depot']]]
            route_lats = [data['lats'][data['depot']]]
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                if node_index != 0:
                    route_load += data['demands'][node_index]
                    route_str += f" -> {node_index}"
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                
                next_node = manager.IndexToNode(index)
                route_lons.append(data['lons'][next_node])
                route_lats.append(data['lats'][next_node])
                
            route_str += " -> 0"
            
            # Draw the line for this specific trip
            plt.plot(route_lons, route_lats, color=route_color, linewidth=2, marker='o', markersize=4, zorder=2)
            
            # Add to our table dataset
            table_data.append({
                "Trip": f"Trip {trip_number}",
                "Route Sequence": route_str,
                "Gallons": route_load,
                "Distance (m)": route_distance
            })
            
            total_distance += route_distance
            total_load += route_load
            trip_number += 1
            
    # 1. Output the Tabular Data
    df_results = pd.DataFrame(table_data)
    print("\n" + "="*60)
    print("                 FINAL DELIVERY SCHEDULE")
    print("="*60)
    print(df_results.to_markdown(index=False))
    print("="*60)
    print(f"Total Daily Distance: {total_distance} meters")
    print(f"Total Gallons Delivered: {total_load}\n")
    
    # Save table to CSV
    df_results.to_csv("delivery_schedule.csv", index=False)
    print("SUCCESS: 'delivery_schedule.csv' created (Open in Excel/Sheets).")
    
    # 2. Output the Static Visual Image
    plt.title('Vehicle Routing Problem - Optimal Tricycle Trips', fontsize=14, fontweight='bold')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.savefig('printable_routes.png', dpi=300, bbox_inches='tight')
    print("SUCCESS: 'printable_routes.png' created (Ready for your paper).")

def main():
    data = create_data_model()
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return data['distance_matrix'][manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        return data['demands'][manager.IndexToNode(from_index)]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_callback_index, 0, data['vehicle_capacities'], True, 'Capacity')

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(5)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print_solution_and_visuals(data, manager, routing, solution)
    else:
        print("No solution found.")

if __name__ == '__main__':
    main()