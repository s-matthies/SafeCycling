import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import random 


# Favicon und Titel setzen
st.set_page_config(
    page_title="SafeCycling", 
    page_icon="favicon.ico"  # Pfad zu deinem Favicon
)

# CSS für die Farbänderung hinzufügen
st.markdown(
    """
    <style>
    /* Auswahlboxen anpassen */
    div[data-baseweb="select"] > div {
        /*background-color: #76B900 !important;  Hintergrundfarbe */
        /*border: 1px solid #76B900 !important;  Rahmenfarbe */
        color: grey !important;  /* Textfarbe */
    }

    /* Rahmen und Schatten-Effekt, wenn die Auswahlbox fokussiert oder ausgewählt wird */
    div[data-baseweb="select"] > div:focus-within {
        border-color: #76B900 !important; /* Rahmenfarbe bei Fokus */
        /*box-shadow: 0 0 10px rgba(72, 187, 120, 0.5);  Grüner Schein bei Fokus */
    }

    /* Checkbox anpassen */
    div[data-baseweb="checkbox"] > div {
        /* background-color: #76B900 !important; /* Hintergrundfarbe */
        border: 1px solid #76B900 !important; /* Rahmenfarbe */
    }

    /* Angepasstes Häkchen für Checkbox */
    div[data-baseweb="checkbox"] input:checked + div {
        background-color: #76B900 !important; /* Farbe des markierten Kästchens */
        border: 1px solid #76B900 !important; /* Rahmenfarbe für markiertes Kästchen */
    }

/*-------------------------------------------*/
    .stMultiSelect .stMultiSelect__option--selected {
        background-color: #76B900 !important; /* Hellgrün für ausgewählte Elemente */
        color: white !important; /* Textfarbe */
    }


/*-------------------------------------------*/

    /* Standard-Stil für die Buttons */
    button[kind="secondary"], button[kind="primary"] {
        /*background-color: #76B900 !important;  Hellgrün für den Button-Hintergrund */
        border: 2px solid #76B900 !important;  
        color: #76B900 !important;  
        border-radius: 8px !important; /* Abgerundete Ecken */
        padding: 0.5em 1em !important; /* Polsterung des Buttons */
        transition: box-shadow 0.3s ease, transform 0.3s ease; /* Übergänge für Schatten und Transformation */
    }

    /* Effekt beim Hover (Maus über dem Button) */
    button[kind="secondary"]:hover, button[kind="primary"]:hover {
        /* background-color: #58a600 !important; Dunkleres Grün bei Hover */
        border-color: #76B900 !important; /* Dunklerer Rand bei Hover */
        /* box-shadow: 0 4px 8px rgba(72, 187, 120, 0.4); Schatteneffekt bei Hover */
        transform: translateY(-2px); /* Leichtes Anheben des Buttons bei Hover */
    }

    /* Effekt beim Klicken auf den Button */
    button[kind="secondary"]:active, button[kind="primary"]:active {
        background-color: #76B900 !important; 
        color: white !important; 
        /* border-color: #2f855a !important; Dunklerer Rand bei Klick */
        /*box-shadow: 0 2px 4px rgba(72, 187, 120, 0.5);  Leichter Schatten bei Klick */
        transform: translateY(0px); /* Button senkt sich wieder bei Klick */
    }

    /* Effekt wenn der Button fokussiert ist (z.B. nach Tab-Klick) */
    button[kind="secondary"]:focus, button[kind="primary"]:focus {
        outline: none !important; /* Entfernt die Standard-Fokusumrandung */
        /* box-shadow: 0 0 10px rgba(72, 187, 120, 0.5) !important;  Grüner Schattenschein bei Fokus */
    }

    
    
    </style>
    """,
    unsafe_allow_html=True
)


################################################################################################

# Funktion zum Laden der GeoJSON-Daten
@st.cache_data
def load_data_from_geojson():
    # Lade GeoJSON-Daten für maxspeed, surface und highway
    streets_maxspeed = gpd.read_file('../data/processed_data/cycle_net_berlin_cleaned_maxspeed.geojson')
    streets_surface = gpd.read_file('../data/processed_data/cycle_net_berlin_cleaned_surface.geojson')
    streets_highway = gpd.read_file('../data/processed_data/filtered_osm_highway_v1.geojson')

    # Kombiniere die Daten durch spatial join oder merge, falls notwendig
    # Annahme: alle GeoJSONs haben dieselbe Geometrie
    streets = streets_maxspeed.merge(streets_surface[['geometry', 'surface_category']], on='geometry', how='left')
    streets = streets.merge(streets_highway[['geometry', 'highway']], on='geometry', how='left')

    return streets

# Funktion zum Laden und Filtern der Daten
@st.cache_data
def load_filtered_data(maxspeed=None, street_type=None, surface_type=None):
    streets = load_data_from_geojson()

    # Debug-Ausgabe für das Daten-Shape
    #st.write("Ungefilterte Daten Shape:", streets.shape)

    if maxspeed:
        #st.write(f"Filtern nach maxspeed={maxspeed}")
        streets = streets.loc[streets['maxspeed_category'] == maxspeed].copy()

    if street_type:
        #st.write(f"Filtern nach street_type={street_type}")
        # Konvertieren der Auswahl zurück zu OSM-Namen
        selected_street_types = [reverse_street_type_translation[st] for st in street_type if st in reverse_street_type_translation]
        streets = streets.loc[streets['highway'].isin(selected_street_types)].copy()

    if surface_type:
        #st.write(f"Filtern nach surface_type={surface_type}")
        # Konvertieren der Auswahl zurück zu OSM-Namen
        selected_surface_types = [reverse_surface_type_translation[st] for st in surface_type if st in reverse_surface_type_translation]
        streets = streets.loc[streets['surface_category'].isin(selected_surface_types)].copy()  # Hier die Korrektur


    # Debug-Ausgabe für das gefilterte Daten-Shape
    #st.write("Gefilterte Daten Shape:", streets.shape)

    return streets


# Funktion zum Laden der Unfallorte aus einer GeoJSON-Datei
@st.cache_data
def load_accident_data(filepath):
    accidents = gpd.read_file(filepath)
    # Filtere nur Unfälle, bei denen incidents > 0 ist
    accidents_filtered = accidents[accidents['incidents'] > 0]
    
    return accidents_filtered


# Lade die Straßen-Daten und extrahiere eindeutige Werte für die Filter-Optionen
streets_data = load_data_from_geojson()

# Eindeutige Werte für die Filteroptionen extrahieren
available_maxspeed = streets_data['maxspeed_category'].dropna().unique().tolist()
available_street_type = streets_data['highway'].dropna().unique().tolist()
available_surface_type = streets_data['surface_category'].dropna().unique().tolist()

# Initialisiere Session State für die Filter und die Auswahlfelder
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

#------streets-----------------------------------------------
# Dictionary für highway
street_type_translation = {
    'primary': 'Hauptverkehrsstraße',
    'secondary': 'Nebenstraße',
    'tertiary': 'Verbindungsstraße',
    'residential': 'Wohngebietsstraße',
    'living_street': 'verkehrsberuhigter Bereich',
    'footway': 'Gehweg',
    'cycleway': 'Radweg',
    'highway_rare': 'sonstige Straßen',
    'track': 'Feld-/Waldweg',
    'path': 'schmaler Weg',
    'service': 'Erschließungsweg (Toreinfahrt)',
}

# Umkehrung des Übersetzungs-Dictionaries highway
reverse_street_type_translation = {v: k for k, v in street_type_translation.items()}

desired_street_order = [
    'Hauptverkehrsstraße',
    'Nebenstraße',
    'Verbindungsstraße',
    'Wohngebietsstraße',
    'verkehrsberuhigter Bereich',
    'Gehweg',
    'Radweg',
    'Feld-/Waldweg',
    'schmaler Weg',
    'Erschließungsweg (Toreinfahrt)',
    'sonstige Straßen',
]


#street_colors = {
#    'primary': 'blue',
#    'secondary': 'green',
#    'tertiary': 'orange',
#    'residential': 'yellow',
#    'living_street': 'pink',
#    'footway': 'purple',
#    'cycleway': 'cyan',
#    'track': 'brown',
#    'path': 'grey',
#    'service': 'lightblue',
#    'highway_rare': 'lightgreen',
#}

#------surface------------------------------------------------------
# Dictionary für surface
surface_type_translation = {
    'asphalt': 'Asphalt',
    'unpaved': 'kein Straßenbelag',
    'concrete': 'Beton',
    'sett': 'grob gepflastert',
    'paving_stone': 'gepflastert',
}

# Umkehrung des Übersetzungs-Dictionaries highway
reverse_surface_type_translation = {v: k for k, v in surface_type_translation.items()}

desired_surface_order = [
    'Asphalt',
    'Beton',
    'gepflastert',
    'grob gepflastert',
    'kein Straßenbelag',
]


#surface_colors = {
#   'asphalt': 'darkgrey',
#   'unpaved': 'beige',
#   'concrete': 'lightgrey',
#   'sett': 'saddlebrown',
#   'paving_stone': 'lightslategray',
#}

messages = [
    "Tolle Auswahl!",
    "Super Auswahl!",
    "Interessante Auswahl!",
    "Gute Auswahl!"
]

################################################################################################

# Streamlit Interface
#st.title('SafeCycling 🚲')

col1, col2 = st.columns([0.35, 0.65])  

with col1:
    
    # HTML-Markup für den Titel mit Farbe
    st.markdown(
        """
        <div class="title-text" style="color: #76B900; font-size: 48px; font-weight: bold;">
            SafeCycling
        </div>
        """, unsafe_allow_html=True
    )

with col2:
    st.image("bike3.png", width=80)

st.write("Für unser Projekt SafeCycling haben wir die Straßen Berlins, die für Radfahrende geeignet sind, untersucht. Dazu haben wir Daten aus Open-Street-Map benutzt.")
st.write("Schau dir gern an, welche Straßen Radfahrende in Berlin nutzen können und filtere nach ihrer Oberflächenbeschaffenheit oder Höchstgeschwindigkeit. Außerdem kannst du dir sog. Gefahrenpunkte ausgeben lassen. Das sind Stellen, die von anderen Radfahrenden als solche eingestuft worden sind, weil sie dort schon in gefährliche Situationen geraten sind. Diese Informationen haben wir aus dem SimRa-Datensatz (Sicherheit im Radverkehr).  ")
st.write("Viel Spaß!")
st.write("")
st.write("")

# Filter und Button in einem Container über der Karte
with st.container():
    # Widgets für Filter (in einer Zeile)
    col1, col2, col3 = st.columns(3)

    with col1:
        # Sortiere die available_maxspeed Werte numerisch
        available_maxspeed_sorted = sorted(available_maxspeed, key=lambda x: int(x))  # Konvertiere zu int für korrekte Sortierung
    
        st.session_state['maxspeed'] = st.selectbox(
            'Höchstgeschwindigkeit (blau)', 
            options=[None] + available_maxspeed_sorted,  # Dynamisch verfügbare und sortierte Werte laden
            index=0 if st.session_state['maxspeed'] is None else available_maxspeed_sorted.index(st.session_state['maxspeed']) + 1
        )


    with col2:
        # Liste der übersetzten Straßentypen
        translated_street_types = [street_type_translation[st] for st in available_street_type if st in street_type_translation]
    
        # Sortiere die translated_street_types basierend auf der gewünschten Reihenfolge
        translated_street_types_sorted = sorted(translated_street_types, key=lambda x: desired_street_order.index(x) if x in desired_street_order else len(desired_street_order))
    
        st.session_state['street_type'] = st.multiselect(
            'Straßentyp (gelb)',
            options=translated_street_types_sorted,  # Zeige die sortierten Werte an
            default=[street_type_translation[st] for st in st.session_state['street_type'] if st in street_type_translation]
        )

    with col3:
        # Liste der übersetzten surface-typen
        translated_surface_types = [surface_type_translation[st] for st in available_surface_type if st in surface_type_translation]
        
        # Sortiere die translated_surface_types basierend auf der gewünschten Reihenfolge
        translated_surface_types_sorted = sorted(translated_surface_types, key=lambda x: desired_surface_order.index(x) if x in desired_surface_order else len(desired_surface_order))
    
        st.session_state['surface_type'] = st.multiselect(
            'Oberflächenbeschaffenheit (schwarz)', 
            options=translated_surface_types_sorted,  # Dynamisch verfügbare und sortierte Werte laden
            default=[surface_type_translation[st] for st in st.session_state['surface_type'] if st in surface_type_translation]

        )



    
    # Checkbox zum Anzeigen der Unfallorte
    st.session_state['show_accidents'] = st.checkbox('Gefahrenpunkte anzeigen', value=st.session_state['show_accidents'])

    # Buttons in einer Zeile mit schmaleren Spalten
    col_btn1, col_btn2 = st.columns([1, 3])
    
    # Der Button für das Anwenden des Filters (links)
    with col_btn1:
        apply_filter = st.button('Filter anwenden', key='filter_button')
    
    # Der Button für das Zurücksetzen des Filters (rechts)
    with col_btn2:
        reset_filter = st.button('Filter zurücksetzen', key='reset_button')

# Überprüfe, ob mindestens ein Filter ausgewählt wurde
is_filter_selected = (
    st.session_state['maxspeed'] is not None or 
    st.session_state['street_type'] or 
    st.session_state['surface_type']
)

# Erstelle eine Karte
m = folium.Map(location=[52.5200, 13.4050], zoom_start=12)

if apply_filter:
    if is_filter_selected:
        st.write(random.choice(messages))
        st.write("Hab einen Moment Geduld, denn das Laden der Daten dauert ein wenig.")
        st.session_state['filtered_data'] = load_filtered_data(
            maxspeed=st.session_state['maxspeed'], 
            street_type=st.session_state['street_type'], 
            surface_type=st.session_state['surface_type']
        )
    else:
        st.warning("Bitte wähle mindestens eine der drei obigen Optionen aus, bevor du den Filter anwendest.")

# Filter zurücksetzen, wenn der Button geklickt wird
if reset_filter:
    st.write("Filter zurückgesetzt.")
    st.session_state['maxspeed'] = None  # Setze die maxspeed zurück
    st.session_state['street_type'] = []  # Setze den Straßentyp zurück
    st.session_state['surface_type'] = []  # Setze die Oberflächenbeschaffenheit zurück
    st.session_state['filtered_data'] = None 
    st.session_state['show_accidents'] = False
    

# **GeoJson Layer hinzufügen, wenn gefilterte Daten vorhanden sind**
if st.session_state['filtered_data'] is not None and not st.session_state['filtered_data'].empty:
    st.write("")
    st.write("")
    # Informationen zu gefilterten Daten anzeigen
    total_streets = streets_data.shape[0]  # Gesamte Straßen vor dem Filtern
    filtered_streets_count = st.session_state['filtered_data'].shape[0]
    
    # Liste für die Teile der Ausgabe
    output_parts = []
    
    # Prüfen, ob maxspeed ausgewählt wurde
    if st.session_state['maxspeed'] is not None:
        output_parts.append(f" haben eine Höchstgeschwindigkeit von {st.session_state['maxspeed']} km/h")
    
    # Prüfen, ob surface_type ausgewählt wurde
    if st.session_state['surface_type']:
        output_parts.append(f"haben eine Oberflächenbeschaffenheit von {' oder '.join(st.session_state['surface_type'])}")
    
    # Prüfen, ob street_type ausgewählt wurde
    if st.session_state['street_type']:
        output_parts.append(f"sind vom Typ {' oder '.join(st.session_state['street_type'])}")
    
    # Funktion zum Formatieren der Zahlen
    def format_number(num):
        return f"{num:,}".replace(",", ".")
    
    # Zusammenstellen der finalen Ausgabe
    if output_parts:
        output_sentence = " und ".join(output_parts)
        st.write(f"{format_number(filtered_streets_count)} von {format_number(total_streets)} Straßen in Berlin {output_sentence}.")
    else:
        st.write(f"Von {format_number(total_streets)} Straßen in Berlin haben {format_number(filtered_streets_count)} Straßen keine spezifischen Filter ausgewählt.")


    # Überprüfe, ob eine Auswahl für maxspeed, street_type oder surface_type getroffen wurde
    if st.session_state['maxspeed'] is not None:
        # Füge die GeoJSON-Daten für maxspeed hinzu
        folium.GeoJson(
            st.session_state['filtered_data'],
            name='Maxspeed',
            style_function=lambda feature: {
                'color': 'blue',  # Farbe für maxspeed
                'weight': 5,
                'opacity': 0.4 
            },
            tooltip=folium.GeoJsonTooltip(fields=['maxspeed_category', 'highway', 'surface_category'])
        ).add_to(m)

    if st.session_state['street_type']:  # Wenn mindestens ein Straßentyp ausgewählt ist
        # Füge die GeoJSON-Daten für street_type hinzu
        folium.GeoJson(
            st.session_state['filtered_data'],
            name='Gefilterte Straßen',
            style_function=lambda feature: {
                'color': 'yellow',  # oder eine spezifische Farbe für den Straßentyp
                'weight': 3,
                'opacity': 0.6 
            },
            tooltip=folium.GeoJsonTooltip(fields=['highway', 'surface_category'])
        ).add_to(m)

    if st.session_state['surface_type']:  # Wenn mindestens ein Oberflächentyp ausgewählt ist
        # Füge die GeoJSON-Daten für surface_type hinzu
        folium.GeoJson(
            st.session_state['filtered_data'],
            name='Oberflächenbeschaffenheit',
            style_function=lambda feature: {
                'color': 'black',  # Farbe für Oberflächen
                'weight': 1,
            },
            tooltip=folium.GeoJsonTooltip(fields=['surface_category'])
        ).add_to(m)
#else:
#    st.write("Keine Daten nach dem Filter übrig oder es wurden noch keine Filter angewendet.")



# Unfallorte hinzufügen, wenn die Checkbox aktiviert ist
if st.session_state['show_accidents']:
    if st.session_state['accident_data'] is None:
        # Lade die GeoJSON-Datei mit den Unfallorten
        st.session_state['accident_data'] = load_accident_data('../data/processed_data/simra_within_berlin.geojson')

    # **GeoJson Layer für die Unfallorte hinzufügen**
    if st.session_state['accident_data'] is not None:
        def style_function(feature):
            score = feature['properties']['score']  # Zugriff auf den Score-Wert
            if score > 0.1:
                return {'color': 'red', 'weight': 4, 'fillColor': 'red'}  # Anpassungen bei Score > 0.02
            else:
                return {'color': 'brown', 'weight': 1}  
        st.write("Gefahrenpunkte: Besonders gefährliche Bereiche sind rot gekennzeichnet, alle anderen braun.")

        folium.GeoJson(
            st.session_state['accident_data'],
            name='Beihnahe-Unfallorte',
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(fields=['incidents', 'rides', 'score'])
        ).add_to(m)
         

# Layer Control hinzufügen (unabhängig von Filterung)
folium.LayerControl().add_to(m)

# Karte anzeigen
st_folium(m, width=725)

