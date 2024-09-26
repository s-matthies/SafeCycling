import streamlit as st
import folium
from streamlit_folium import st_folium
from pyrosm import OSM
import geopandas as gpd
import requests

# Funktion zum Laden und Filtern der Daten
@st.cache_data
def load_filtered_data(maxspeed=None, street_type=None, surface_type=None):
    osm = OSM('../data/berlin-latest.osm.pbf')
    cycle_net_berlin = osm.get_network(network_type="cycling")
    streets = cycle_net_berlin.copy()

    # Debug-Ausgabe für das Daten-Shape
    st.write("Ungefilterte Daten Shape:", streets.shape)

    if maxspeed:
        st.write(f"Filtern nach maxspeed={maxspeed}")
        streets = streets.loc[streets['maxspeed'] == maxspeed].copy()

    if street_type:
        st.write(f"Filtern nach street_type={street_type}")
        streets = streets.loc[streets['highway'].isin(street_type)].copy()

    if surface_type:
        st.write(f"Filtern nach surface_type={surface_type}")
        streets = streets.loc[streets['surface'].isin(surface_type)].copy()

    # Debug-Ausgabe für das gefilterte Daten-Shape
    st.write("Gefilterte Daten Shape:", streets.shape)

    return streets

# Funktion zum Laden der Unfallorte aus einer GeoJSON-Datei
@st.cache_data
def load_accident_data(filepath):
    accidents = gpd.read_file(filepath)
    # Filtere nur Unfälle, bei denen incidents > 0 ist
    accidents_filtered = accidents[accidents['incidents'] > 0]
    
    return accidents_filtered

# Funktion zur Berechnung der Route mit der BBBike API
def calculate_route(start_coords, end_coords, api_key):
    url = "https://api.bbbike.org/api/0.2/bbbike/"
    params = {
        'start': f'{start_coords[0]},{start_coords[1]}',
        'end': f'{end_coords[0]},{end_coords[1]}',
        'key': api_key
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Funktion zum Hinzufügen der Route zur Karte
def add_route_to_map(map_object, route_data):
    folium.PolyLine(
        locations=route_data['coordinates'],  # Stellen sicher, dass die Koordinaten im richtigen Format vorliegen
        color='green',
        weight=4
    ).add_to(map_object)

# Initialisiere Session State für die Filter, die Auswahlfelder und die Route
if 'maxspeed' not in st.session_state:
    st.session_state['maxspeed'] = None
if 'street_type' not in st.session_state:
    st.session_state['street_type'] = []
if 'surface_type' not in st.session_state:
    st.session_state['surface_type'] = []
if 'filtered_data' not in st.session_state:
    st.session_state['filtered_data'] = None
if 'show_accidents' not in st.session_state:
    st.session_state['show_accidents'] = False
if 'accident_data' not in st.session_state:
    st.session_state['accident_data'] = None
if 'route_data' not in st.session_state:
    st.session_state['route_data'] = None

# Streamlit Interface
st.title('SafeCycling')

# Filter und Button in einem Container über der Karte
with st.container():
    # Widgets für Filter (in einer Zeile)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.session_state['maxspeed'] = st.selectbox(
            'Höchstgeschwindigkeit:', 
            options=[None, '30', '50', '80'], 
            index=0 if st.session_state['maxspeed'] is None else [None, '30', '50', '80'].index(st.session_state['maxspeed'])
        )


    with col2:
        st.session_state['street_type'] = st.multiselect(
            'Straßentyp', 
            options=['primary', 'secondary', 'tertiary'], 
            default=st.session_state['street_type']
        )


    with col3:
        st.session_state['surface_type'] = st.multiselect(
            'Oberflächenbeschaffenheit', 
            options=['asphalt', 'paved', 'gravel'], 
            default=st.session_state['surface_type']
        )
    # Checkbox zum Anzeigen der Unfallorte
    st.session_state['show_accidents'] = st.checkbox('Gefahrenpunkte anzeigen', value=st.session_state['show_accidents'])

    # Eingabefelder für Start- und Endkoordinaten
    col4, col5 = st.columns(2)

    with col4:
        start_coords = st.text_input('Startkoordinaten (lat, lon)', '52.5200, 13.4050')

    with col5:
        end_coords = st.text_input('Zielkoordinaten (lat, lon)', '52.5200, 13.4060')

    # Buttons in einer Zeile mit schmaleren Spalten
    col_btn1, col_btn2 = st.columns([1, 3])
    
    # Der Button für das Anwenden des Filters (links)
    with col_btn1:
        apply_filter = st.button('Filter anwenden', key='filter_button')
    
    # Der Button für das Zurücksetzen des Filters (rechts)
    with col_btn2:
        reset_filter = st.button('Filter zurücksetzen', key='reset_button')

    # Button zur Berechnung der Route
    calculate_route_button = st.button('Route berechnen')

# Überprüfe, ob mindestens ein Filter ausgewählt wurde
is_filter_selected = (
    st.session_state['maxspeed'] is not None or 
    st.session_state['street_type'] or 
    st.session_state['surface_type']
)

# Erstelle eine Karte
m = folium.Map(location=[52.5200, 13.4050], zoom_start=12)

# Filter anwenden
if apply_filter:
    if is_filter_selected:
        st.write("Filter angewendet.")
        st.session_state['filtered_data'] = load_filtered_data(
            maxspeed=st.session_state['maxspeed'], 
            street_type=st.session_state['street_type'], 
            surface_type=st.session_state['surface_type']
        )
    else:
        st.warning("Bitte wähle mindestens einen Filter aus, bevor du den Filter anwendest.")

# Filter zurücksetzen, wenn der Button geklickt wird
if reset_filter:
    st.write("Filter zurückgesetzt.")
    st.session_state['maxspeed'] = None  # Setze die maxspeed zurück
    st.session_state['street_type'] = []  # Setze den Straßentyp zurück
    st.session_state['surface_type'] = []  # Setze die Oberflächenbeschaffenheit zurück
    st.session_state['filtered_data'] = None 
    st.session_state['show_accidents'] = False
    st.session_state['route_data'] = None  # Setze die Route zurück

# Berechne die Route, wenn der Button geklickt wird
if calculate_route_button:
    try:
        start_lat, start_lon = map(float, start_coords.split(','))
        end_lat, end_lon = map(float, end_coords.split(','))
        st.session_state['route_data'] = calculate_route((start_lat, start_lon), (end_lat, end_lon), 'smatthies')
        st.write("Route berechnet.")
    except Exception as e:
        st.error(f"Fehler bei der Routenberechnung: {e}")

# **GeoJson Layer hinzufügen, wenn gefilterte Daten vorhanden sind**
if st.session_state['filtered_data'] is not None and not st.session_state['filtered_data'].empty:
    st.write("Gefilterte Daten werden der Karte hinzugefügt.")
    folium.GeoJson(
        st.session_state['filtered_data'],
        name='Gefilterte Straßen',
        style_function=lambda x: {'color': 'blue', 'weight': 2},
        tooltip=folium.GeoJsonTooltip(fields=['name', 'maxspeed', 'highway', 'surface'])
    ).add_to(m)

# Unfallorte hinzufügen, wenn die Checkbox aktiviert ist
if st.session_state['show_accidents']:
    if st.session_state['accident_data'] is None:
        # Lade die GeoJSON-Datei mit den Unfallorten
        st.session_state['accident_data'] = load_accident_data('../data/processed_data/simra_within_berlin.geojson')

    # **GeoJson Layer für die Unfallorte hinzufügen**
    if st.session_state['accident_data'] is not None:
        folium.GeoJson(
            st.session_state['accident_data'],
            name='Beinahe-Unfallorte',
            style_function=lambda x: {'color': 'red', 'weight': 1},
            tooltip=folium.GeoJsonTooltip(fields=['incidents', 'rides', 'score'])
        ).add_to(m)

# Route zur Karte hinzufügen
if st.session_state['route_data'] is not None:
    add_route_to_map(m, st.session_state['route_data'])

# Layer Control hinzufügen (unabhängig von Filterung)
folium.LayerControl().add_to(m)

st_folium(m, width=725)
