# TaxiRouteTracker

This repository contains a Python script for processing geospatial data related to taxi routes. The script utilizes the Pandas library for data manipulation and the Requests library for making API requests to geocoding and mapping services.

## Dependencies
- [Pandas](https://pandas.pydata.org/): A fast, powerful, and flexible open-source data manipulation and analysis library.
- [Requests](https://docs.python-requests.org/en/latest/): A simple HTTP library for making requests to APIs.
- [tqdm](https://github.com/tqdm/tqdm): A fast, extensible progress bar for loops and CLI.


## Installation
pip install pandas requests tqdm


## Script Overview

### `find_nodes_for_location(lat, lon)`

This function performs reverse geocoding using the OpenStreetMap Nominatim API to find the OpenStreetMap ID and street name for a given set of coordinates.

### `find_segment_for_location(lat, lon)`

This function builds upon `find_nodes_for_location` to identify the street segment information (index and length) based on proximity to the provided coordinates. It also calls `find_segment_info` for further processing.

### `find_segment_info(lat, lon, nodes)`

Given a set of nodes along a street, this function identifies the two nodes closest to the specified coordinates and calculates the segment index and length.

### `distance(lat1, lon1, lat2, lon2)`

Calculates the Haversine distance between two sets of coordinates.

### `process_csv_file(df)`

Processes a CSV file containing taxi route data. It identifies segments where a specific condition (e.g., `Di2` being 1) is met and prints information about these segments.

## Usage

```python
import pandas as pd
from your_script_file import process_csv_file

# Example usage
csv_file_path = "SampleCsv.csv"
df = pd.read_csv(csv_file_path)
process_csv_file(df)


