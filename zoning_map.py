import pandas as pd
import matplotlib.pyplot as plt

def generate_zoning_map():
    # Load the data
    df = pd.read_csv('data.csv')
    
    # Extract coordinates for the Depot (Node 0)
    depot = df[df['Node ID (Team adds)'] == 0].iloc[0]
    depot_lat, depot_lon = depot['Latitude (Team adds)'], depot['Longitude (Team adds)']
    
    # Define our geographic zones based on the address column
    # We will create a new column called 'Zone'
    df['Zone'] = 'Unassigned'
    df.loc[df['Address & Barangay (Auto)'].str.contains('Tierra Nova', case=False, na=False), 'Zone'] = 'Zone 1 (Tierra Nova)'
    df.loc[df['Address & Barangay (Auto)'].str.contains('Neovista', case=False, na=False), 'Zone'] = 'Zone 2 (Neovista)'
    df.loc[df['Address & Barangay (Auto)'].str.contains('Northville', case=False, na=False), 'Zone'] = 'Zone 3 (Northville)'
    df.loc[df['Address & Barangay (Auto)'].str.contains('Avana', case=False, na=False), 'Zone'] = 'Zone 4 (Avana)'
    
    # Remove the depot from the customer zoning plot
    customers = df[df['Node ID (Team adds)'] != 0]
    
    # Setup the plot
    plt.figure(figsize=(10, 8))
    
    # Define colors for each zone
    zone_colors = {
        'Zone 1 (Tierra Nova)': 'blue',
        'Zone 2 (Neovista)': 'green',
        'Zone 3 (Northville)': 'orange',
        'Zone 4 (Avana)': 'purple',
        'Unassigned': 'gray'
    }
    
    # Plot each zone
    for zone_name, color in zone_colors.items():
        zone_data = customers[customers['Zone'] == zone_name]
        if not zone_data.empty:
            # We use alpha=0.6 to make the dots slightly transparent, showing density
            plt.scatter(zone_data['Longitude (Team adds)'], zone_data['Latitude (Team adds)'], 
                        c=color, label=zone_name, s=100, alpha=0.6, edgecolors='black')
            
    # Plot the Depot
    plt.plot(depot_lon, depot_lat, 'rs', markersize=14, zorder=5, label='DEPOT (Water Station)')
    
    # Formatting the visual for an academic paper
    plt.title('ACA 2: Geographic Zoning Allocation by Subdivision', fontsize=14, fontweight='bold')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend(title="Delivery Territories", loc='best')
    
    # Save the file
    filename = 'aca2_zoning_map.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"SUCCESS: '{filename}' has been created! You can now download it and put it in your paper.")

if __name__ == '__main__':
    generate_zoning_map()