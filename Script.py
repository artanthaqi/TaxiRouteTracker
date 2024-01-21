import pandas as pd
import requests
from tqdm import tqdm

def find_nodes_for_location(lat, lon):
    nominatim_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"

    response = requests.get(nominatim_url)
    
    data = response.json()

    osm_id = None
    street_name = None
    if 'osm_id' in data:
        osm_id = data['osm_id']
    if 'address' in data and 'road' in data['address']:
        street_name = data['address']['road']
    else:
        street_name = "Unknown"
    modified_street_name = street_name.replace(" ", "_")
    return osm_id, modified_street_name

def find_segment_for_location(lat, lon):
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    street_id, street_name = find_nodes_for_location(lat, lon)

    if not street_id:
        print("No street found based on the provided coordinates.")
        return None, None

    overpass_query = f"""
        [out:json];
        way({street_id});
        node(w);
        out;
    """

    response = requests.post(overpass_url, data=overpass_query)

    data = response.json()

    nodes = []
    if 'elements' in data:
        for element in data['elements']:
            if element['type'] == 'node':
                nodes.append({
                    'id': element['id'],
                    'latitude': element['lat'],
                    'longitude': element['lon']
                })

    segment_info = find_segment_info(lat, lon, nodes)

    return segment_info, street_name

def find_segment_info(lat, lon, nodes):
    closest_nodes = sorted(nodes, key=lambda node: distance(lat, lon, node['latitude'], node['longitude']))[:2]
    
    if len(closest_nodes) != 2:
        return None

    closest_nodes.sort(key=lambda x: nodes.index(x))

    segment_index = nodes.index(closest_nodes[0])
    segment_length = distance(closest_nodes[0]['latitude'], closest_nodes[0]['longitude'],
                               closest_nodes[1]['latitude'], closest_nodes[1]['longitude'])

    return {
        'segment_index': segment_index,
        'segment_length': segment_length
    }

def distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    R = 1000.0

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance_km = R * c

    return distance_km


def process_csv_file(df):
    current_segment = None
    current_street_name = None
    passengerPicedUp = False
    total_segments = 0
    segment_list = []

    # Use tqdm to create a progress bar
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows", unit="row"):
        if row['Di2'] == 1:
            passengerPicedUp = True
            latitude = float(row['Latitude'])
            longitude = float(row['Longitute'])

            segment_info, street_name = find_segment_for_location(latitude, longitude)

            if segment_info and street_name:
                current_street_name = street_name
                current_segment = {
                    'street_name': current_street_name,
                    'segment_index': segment_info['segment_index'],
                    'segment_length': segment_info['segment_length']
                }

                segment = f"{current_segment['segment_index']} {current_street_name}_{current_segment['segment_index']}"

                if segment not in segment_list:
                    segment_list.append(segment)
                    total_segments += 1

        elif row['Di2'] == 0 and passengerPicedUp:
            passengerPicedUp = False
            with open('output.txt', 'a') as file:
                for element in segment_list:
                    file.write(element + '\n')

            if len(segment_list) > 0:
                with open('output.txt', 'a') as file:
                    file.write(f"{len(segment_list)} ")
                    formatted_elements = [f"{element.split(' ', 1)[1]}" for element in segment_list]
                    file.write(', '.join(formatted_elements))
                    file.write('\n')
            segment_list.clear()
        


csv_file_path = "SampleCsv.csv"
df = pd.read_csv(csv_file_path)
process_csv_file(df)


