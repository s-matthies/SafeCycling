import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import urllib.parse
import pyrosm

# Konfiguration
API_URL = "https://api.bbbike.org/api/0.2/bbbike/"
APP_ID = "smatthies"
OPENCAGE_API_KEY = "46bbbd3be1674994a02ad03b9569c0ed"  
file_path = "../data/berlin-latest.osm.pbf"

# Funktion zum Abrufen von Koordinaten für eine angegebene Adresse
def get_coordinates(address):
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

# Funktion zum Abrufen der Route von der BBBike-API
def get_route(start_coords, end_coords):
    if start_coords is None or end_coords is None:
        st.error("Ungültige Koordinaten für Start- oder Zieladresse.")
        return None

    url = (f"{API_URL}?appid={APP_ID}"
           f"&startc_wgs84={start_coords[1]},{start_coords[0]}"
           f"&zielc_wgs84={end_coords[1]},{end_coords[0]}"
           f"&pref_seen=1&pref_cat=N1&output_as=json")

    st.write(f"Routen-URL: {url}")
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

# Funktion zur Visualisierung der Route auf der Karte
def visualize_route(route_data, m):
    try:
        points = [(float(coord.split(',')[1]), float(coord.split(',')[0])) for coord in route_data['LongLatPath']]
        folium.PolyLine(points, color='green', weight=8, opacity=0.6).add_to(m)  # Route in Grün, 8px breit, 60% transparent
        
        for point in points:
            folium.CircleMarker(location=point,
                                radius=3,
                                color="red",
                                fill=True,
                                fill_color="red").add_to(m)
    except KeyError as e:
        st.error(f"Fehler beim Verarbeiten der Routenpunkte: {e}")

# Funktion zum Abrufen der gefilterten Daten
@st.cache_data
def load_filtered_data(maxspeed=None, street_type=None, surface_type=None):
    osm = pyrosm.OSM(file_path)
    cycle_net_berlin = osm.get_network(network_type="cycling")
    streets = cycle_net_berlin.copy()

    if maxspeed:
        streets = streets.loc[streets['maxspeed'] == maxspeed].copy()

    if street_type:
        streets = streets.loc[streets['highway'].isin(street_type)].copy()

    if surface_type:
        streets = streets.loc[streets['surface'].isin(surface_type)].copy()

    return streets

# Funktion zum Abrufen der OSM-Segmentinformationen
def fetch_osm_segment_info(route_data):
    osm_data = []
    try:
        berlin_osm = pyrosm.OSM(file_path)
        cycle_net_berlin = berlin_osm.get_network(network_type="cycling", extra_attributes=["highway"])

        for coord in route_data['LongLatPath']:
            lat, lon = map(float, coord.split(','))
            point = Point(lon, lat)
            mask = cycle_net_berlin['geometry'].apply(lambda x: x.contains(point)).values
            
            segment_info = cycle_net_berlin.loc[mask]
            if not segment_info.empty:
                osm_data.append(segment_info)

    except KeyError as e:
        st.error("Fehler: API-Antwortstruktur enthält keine 'LongLatPath'.")
    except Exception as e:
        st.error(f"Allgemeiner Fehler: {e}")

    if osm_data:
        osm_gdf = gpd.GeoDataFrame(pd.concat(osm_data, ignore_index=True))

        highways = osm_gdf[['geometry', 'highway']]
        highway_count = highways['highway'].value_counts(normalize=True)*100
        st.write("Verteilung der Straßentypen auf der Route:")
        st.write(highway_count)

        threshold = 1
        rare_highways = highway_count[highway_count < threshold]
        st.write("Seltene Straßentypen:")
        st.write(rare_highways)

        osm_gdf.loc[osm_gdf['highway'].isin(rare_highways.index), 'highway'] = 'highway_rare'

        return osm_gdf
    return gpd.GeoDataFrame()

# Funktion zum Erstellen einer Legende
def add_legend(m):
    legend_html = """
    <div style="
        position: fixed; 
        bottom: 10px; left: 10px; width: 150px; height: auto; 
        background: white; opacity: 0.8; padding: 10px; 
        font-size: 14px; z-index:9999; border:2px solid black;">
        <b>Legende</b><br>
        <i style="background: green; width: 20px; height: 20px; display: inline-block;"></i> Route<br>
        <i style="background: blue; width: 20px; height: 20px; display: inline-block;"></i> Gefilterte Straßen<br>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

# Pipeline-Funktion zum Kombinieren der Funktionen
def pipeline(start_address, end_address, maxspeed, street_type, surface_type):
    start_coords = get_coordinates(start_address)
    end_coords = get_coordinates(end_address)
    if None in start_coords or None in end_coords:
        st.error("Konnte die Koordinaten für eine der eingegebenen Adressen nicht ermitteln.")
        return

    st.write(f"Route von {start_address} nach {end_address}:")
    route_data = get_route(start_coords, end_coords)
    if route_data:
        m = folium.Map(location=[52.5200, 13.4050], zoom_start=12)

        # Füge gefilterte Daten zur Karte hinzu
        filtered_data = load_filtered_data(maxspeed=maxspeed, street_type=street_type, surface_type=surface_type)

        if filtered_data is not None and not filtered_data.empty:
            folium.GeoJson(
                filtered_data,
                name='Gefilterte Straßen',
                style_function=lambda x: {'color': 'blue', 'weight': 2},
                tooltip=folium.GeoJsonTooltip(fields=['name', 'maxspeed', 'highway', 'surface'])
            ).add_to(m)
        else:
            st.write("Keine gefilterten Daten vorhanden.")

        # Visualisiere die Route auf der Karte
        visualize_route(route_data, m)
        add_legend(m)  # Füge die Legende hinzu
        folium_static(m)
        
        osm_segment_info = fetch_osm_segment_info(route_data)
        if not osm_segment_info.empty:
            st.write(osm_segment_info[['highway']].dropna())
        else:
            st.write("Keine OSM-Segmentinformationen verfügbar.")
    else:
        st.error("Konnte die Route nicht abrufen.")

# Streamlit-App Setup
st.title("Berlin Fahrradroute Planung")

# Filter-Widgets
with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        maxspeed = st.selectbox('Höchstgeschwindigkeit:', options=[None, '30', '50', '80'])

    with col2:
        street_type = st.multiselect('Straßentyp', options=['primary', 'secondary', 'tertiary'])

    with col3:
        surface_type = st.multiselect('Oberflächenbeschaffenheit', options=['asphalt', 'paved', 'gravel'])

    start_address = st.text_input("Startadresse eingeben", value="Wildenbruchstraße 33, Berlin")
    end_address = st.text_input("Zieladresse eingeben", value="Rubensstr. 6, Berlin")

    if st.button("Route berechnen"):
        if start_address and end_address:
            pipeline(start_address, end_address, maxspeed, street_type, surface_type)
        else:
            st.error("Bitte sowohl Start- als auch Zieladresse eingeben.")
