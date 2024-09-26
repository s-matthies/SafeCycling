# Idee des Projekts

Das Gefahrenpotential für Radfahrende im Berliner Straßenverkehr vorhersagen.


## Sprint 1: Datensätze und Verständnis

Ziel: Wir recherchieren verschiedene Datensätze, die für unser Projekt sinnvoll sein können.
Wir möchten mindestens drei verschiedene Datensätze finden und den grundlegenden Inhalt der Datensätze verstehen.  
Wir haben am Ende des Sprints ein besseres Verständnis für die Aufgabenstellung gewonnen und wie wir unsere Idee umsetzen könnten.

Welche Datensätze könnte man nutzen?

Ergebnis:
- SimRa - Beinnahunfälle 
- OSM  - Daten zu Strassenbeschaffenheit und Art der Strassen/ Radwege
- Berliner Datensatz - Fahrradunfälle Berlin
- Berliner Datensatz - Verkehrsdichte



## Sprint 2: Explorieren der Datensätze

Ziel: Wir möchten die Datensätze und ihre enthaltenen Daten beschaffen und analysieren. Auf dieser Grundlage wollen wir entscheiden, welche Datensätze wirklich sinnvoll sind für unser Projekt. Am Ende des Sprints wissen wir welche Datensätze wir nutzen.

Datenmenge groß genug?  
Welche Features genau enthalten?  
Fehlerhafte Daten?  
Welche Datensätze sind tatsächlich sinnvoll zu nutzen?  

- SimRa Datensatz 01  -->  [SimRa Analyse Teil 1](notebooks/simra/01_simra_data_analysis.ipynb), [SimRa Analyse Teil 2](notebooks/simra/02_simra_data_analysis.ipynb)
- SimRa Datensatz 02  -->  [SimRa Analyse](notebooks/simra/simra_data_all.ipynb)
- Berliner Datensatz - Unfälle -->  [Rad-Unfälle Berlin](notebooks/Radunfaelle_datensatz_extr.ipynb)
- Berliner Datensatz - Verkehrsdichte  -->  [Verkehrsdichte](notebooks/Verkehrsdichte/Stammdaten.ipynb)

Ergebnis: Wir arbeiten mit zwei Datensätzen weiter: SimRa Datensatz 02 und OSM 


## Sprint 3: Explorieren der OSM-Daten, Bereinigung der Datensätze OSM und SimRa

Ziel: Wir möchten die für uns relevanten aus OSM extrahieren, verstehen und bereinigen. Die SimRa-Daten wollen wir dementsprechend auch vorbereiten.
Am Ende des Sprints haben wir zwei Datensätze, in denen nur die relevanten Features vorhanden sind.

**Extrahieren der OSM-Daten**
- über overpass-turbo.eu ( nicht so gut)
- über Geofabrik 


**Explorieren und Bereinigen der Daten aus OSM**  

OSM -->   [OSM allg. Analyse](notebooks/osm/OSM_network_type_cycle_analyse1.ipynb)

- Welche Features sind enthalten?
- Features, die wir nutzen wollen:
    - Maxspeed  -->  [OSM maxspeed](notebooks/osm/osm_maxspeed.ipynb) und
      [OSM maxsped ohne "service" Straßen](notebooks/osm/osm_maxspeed_noservice.ipynb)
    - Surface -->   [OSM surface](notebooks/osm/osm_surface.ipynb) und
      [OSM surface ohne "service" Straßen](notebooks/osm/osm_surface_noservice.ipynb)
    - Type of Highway -->   [OSM highways](notebooks/osm/osm_highway.ipynb) und
      [OSM highways ohne "service" Straßen](notebooks/osm/osm_highway_no_service.ipynb)
    - Cycleway -->   [OSM cycleway](notebooks/osm/osm_cycleway_bicycle.ipynb)
    - ...
Analyse weiterer möglicher Features? -->  [OSM Featurecheck](notebooks/osm/osm_features_check.ipynb)



**Bereinigung der SimRA-Daten**

- SimRa -->  [SimRa](notebooks/simra/simra_data_all.ipynb)


Ergebnis: Wir haben einen sauberen SimRa-Datensatz und zwei saubere OSM-Datensätze (einen ohne und einen mit "service" Straßen)


## Sprint 4: Zusammenbringen der Datensätze und Zwischenpräsentation

Ziel: Wir verknüfen die Datensätze SimRa und OSM (einmal mit dem Straßentyp `service`und einmal ohne). Wir erstellen eine Präsentation unserer bisherigen Ergebnisse.

- vollständiger Datensatz -->  [SimRa+OSM](notebooks/joined_datasets/simra_plus_osm_all.ipynb)
- vollständiger Datensatz ohne "service" Straßen --> [SimRa+OSM ohne service](notebooks/joined_datasets/simra_osm_no_service_all.geojson)


  
- Zwischenpräsentation --> [Pdf](Zwischenpräsentation_IKT.pdf)

Ergebnis: Wir haben einen einzigen Datensatz, den wir für das Modeltraining nutzen werden.

## Sprint 5: Modelle trainieren

Ziel: Wir trainieren verschiedene Modelle und können am Ende eine Aussage darüber treffen, welches Modell am geeignesten ist für unsere Vorhersage.
Wir wissen, ob das Fehlen der sog. "service" Straßen eine Einfluss auf die Vorhersage hat.

- K-NN -->  [knn](notebooks/training/kNN__Min_max_Scaler.ipynb) und [knn ohne service](notebooks/training/kNN__Min_max_Scaler_noService.ipynb)
- Lineare Regression -->  [Lineare Regression](notebooks/training/lineareRegression_3.ipynb) und [Lineare Regression ohne Service](notebooks/training/lineareRegression_noService.ipynb)
- Decision Tree -->  [Decision Tree](notebooks/training/decision_tree/decision_trees.ipynb),
  [Decision Tree ohne service](notebooks/training/decision_tree/decision_trees_without_service.ipynb), 
- Random Forest -->  [Random Forest](notebooks/training/random_forest/random_forest_2.ipynb), 
[Random Forest ohne service](notebooks/training/random_forest/random_forest_noservice.ipynb)


Ergebnis: Es gibt kein Model, dass gute Vorhersage macht. Weitere Daten wären notwendig.

## Sprint 6: Zusammenfassung unserer Ergebnisse und Streamlit App

Ziel: Wir fassen unsere Ergebnisse in einem Dokument zusammen und erstellen eine Streamlit App

- Dokumentation:  --> [Pdf](Dokumentation_03.pdf)  

Bei der Umsetzung der Streamlit App haben wir verschiedene Ansätze verfolgt, nicht alle konnten wir erfolgreich zu Ende führen:

- Ausgabe von Fahradrouten (Rohentwurf, in Bearbeitung) siehe Verzeichnis streamlit_app --> [App mit Routenausgabe](streamlit_app) 

- **finale App**:  Visualisierung der Gefahrenpunkte und OSM Features auf der Berliner Karte --> [finale App](streamlit_app_02/safecycling.py)  

Ergebnis: Wir haben die Dokumentation und eine App erstellt.

