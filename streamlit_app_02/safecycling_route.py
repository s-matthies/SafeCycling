import requests
import streamlit as st
import urllib.parse
import folium
from streamlit_folium import folium_static
import json

# Konfigurationen für die API und Pfad zur GeoJSON-Datei
API_URL = "https://api.bbbike.org/api/0.2/bbbike/"
API_ID = "smatthies"
GEOJSON_PATH = "../data/processed_data/simra_within_berlin.geojson"

# Funktion zur Geokodierung einer Adresse
def get_coordinates(address):
    """Verwende Nominatim, um Koordinaten für eine gegebene Adresse zu erhalten."""
    address_encoded = urllib.parse.quote(address)
    url = f"https://nominatim.openstreetmap.org/search?q={address_encoded}&format=json&addressdetails=1"
    headers = {
        "User-Agent": "DeinName <deine-email@example.com>"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            response_json = response.json()
            if response_json:
                lat = response_json[0].get('lat')
                lon = response_json[0].get('lon')
                if lat and lon:
                    return float(lat), float(lon)
                else:
                    st.error(f"Fehler: Keine Koordinaten in der Antwort für Adresse '{address}' gefunden.")
                    return None, None
            else:
                st.error(f"Keine Koordinaten für Adresse '{address}' gefunden.")
                return None, None
        except (ValueError, KeyError, IndexError) as e:
            st.error(f"Fehler beim Verarbeiten der Antwort für Adresse '{address}': {e}")
            return None, None
    else:
        st.error(f"Fehler beim Abrufen der Koordinaten für Adresse '{address}': HTTP {response.status_code}")
        return None, None

# Funktion zur Abrufung der Route über die BBBike API
def get_bbbike_route(start_coords, end_coords):
    """Fetch route from BBBike API using coordinates."""
    if not start_coords or not end_coords:
        st.error("Ungültige Start- oder Zielkoordinaten.")
        return None
    
    # API-Anfrage URL zusammenstellen
    url = (f"{API_URL}?appid={API_ID}"
           f"&startc_wgs84={start_coords[1]},{start_coords[0]}"
           f"&zielc_wgs84={end_coords[1]},{end_coords[0]}"
           f"&output_as=json")
    
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            data = response.json()
            st.write("Route erfolgreich abgerufen!")  # Debug-Ausgabe
            return data  # Rückgabe der JSON-Daten der Route
        except ValueError:
            st.error("Fehler beim Parsen der JSON-Antwort.")
            return None
    else:
        st.error(f"Fehler beim Abrufen der Route: {response.status_code}")
        return None

# Funktion zum Laden der Gefahrenpunkte aus einer GeoJSON-Datei
@st.cache_data
def load_dangerpoints():
    """Lade GeoJSON-Daten von einer lokalen Datei mit Gefahrenpunkten."""
    try:
        with open(GEOJSON_PATH, 'r') as file:
            geojson_data = json.load(file)
            st.write(f"Gefahrenpunkte erfolgreich geladen: {len(geojson_data['features'])} Punkte")  # Debug-Ausgabe
            return geojson_data
    except Exception as e:
        st.error(f"Fehler beim Laden der GeoJSON-Daten: {e}")
        return None

# Funktion zum Anzeigen der Route auf der Karte
def display_route_on_map(route_data, start_coords, end_coords, show_danger_points=False):
    """Visualize route on map and optionally add danger points."""
    m = folium.Map(location=start_coords, zoom_start=12)
    
    if route_data and 'LongLatPath' in route_data:
        points = [(float(coord.split(',')[1]), float(coord.split(',')[0])) for coord in route_data['LongLatPath']]
        folium.PolyLine(points, color='blue', weight=5).add_to(m)
        
        folium.Marker(location=points[0], popup="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(location=points[-1], popup="Ziel", icon=folium.Icon(color="red")).add_to(m)
    
    if show_danger_points:
        st.write("Gefahrenpunkte werden angezeigt...")  # Debug-Ausgabe
        geojson_data = load_dangerpoints()
        if geojson_data:
            folium.GeoJson(geojson_data, name="Gefahrenpunkte", style_function=lambda x: {'color': 'red', 'weight': 1}).add_to(m)
            st.write("Gefahrenpunkte auf der Karte hinzugefügt!")  # Debug-Ausgabe
        else:
            st.warning("Gefahrenpunkte konnten nicht geladen werden.")

    return m

# Streamlit App Benutzeroberfläche
st.title("SafeCycling 🚲 ")
st.subheader("Wie sicher ist deine gewählte Route?")
st.write("Fahrradfahren in Berlin kann gefährlich sein.")
st.write("Gib die Start- und Zieladresse ein, um deine Fahrradroute zu berechnen. "
         "Sobald die Route angezeigt wird, kannst du dir zusätzliche Informationen zur Straßenbeschaffenheit, Höchstgeschwindigkeit, Straßentyp und Gefahrenpunkten für deine Strecke ausgeben lassen.")

# Eingabefelder und Button werden in einem Container platziert
with st.container():
    st.write("**Start- und Zieladresse eingeben**")
    
    # Eingabefelder für Start- und Zieladresse (in einer Zeile)
    col1, col2 = st.columns(2)
    with col1:
        start_address = st.text_input("Startadresse eingeben:")
    with col2:
        end_address = st.text_input("Zieladresse eingeben:")

    # Button zur Berechnung der Route
    calculate_route = st.button("Route berechnen")

# Platzhalter für die Karte nach den Eingabefeldern platzieren
map_placeholder = st.empty()

# Initiale Karte anzeigen
default_coords = (52.5200, 13.4050)  # Berlin Mitte

# Wenn die Route nicht berechnet wird, zeige die initiale Karte an
if not calculate_route:
    initial_map = folium.Map(location=default_coords, zoom_start=12)
    folium_static(initial_map, height=500)

# Nach Klick auf "Route berechnen"
if calculate_route:
    if start_address and end_address:
        # Koordinaten abrufen
        start_coords = get_coordinates(start_address + ", Berlin, Germany")
        end_coords = get_coordinates(end_address + ", Berlin, Germany")
        
        if start_coords and end_coords:
            # Route von BBBike API abrufen
            route_data = get_bbbike_route(start_coords=start_coords, end_coords=end_coords)
            
            if route_data:
                # Zusätzliche Informationen (Checkboxen) **über der Karte anzeigen**
                st.write("**Zusätzliche Informationen zur Route**")
                col1, col2 = st.columns(2)
                with col1:
                    maxspeed = st.checkbox('Höchstgeschwindigkeit')
                    surface_type = st.checkbox('Oberflächenbeschaffenheit')
                with col2:
                    street_type = st.checkbox('Straßentyp')
                    accident_points = st.checkbox('Gefahrenpunkte')

                # Debug-Ausgabe für den Status der Checkboxen
                st.write(f"Gefahrenpunkte Checkbox aktiviert: {accident_points}")
                
                st.write("**Route auf der Karte anzeigen**")
                
                # Route auf der Karte darstellen
                route_map = display_route_on_map(route_data, start_coords, end_coords, show_danger_points=accident_points)
                
                # Initiale Karte im Platzhalter aktualisieren
                map_placeholder.empty()  # Lösche die initiale Karte
                folium_static(route_map, height=500)  # Zeige die Karte mit Route an
            else:
                st.error("Route konnte nicht abgerufen werden.")
        else:
            st.error("Fehler beim Abrufen der Koordinaten. Bitte überprüfen Sie die Adressen.")
    else:
        st.error("Bitte sowohl Start- als auch Zieladresse eingeben.")
