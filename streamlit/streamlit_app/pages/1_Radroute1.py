import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import urllib.parse
import pyrosm
import os
from shapely.geometry import Point

# Konfiguration 
# BBBike API Parameters
API_URL = "https://api.bbbike.org/api/0.2/bbbike/"
APP_ID = "smatthies"

# OpenCage API Key
OPENCAGE_API_KEY = "46bbbd3be1674994a02ad03b9569c0ed"  

# Pfad zum Fahrradnetzwerk in Berlin (OSM)
file_path = "../data/berlin-latest.osm.pbf"

# OpenCage-API wird verwendet, um Koordinaten für eine angegebene Adresse zu erhalten
def get_coordinates(address):
    """Use OpenCage to get coordinates for a given address"""
    address_encoded = urllib.parse.quote(address)
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address_encoded}&key={OPENCAGE_API_KEY}"
    
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Fehler beim Abrufen der Koordinaten für Adresse '{address}': HTTP {response.status_code}")
        return None, None

    try:
        response_json = response.json()
        if response_json and response_json['results']:
            return float(response_json['results'][0]['geometry']['lat']), float(response_json['results'][0]['geometry']['lng'])
        else:
            st.error(f"Keine Koordinaten für Adresse '{address}' gefunden.")
    except (ValueError, KeyError, IndexError) as e:
        st.error(f"Fehler beim Verarbeiten der Antwort für Adresse '{address}': {e}")
    return None, None

# BBBike-API wird verwendet, um eine Fahrradroutenplanung zwischen zwei Koordinatenpunkten zu erhalten.
def get_route(start_coords, end_coords):
    """Fetch route from BBBike API with preferred settings"""
    if start_coords is None or end_coords is None:
        st.error("Ungültige Koordinaten für Start- oder Zieladresse.")
        return None

    url = (f"{API_URL}?appid={APP_ID}"
           f"&startc_wgs84={start_coords[1]},{start_coords[0]}"
           f"&zielc_wgs84={end_coords[1]},{end_coords[0]}"
           f"&pref_seen=1&pref_cat=N1&output_as=json")  # Bevorzugter Straßentyp = Nebenstraßen (pref_cat=N1)

    response = requests.get(url)
    if response.status_code == 200:
        try:
            result = response.json()
            return result
        except ValueError as e:
            st.error(f"Fehler beim Abrufen der Route: {e}")
    else:
        st.error(f"Fehler beim Abrufen der Route: {response.status_code}")
    return None

def visualize_route(route_data):
    """Visualize route on map"""
    m = folium.Map(location=[52.5200, 13.4050], zoom_start=12)
    
    try:
        # Route als Liste von Punkten (Longitude, Latitude)
        points = [(float(coord.split(',')[1]), float(coord.split(',')[0])) for coord in route_data['LongLatPath']]
        
        # Polyline für die Route: Rot und breiter (z. B. 8)
        folium.PolyLine(points, color='blue', weight=8, opacity=0.5).add_to(m)
        
        # Startmarkierung
        folium.Marker(
            location=points[0], 
            popup="Start", 
            icon=folium.Icon(color="green", icon="play")
        ).add_to(m)
        
        # Zielmarkierung
        folium.Marker(
            location=points[-1], 
            popup="Ziel", 
            icon=folium.Icon(color="red", icon="flag")
        ).add_to(m)
        
    except KeyError as e:
        st.error(f"Fehler beim Verarbeiten der Routenpunkte: {e}")
        
    return m

# OSM-Segmentinformationen werden für die Punkte in der Route abgerufen
def fetch_osm_segment_info(route_data, file_path):
    """Fetch OSM segment info for the points in the route"""
    osm_data = []
    try:
        berlin_osm = pyrosm.OSM(file_path)
        cycle_net_berlin = berlin_osm.get_network(network_type="cycling", extra_attributes=["highway"])

        points = [(float(coord.split(',')[0]), float(coord.split(',')[1])) for coord in route_data['LongLatPath']]
        unique_points = set(points)

        for lat, lon in unique_points:
            point = Point(lon, lat)
            # Hier könnte eine kleine Abweichung helfen, um auch nahe Punkte zu finden
            buffer_point = point.buffer(0.0001)  # Ein kleines Buffer um den Punkt

            mask = cycle_net_berlin['geometry'].apply(lambda x: x.intersects(buffer_point))
            segment_info = cycle_net_berlin.loc[mask]

            if segment_info.empty:
                st.warning(f"Keine Segmente für Punkt {point} gefunden.")
            else:
                osm_data.append(segment_info)

    except KeyError:
        st.error("Fehler: API-Antwortstruktur enthält keine 'LongLatPath'.")
    except Exception as e:
        st.error(f"Allgemeiner Fehler: {e}")

    if osm_data:
        osm_gdf = gpd.GeoDataFrame(pd.concat(osm_data, ignore_index=True))
        highways = osm_gdf[['geometry', 'highway']].drop_duplicates()

        st.write("Highway-Informationen für die Route:")
        st.write(highways.dropna())
        
        return highways
    return gpd.GeoDataFrame()



# Pipeline-Funktion: kombiniert die Funktionen, um alles zusammenzubringen
def pipeline(start_address, end_address):
    start_coords = get_coordinates(start_address)
    end_coords = get_coordinates(end_address)
    if None in start_coords or None in end_coords:
        st.error("Konnte die Koordinaten für eine der eingegebenen Adressen nicht ermitteln.")
        return

    route_data = get_route(start_coords, end_coords)
    if route_data:
        route_map = visualize_route(route_data)
        folium_static(route_map)
        
        osm_segment_info = fetch_osm_segment_info(route_data, file_path)
        if not osm_segment_info.empty:
            st.write(osm_segment_info[['highway']].dropna())
        else:
            st.write("Keine OSM-Segmentinformationen verfügbar.")
    else:
        st.error("Konnte die Route nicht abrufen.")
        

# Streamlit-App Setup
st.title("Berlin Fahrradroute Planung")

start_address = st.text_input("Startadresse eingeben", value="Wildenbruchstraße 33, Berlin")
end_address = st.text_input("Zieladresse eingeben", value="Rubensstr. 6, Berlin")

if st.button("Route berechnen"):
    if start_address and end_address:
        pipeline(start_address, end_address)
    else:
        st.error("Bitte sowohl Start- als auch Zieladresse eingeben.")
