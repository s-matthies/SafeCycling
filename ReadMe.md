# SafeCycling: Prognose des Gefahrenpotenzials im Berliner Radverkehr

**SafeCycling** ist ein Machine-Learning-Projekt, das das Ziel verfolgt, das Gefahrenpotenzial für Radfahrende im Berliner Straßenverkehr zu prognostizieren. 

## Inhalt

1. [Projektbeschreibung](#projektbeschreibung)
2. [Vorgehensweise](#vorgehensweise)
3. [Installation](#installation)
4. [Technologien](#technologien)
5. [Verwendung](#verwendung)
6. [Streamlit App](#streamlit-app)
7. [Projektteam](Projektteam)
8. [Lizenz](#lizenz)

## Projektbeschreibung

Mithilfe von Daten aus dem [SimRa-Projekt](https://simra-project.github.io/) (Sicherheit im Radverkehr) und der OpenStreetMap (OSM) untersucht das Projekt eine mögliche Beziehung zwischen Verkehrsinfrastruktur und dem Auftreten von Beinaheunfällen.

Durch den Einsatz von Machine-Learning-Modellen wie k-Nearest Neighbors, linearer Regression, Decision Tree und Random Forest wird versucht, Gefahrenstellen auf Basis von Straßentypen, Oberflächenbeschaffenheit und Höchstgeschwindigkeit vorherzusagen.

Trotz vieler Herausforderungen, insbesondere durch unausgewogene Daten, bietet das Projekt wertvolle Einblicke in die Möglichkeiten und Grenzen der Vorhersage von Gefahrenpotenzialen im städtischen Radverkehr.

## Vorgehensweise

Für einen umfassenden Überblick über das Projekt verweisen wir auf die [Dokumentation](Dokumentation_03.pdf). Diese enthält detaillierte Informationen zu Zielen, Daten, Vorgehen und Ergebnissen.

Zusätzlich gibt es einen [Projektverlauf](projekt-verlauf.md), der die einzelnen Sprints sowie die verwendeten Notebooks auflistet. Hier findest du eine kurze Beschreibungen der durchgeführten Schritte.

## Installation

### 1. Voraussetzungen

- Python 3.12.6 (entwickelt und getestet), sollte aber auch mit niedrigeren Python 3.x-Versionen funktionieren
- Abhängigkeiten: Alle erforderlichen Pakete sind in der Datei `requirements.txt` aufgelistet

### 2. Schritte zur Installation

- Repository klonen: `https://gitlab.rz.htw-berlin.de/Sabine.Matthies/safecycling.git`

- Wechsel in das Verzeichnis des Projekts: `cd safecycling`

- Virtuelle Umgebung erstellen und aktivieren: `python -m venv venv`

  - `source venv/bin/activate` # Linux/Mac 

  - `source venv/Scripts/activate` # Windows

- Abhängigkeiten installieren: `pip install -r requirements.txt`


## Technologien

Das Projekt verwendet folgende Technologien und Bibliotheken:

- **Python**: Programmiersprache zur Datenanalyse und -verarbeitung
- **pandas**: Datenverarbeitung und -analyse
- **geopandas**: Arbeiten mit geospatialen Daten
- **scikit-learn**: Maschinelles Lernen zur Analyse von Mustern
- **matplotlib**: Visualisierung von Daten
- **Streamlit**: Erstellung eines interaktiven Dashboards zur Visualisierung
- **Jupyter Notebook**: Interaktive Entwicklungsumgebung

## Verwendung

#### 1. Starten der Analyse (Jupyter Notebook):
- Öffne das Projektverzeichnis und starte Jupyter Notebook: `jupyter notebook`

- Die Notebooks im Ordner `notebooks` enthalten unter anderem die Analysen der einzelnen Datensätze, das Modelltraining und die jeweiligen Ergebnisse. Führe die jeweiligen Skripte für den gewünschten Schritt der Datenanalyse und Modellentwicklung aus.

#### 2. Starten des Streamlit Dashboards:
- Navigiere in folgendes Verzeichnis: `cd streamlit_app_02`

- Um die interaktive Visualisierung zu starten, führe folgenden Befehl aus: `streamlit run safecycling.py`

- Das Dashboard wird im Browser geöffnet.

## Streamlit App 

- **Link zur App**: [Streamlit App](streamlit_app_02/safecycling.py)
- Die Streamlit-App visualisiert die gesammelten Daten aus OSM (Straßentyp, Höchstgeschwindigkeit, Straßenbelag) sowie die Gefahrenpunkte für Radfahrende in Berlin. Nutzer*innen können interaktiv verschiedene Features erkunden und die bisher erhobenen Gefahrenpunkte durch das SimRa-Projekt auf einer Karte einsehen.

## Projektteam

- Nicole Driebe
- Lisa Rübel
- Sabine Matthies

## Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](https://opensource.org/licenses/MIT) lizenziert.
