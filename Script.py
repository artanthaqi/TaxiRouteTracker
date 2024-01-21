import pandas as pd
import requests

def find_nodes_for_location(lat, lon):
    nominatim_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"

    # Make the request to the Nominatim API for reverse geocoding
    response = requests.get(nominatim_url)
    
    # Parse the JSON response
    data = response.json()

    # Extract the osm_id and street name from the response
    osm_id = None
    street_name = None
    if 'osm_id' in data:
        osm_id = data['osm_id']
    if 'address' in data and 'road' in data['address']:
        street_name = data['address']['road']

    return osm_id, street_name

def find_segment_for_location(lat, lon):
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Find the street ID and street name using reverse geocoding
    street_id, street_name = find_nodes_for_location(lat, lon)

    if not street_id:
        print("No street found based on the provided coordinates.")
        return None, None

    # Define the Overpass query to get all nodes for the given street ID
    overpass_query = f"""
        [out:json];
        way({street_id});
        node(w);
        out;
    """

    # Make the request to the Overpass API
    response = requests.post(overpass_url, data=overpass_query)

    # Parse the JSON response
    data = response.json()

    # Extract the nodes from the response
    nodes = []
    if 'elements' in data:
        for element in data['elements']:
            if element['type'] == 'node':
                nodes.append({
                    'id': element['id'],
                    'latitude': element['lat'],
                    'longitude': element['lon']
                })

    # Find the segment of the street based on proximity to the provided coordinates
    segment_info = find_segment_info(lat, lon, nodes)

    return segment_info, street_name

def find_segment_info(lat, lon, nodes):
    # Find the two nodes closest to the specified coordinates
    closest_nodes = sorted(nodes, key=lambda node: distance(lat, lon, node['latitude'], node['longitude']))[:2]
    
    if len(closest_nodes) != 2:
        return None

    # Sort the nodes by their order in the way
    closest_nodes.sort(key=lambda x: nodes.index(x))

    # Find the segment index and length
    segment_index = nodes.index(closest_nodes[0])
    segment_length = distance(closest_nodes[0]['latitude'], closest_nodes[0]['longitude'],
                               closest_nodes[1]['latitude'], closest_nodes[1]['longitude'])

    return {
        'segment_index': segment_index,
        'segment_length': segment_length
    }

def distance(lat1, lon1, lat2, lon2):
    # Calculate the Haversine distance between two sets of coordinates
    from math import radians, sin, cos, sqrt, atan2

    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate the differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in kilometers
    distance_km = R * c

    return distance_km


def process_csv_file(df):
    in_segment = False
    current_segment = None
    current_street_name = None
    previous_segment = None
    printed_segments = set()
    segments_with_passenger = set()
    total_segments = 0  # New variable to track total segments

    for index, row in df.iterrows():
        # Check if Di2 is 1
        if row['Di2'] == 1:
            if not in_segment:
                # Start a new segment
                in_segment = True
                device_datetime = row['DeviceDateTime']
                latitude = float(row['Latitude'])
                longitude = float(row['Longitute'])

                # Find the segment information and street name for the specified coordinates
                segment_info, street_name = find_segment_for_location(latitude, longitude)

                if segment_info and street_name and previous_segment != segment_info['segment_index']:
                    current_street_name = street_name
                    previous_segment = segment_info['segment_index']
                    current_segment = {
                        'start_datetime': device_datetime,
                        'end_datetime': None,
                        'street_name': current_street_name,
                        'segment_index': segment_info['segment_index'],
                        'segment_length': segment_info['segment_length']
                    }

                    # Check if the segment has not been printed yet
                    if current_segment['segment_index'] not in printed_segments:
                        print(f"Segment found: {current_street_name}[{current_segment['segment_index']}]")
                        printed_segments.add(current_segment['segment_index'])

                        # If Di2 is 1, mark the segment as having a passenger
                        segments_with_passenger.add(current_segment['segment_index'])

                    # Increment total segments
                    total_segments += 1

        elif in_segment:
            # End the current segment when Di2 becomes 0
            if current_segment:
                current_segment['end_datetime'] = row['DeviceDateTime']
                in_segment = False

    # Print the count of segments with a passenger
    print(f"\nNumber of segments with a passenger: {len(segments_with_passenger)}")
    # Print the total number of segments
    print(f"Total number of segments: {total_segments}")

# Example usage
csv_file_path = "TaxiRouteData-October.csv"
df = pd.read_csv(csv_file_path)
process_csv_file(df)


