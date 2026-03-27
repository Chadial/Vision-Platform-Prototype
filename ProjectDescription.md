# Projektbeschreibung – Modulare Vision-Plattform für Kamerastream, Fokusbewertung und bildbasierte Rissverfolgung

## 1. Kurzbeschreibung

Ziel des Projekts ist die Entwicklung einer modularen Bildverarbeitungs- und Kameraplattform zur Aufnahme, Anzeige, Analyse und Weiterverarbeitung von Livebilddaten. Die Plattform soll sowohl als prototypisches Entwicklungswerkzeug als auch als Grundlage für spätere produktionsnähere Anwendungen dienen.

Im Zentrum stehen folgende Funktionen:

- Initialisierung und Parametrierung einer Kamera
- kontinuierlicher Kamerastream mit Livebildanzeige
- Speicherung von Einzelbildern oder Bildfolgen in definierten Intervallen
- interaktive Bildanzeige mit Overlays und Werkzeugen
- globale und lokale Fokusbewertung in definierbaren ROI-Masken
- Auswahl unterschiedlicher Fokusmetriken
- vorbereitende und perspektivisch direkte Kanten- bzw. Rissspitzenerkennung
- Bereitstellung von Analysewerten über definierte Schnittstellen für andere Anwendungen
- spätere Anbindung an Aktorik, z. B. Linearachsen oder Z-Nachführung

Die Plattform soll zunächst prototypisch mit Python aufgebaut werden, aber architektonisch so strukturiert sein, dass ein späterer Transfer zentraler Komponenten nach C# mit möglichst geringem Reibungsverlust möglich ist.

---

## 2. Ausgangslage und Motivation

Aktuell bestehen bereits Teilfunktionalitäten in getrennten oder historisch gewachsenen Ansätzen. Dazu gehören insbesondere ein bestehender Kamerastream mit Livebildanzeige sowie Erfahrung mit ROI-basierter Fokusbewertung über Laplace-Methoden in Drittsoftware. Zusätzlich besteht Interesse, OpenCV-basierte Edge-Detection-Ansätze zu erproben, um damit perspektivisch eine Rissspitze oder andere relevante Kantenmerkmale im Bild zu detektieren.

Die Motivation für das Gesamtprojekt ergibt sich aus mehreren Punkten:

- vorhandene Drittsoftware ist funktional begrenzt oder nicht flexibel genug
- Fokusbewertung soll gezielt auf die spätere Kanten- oder Rissdetektion abgestimmt werden
- Bildanzeige und Analyse sollen stärker unter eigener Kontrolle stehen
- interaktive Werkzeuge wie ROI-Masken, Crosshair, Hilfspunkte und Overlays sollen flexibel kombinierbar sein
- Analysewerte sollen nicht nur visualisiert, sondern auch extern nutzbar gemacht werden
- langfristig soll eine Rückkopplung an Bewegungssysteme oder Autofokusmechanismen möglich werden
- der Prototyp soll sowohl Echtzeit- als auch Postprocess-Szenarien unterstützen
- die Architektur soll nicht in einer reinen Python-Prototyplogik verharren, sondern spätere Desktop-, Web- und C#-Varianten vorbereiten

Das Projekt entwickelt sich damit von einem isolierten Kamera- oder Bildverarbeitungstool hin zu einer modularen Plattform mit mehreren Teilprojekten, gemeinsamen Kernmodulen und unterschiedlichen Frontends.

---

## 3. Projektziele

### 3.1 Fachliche Ziele

- Aufbau einer durchgängigen Pipeline von Kameraaufnahme bis Bildanalyse
- Bewertung der Bildschärfe bzw. des Fokus anhand globaler und lokaler Bildmetriken
- interaktive Definition von ROI-Masken direkt in der Bildanzeige
- Unterstützung mehrerer ROI-Typen:
  - Rechteck
  - Ellipse
  - Freihandmaske
- Untersuchung und prototypische Umsetzung eines kantenbasierten Ansatzes zur Rissspitzen- oder Strukturdetektion
- Anzeige relevanter Analyseergebnisse im Bild oder in ergänzenden Panels
- Bereitstellung der Ergebnisse für nachgelagerte Verarbeitung oder externe Systeme

### 3.2 Technische Ziele

- modularer Aufbau mit klar trennbaren Kernkomponenten
- saubere Trennung von UI, Analysekern, Hardwarezugriff und Schnittstellen
- Kompatibilität mit bestehendem Kamerastream
- Eignung für Livebetrieb, Snapshot-Betrieb und Offline-Auswertung
- Prototyping zunächst in Python, aber strukturell C#-kompatibel
- Mehrfachverwendung zentraler Kernlogik in unterschiedlichen Frontends
- Möglichkeit zur späteren API-Anbindung und Automatisierung

### 3.3 Langfristige Ziele

- Ausbau zu einer Desktop-Anwendung mit robusterer UI
- zusätzliche Webstream-/Browser-basierte Darstellung
- mobile oder tabletbasierte Ansichten
- Bereitstellung von Analysefeeds für externe Systeme
- automatische Nachführung bei Drift oder Fokusverlust
- Anbindung an Linearbewegung, Autofokus oder Z-Kompensation
- gemeinsame Plattform für Live-Analyse und Postprocessing

---

## 4. Nicht-Ziele / Abgrenzung

Folgende Punkte sind derzeit **nicht** primäre Ziele der ersten Ausbaustufe:

- vollständige sofortige Produktreife
- direkte Implementierung aller Frontends gleichzeitig
- vollständige Hard-Real-Time-Regelung
- endgültige Festlegung auf eine einzige GUI-Technologie
- KI-basierte oder datengetriebene Rissdetektion in der ersten Phase
- umfassende Multi-User- oder Cloud-Infrastruktur
- vollständige Produktionsintegration aller Hardwarekopplungen in der ersten Stufe

Das Projekt wird bewusst schrittweise aufgebaut. Zunächst stehen funktionale Prototypen, tragfähige Architekturprinzipien und modulare Kernlogik im Vordergrund.

---

## 5. Anwendungsfälle / Use Cases

### 5.1 Kamerabetrieb

- Kamera initialisieren
- Kameraparameter setzen und ändern
- Livebild streamen
- Livebild stoppen
- Einzelbilder speichern
- Bilder in Zeitintervallen speichern
- Metadaten zur Aufnahme erfassen

### 5.2 Interaktive Bildanzeige

- Livebild anzeigen
- Livebild an Fenster- oder Viewportgröße anpassen
- zwischen Pixel-1:1-Ansicht und fit-to-window wechseln
- in das Bild hinein- und herauszoomen
- den sichtbaren Ausschnitt pannen
- ROI-Masken definieren
- ROI-Masken ein- und ausblenden
- Crosshair ein- und ausblenden
- Crosshair bewegen
- Koordinaten anzeigen
- Hilfspunkte definieren
- Hilfspunkte sichtbar machen
- Hilfspunkte verfolgen oder erneut finden
- Overlays je nach Analysemodus aktivieren oder deaktivieren

### 5.3 Fokusbewertung

- Fokus global für das gesamte Bild bewerten
- Fokus lokal innerhalb einer ROI-Maske bewerten
- Fokusmethode auswählen
- Fokuswerte live anzeigen
- Fokuswerte auf Snapshots anwenden
- Fokus im Postprocess auf gespeicherte Bilder anwenden

### 5.4 Kanten- und Rissanalyse

- Kanten in einer definierten ROI suchen
- Kantenqualität als Fokusindikator nutzen
- Hilfspunkte auf Basis bildbasierter Merkmale verfolgen
- Rissspitzenkandidaten oder Driftmerkmale identifizieren
- erkennen, ob ein relevantes Merkmal aus dem Sichtfeld zu wandern droht

### 5.5 Externe Nutzung der Ergebnisse

- Analysewerte per API abrufen
- Analysewerte an andere Anwendungen weitergeben
- Trigger für Achsen oder Autofokus vorbereiten
- Zustands- oder Warnsignale an externe Systeme ausgeben

---

## 6. Betriebsmodi

Die Plattform soll mehrere Betriebsmodi unterstützen:

### 6.1 Livebetrieb

Kontinuierlicher Kamerastream mit Liveanzeige und optionaler Echtzeit- oder Quasi-Echtzeit-Analyse.

### 6.2 Snapshot-Analyse

Ein aktueller Frame wird manuell oder programmatisch eingefroren und gezielt analysiert.

### 6.3 Intervallaufnahme

Bilder werden in festgelegten Zeitabständen gespeichert und optional parallel angezeigt oder bewertet.

### 6.4 Offline-Postprocessing

Bereits gespeicherte Bilder oder Bildserien werden im Nachhinein ausgewertet.

### 6.5 Analyse-Feed-Modus

Analysewerte werden nicht nur angezeigt, sondern strukturiert an andere Module oder externe Anwendungen ausgegeben.

---

## 7. Gesamtstruktur des Systems

Das Gesamtsystem gliedert sich in mehrere logisch getrennte Hauptbereiche:

1. **Kamera- und Aufnahme-Modul**
2. **Anzeige- und Interaktionsmodul**
3. **Fokusmodul**
4. **Kanten-/Trackingmodul**
5. **Speicher- und Postprocessmodul**
6. **API- und Automationsmodul**
7. **Frontend-/Client-Schicht**

Diese Module greifen auf gemeinsame Kernmodelle und Basiskomponenten zurück.

---

## 8. Module und Verantwortlichkeiten

## 8.1 Kamera- und Aufnahme-Modul

### Aufgaben

- Kamera initialisieren
- Kamera konfigurieren
- Parameteränderungen übernehmen
- Frame-Erzeugung bzw. Streaming verwalten
- Einzelbilder und Intervallbilder speichern
- Bild- und Metadaten an andere Module übergeben

### Typische Funktionen

- Kamera starten / stoppen
- Belichtung, Gain, ROI, PixelFormat etc. setzen
- aktuelle Frame-Daten bereitstellen
- Bildspeicherung koordinieren

### Schnittstellen

- Übergabe von Frames an Anzeige und Analyse
- Übergabe von Bild- und Zeitinformationen an Speicher- und API-Module

---

## 8.2 Anzeige- und Interaktionsmodul

### Aufgaben

- Livebild oder Snapshot darstellen
- Overlays verwalten
- Anzeige-Viewport und Display-Transformation verwalten
- interaktive Werkzeuge bereitstellen
- Benutzerinteraktionen erfassen und an nachgelagerte Module weitergeben

### Unterstützte Interaktionselemente

- Rechteck-ROI
- Ellipsen-ROI
- Freihand-ROI / Freihandmaske
- Crosshair
- Koordinatenanzeige
- Hilfspunkte
- Sichtbarkeitsumschaltung für Overlays und Analyseebenen

### Besonderheit

Dieses Modul ist eng mit der UI verbunden, darf aber die eigentliche Analyse nicht selbst implementieren. Es soll nur Eingaben und Anzeigen koordinieren.

Anzeigeabhängige Funktionen wie Fenstergröße, Bildschirmauflösung, fit-to-window, Zoom, Pan und Overlay-Skalierung gehören in dieses Anzeige-/Interaktionsmodul oder in eine direkt daran gekoppelte Display-Schicht. Diese Funktionen dürfen nicht in den Kamera- oder Analysekern gezogen werden.

---

## 8.3 Fokusmodul

### Aufgaben

- globale Fokusbewertung
- lokale Fokusbewertung innerhalb einer ROI-Maske
- Auswahl und Verwaltung mehrerer Fokusmetriken
- Ausgabe von Fokuswerten an Anzeige, Logging oder API

### Mögliche Fokusverfahren

- Laplace-basierte Methoden
- Gradient-/Sobel-/Scharr-basierte Methoden
- Tenengrad
- kantenbasierte lokale Bewertungsmaße
- später optional MTF-nahe Verfahren

### Ziel

Das Fokusmodul soll einerseits einen generischen Fokuswert liefern, andererseits gezielt bewerten können, ob relevante Kanten im Fokus liegen.

---

## 8.4 Kanten-/Trackingmodul

### Aufgaben

- prototypische oder operative Kantenanalyse in definierten ROIs
- spalten- oder profilbasiertes Scannen entlang definierter Richtungen
- Merkmalsverfolgung bzw. Hilfspunkttracking
- Erkennung kritischer Drift oder des drohenden Verlassens des Sichtfelds
- perspektivische Rissspitzenabschätzung

### Charakter

Dieses Modul baut auf denselben Bilddaten und teilweise denselben ROI-Konzepten wie das Fokusmodul auf, hat jedoch einen anderen Analysezweck.

---

## 8.5 Speicher- und Postprocessmodul

### Aufgaben

- Bilder, Serien und Metadaten speichern
- Bildfolgen für Offline-Auswertung bereitstellen
- Analyseergebnisse dokumentieren
- Export in geeignete Ausgabeformate ermöglichen

### Mögliche Inhalte

- Zeitstempel
- Kameraparameter
- Fokuswerte
- ROI-Definitionen
- Tracking- oder Kantenkennwerte

---

## 8.6 API- und Automationsmodul

### Aufgaben

- Analysewerte nach außen verfügbar machen
- strukturierte Ausgabe für andere Anwendungen
- Trigger- oder Feedbacklogik vorbereiten
- spätere Kopplung an Aktoren oder Nachführsysteme ermöglichen

### Beispielanwendungen

- Warnung bei Bilddrift
- Anforderung einer Achsbewegung
- Autofokus-Trigger
- Z-Nachführung
- Zustandsabfrage anderer Softwaremodule

---

## 8.7 Frontends / Clients

Die Plattform soll perspektivisch mehrere Frontends unterstützen:

- OpenCV-basierter Prototyp
- Desktop-Anwendung
- Webstream-/Browserdarstellung mit Overlay
- Tablet-/Mobile-Anzeige

Die Kernlogik soll möglichst unabhängig von einer konkreten Frontend-Technologie bleiben.

---

## 9. Datenflüsse und Schnittstellen

### 9.1 Primäre Datenflüsse

- Kamera → Frame-Erzeugung → Anzeige
- Kamera → Frame-Erzeugung → Fokusmodul
- Kamera → Frame-Erzeugung → Kanten-/Trackingmodul
- Kamera → Frame-Erzeugung → Speicher
- Fokusmodul → Overlay / Anzeige
- Kantenmodul → Overlay / Anzeige
- Analyseergebnisse → API-Modul
- API-Modul → externe Anwendung / Bewegungssteuerung / Nachführung

### 9.2 Zentrale Schnittstellen

- FrameSource bzw. Kameradatenquelle
- ROI-Definition und ROI-Maske
- Analyse-Requests
- Analyse-Ergebnisse
- Ergebnisexport
- API-Aufrufe oder Eventfeeds

---

## 10. Voraussetzungen und Randbedingungen

## 10.1 Technische Voraussetzungen

- ein bestehender Kamerastream ist bereits vorhanden
- Python eignet sich für die erste Prototypingphase
- OpenCV ist für den Prototyp als Anzeige- und Bildverarbeitungsbasis verfügbar
- spätere Portierung nach C# soll vorbereitet werden
- die Architektur muss daher sprachneutral und modular gedacht werden

## 10.2 Fachliche Voraussetzungen

- relevante Bildmerkmale müssen im Livebild ausreichend sichtbar sein
- ROI-basierte Fokusbewertung ist fachlich sinnvoll
- Kantenbasierte Bewertung und Detektion sind für die Anwendung prinzipiell relevant
- spätere Nutzung der Ergebnisse für Nachführung oder Aktorik ist denkbar

## 10.3 Organisatorische Voraussetzungen

- schrittweiser Ausbau in Teilprojekten
- frühe Dokumentation ist erforderlich, um Komplexität beherrschbar zu halten
- Module sollen unabhängig test- und weiterentwickelbar sein
- nicht alle Frontends oder Automationspfade müssen sofort umgesetzt werden

---

## 11. Architekturprinzipien

Die Architektur des Projekts soll sich an folgenden Grundprinzipien orientieren:

### 11.1 Modularität

Jede Kernfunktion soll in einem logisch separierbaren Modul liegen. Kamera, Anzeige, Fokus, Kantenanalyse, Speicherung und externe Schnittstellen sollen nicht untrennbar verschachtelt werden.

### 11.2 Trennung von UI und Kernlogik

Interaktive Werkzeuge, Anzeige und Overlays gehören in die UI-nahe Schicht. Fokus- oder Kantenlogik gehört in eigenständige Analysekomponenten.

Darstellungsspezifische Transformationen wie Viewport-Anpassung, fit-to-window, Zoom, Pan und overlaybezogene Bildschirmtransformationen sind Teil der UI-/Display-Schicht und nicht Teil des Kamera- oder Aufnahme-Kerns.

### 11.3 Sprachneutrale Kernstruktur

Die Kernmodelle und Analyseabläufe sollen so entworfen werden, dass ein späterer Transfer nach C# erleichtert wird. Python-spezifische Kurzlösungen sollen im Kern möglichst vermieden werden.

### 11.4 Wiederverwendbarkeit

ROI-Definition, Maskenlogik, Datenmodelle und Basiskomponenten sollen zwischen Fokus-, Kanten-, Postprocess- und API-Modulen gemeinsam nutzbar sein.

### 11.5 Erweiterbarkeit

Weitere Frontends, Analyseverfahren oder externe Schnittstellen sollen ergänzbar sein, ohne den gesamten Kern neu strukturieren zu müssen.

### 11.6 Unterstützung mehrerer Betriebsarten

Die Plattform soll nicht nur für Livebetrieb, sondern auch für Snapshot- und Offline-Auswertung geeignet sein.

---

## 12. Arbeitspakete / Arbeitsteilung

Die Umsetzung wird in logisch getrennte Arbeitspakete unterteilt.

## AP1 – Projektgrundlage und Architektur

### Inhalte

- Zieldefinition
- Begriffs- und Modulklärung
- Dokumentation der Systemstruktur
- Definition gemeinsamer Datenmodelle
- Festlegung zentraler Schnittstellen und Architekturprinzipien

---

## AP2 – Kamerabasis und Frame-Bereitstellung

### Inhalte

- Integration oder Konsolidierung des bestehenden Kamerastreams
- Parametrierung der Kamera
- Snapshot- und Intervallaufnahme
- Bereitstellung standardisierter Frame-Daten für andere Module

---

## AP3 – Anzeige und Interaktion

### Inhalte

- Livebildanzeige
- Overlay-Grundlagen
- ROI-Zeichenwerkzeuge
- Crosshair
- Koordinatenanzeige
- Sichtbarkeitsumschaltung
- Hilfspunkte

---

## AP4 – Fokusanalyse

### Inhalte

- globale Fokusbewertung
- lokale Fokusbewertung in ROI-Masken
- Auswahl der Fokusmethode
- Ergebnisdarstellung
- Vergleich von Fokusmetriken

---

## AP5 – Kanten- und Trackingansätze

### Inhalte

- kantenbasierte Analyse in ROI
- spalten- bzw. profilbasierte Auswertung
- Hilfspunktverfolgung
- erste Driftlogik
- perspektivische Rissspitzenheuristiken

---

## AP6 – Speicherung und Postprocess

### Inhalte

- Bild- und Metadatenspeicherung
- Offline-Auswertung
- Ergebnisexport
- Vorbereitung einer getrennten Postprocess-Komponente

---

## AP7 – API und Automation

### Inhalte

- standardisierte Ergebnisbereitstellung
- externe Abfrage von Zuständen und Werten
- Event- oder Feed-Struktur
- Vorbereitung von Achsen-, Fokus- oder Z-Nachführungslogik

---

## AP8 – Frontends und spätere Clients

### Inhalte

- OpenCV-Prototyp als frühe Visualisierungsschicht
- spätere Desktop-App
- Webstream-/Browservarianten
- mobile oder tabletbasierte Anzeige

---

## 13. MVP / erste Ausbaustufe

Die erste sinnvolle Ausbaustufe sollte bewusst begrenzt bleiben.

### MVP-Ziele

- bestehender Kamerastream liefert stabil ein Livebild
- Livebild kann angezeigt werden
- interaktive ROI-Definition ist möglich
- Rechteck-, Ellipsen- und Freihandmaske werden unterstützt
- Fokus kann global und lokal in einer Maske berechnet werden
- Fokusverfahren können ausgewählt werden
- Fokuswerte können im Prototyp eingeblendet werden
- Einzelbilder oder Intervallbilder können gespeichert werden
- Ergebniswerte sind intern oder über eine einfache Schnittstelle abrufbar

### Noch nicht zwingend im MVP

- vollständige Desktop-App
- ausgereiftes Webfrontend
- vollautomatische Nachführung
- komplexe Trackinglogik
- vollständige Rissspitzenbestimmung
- umfassende Multi-Client-Unterstützung

---

## 14. Ausbaupfade / spätere Stufen

Nach dem MVP sind mehrere Ausbaupfade denkbar:

### Ausbaupfad A – Interaktive Analyse verbessern

- zusätzliche Overlays
- mehrere Masken gleichzeitig
- Hilfspunktverwaltung
- Trackinglogik
- bessere Visualisierung von Analyseergebnissen

### Ausbaupfad B – Kanten- und Risslogik vertiefen

- robuste spaltenbasierte Kantendetektion
- Kantenkontinuitätsanalyse
- Driftwarnung
- Rissspitzenkandidaten
- Kombination aus Fokus- und Kantenmetriken

### Ausbaupfad C – API und Automation

- saubere externe API
- Eventfeed
- Ansteuerung externer Aktoren
- Fokus- oder Z-Nachführung
- Kopplung an andere Steuerprogramme

### Ausbaupfad D – Frontend-Ausbau

- Desktop-App
- Webstream mit Overlay
- Tablet-/Mobile-Anzeigen
- getrennte Operator- und Entwickleransichten
- viewportbasierte Preview-Darstellung mit fit-to-window
- interaktive Zoom- und Pan-Steuerung
- overlaystabile Anzeige trotz Display-Skalierung

### Ausbaupfad E – Postprocessing und Datenauswertung

- Batch-Auswertung
- Vergleich verschiedener Fokusmetriken
- gespeicherte Bildserien auswerten
- Dokumentations- und Exportfunktionen

---

## 15. Risiken und offene Punkte

### 15.1 Technische Risiken

- Performance im Livebetrieb
- UI-Komplexität bei wachsender Interaktion
- steigender Integrationsaufwand durch mehrere Frontends
- unterschiedliche Anforderungen von Echtzeit und Postprocess
- saubere Abgrenzung zwischen Prototyp und stabiler Anwendung

### 15.2 Methodische Risiken

- Fokusmetriken korrelieren nicht immer direkt mit praktischer Kantenverwendbarkeit
- Kantenansatz kann empfindlich auf Rauschen, Beleuchtung oder lokale Bildartefakte reagieren
- Freihand-ROI und komplexe Masken erschweren die Analysegeometrie
- Tracking und Risslogik benötigen robuste Qualitätskriterien

### 15.3 Architekturrisiken

- Gefahr der Vermischung von UI, Analyse und Hardwarecode
- Python-Prototyp kann ohne Disziplin zu schwer portierbarem Code führen
- zu frühe Berücksichtigung aller Frontends könnte den MVP verzögern

### 15.4 Offene Punkte

- spätere GUI-Technologie für Desktop-App
- endgültiges API-Format
- Priorisierung zwischen Fokus- und Kantenmodul
- Definition der ersten externen Automationsschnittstelle
- konkrete Speicher- und Exportformate
- Echtzeitgrenzen und Analyseintervalle

---

## 16. Erfolgskriterien

Das Projekt gilt in einer ersten Stufe als erfolgreich, wenn folgende Punkte erfüllt sind:

- stabiler Livebildbetrieb ist möglich
- Kamera kann parametriert werden
- Bilder können gespeichert werden
- ROI-Masken können interaktiv im Bild definiert werden
- mehrere ROI-Formen werden unterstützt
- Fokus kann global und lokal bewertet werden
- Fokusverfahren sind auswählbar
- Analysewerte können sichtbar gemacht und abgerufen werden
- die Architektur bleibt trotz wachsender Anforderungen modular
- zentrale Komponenten sind so strukturiert, dass eine spätere Portierung nach C# realistisch bleibt

---

## 17. Vorläufige Zusammenfassung

Das Vorhaben ist kein einzelnes kleines Bildverarbeitungsskript mehr, sondern die Grundlage für eine modulare Vision-Plattform. Der erste Schwerpunkt liegt auf einem tragfähigen Kern aus Kamerastream, interaktiver Anzeige, ROI-basierter Fokusbewertung und strukturierter Erweiterbarkeit. Darauf aufbauend sollen weitere Module für Kantenanalyse, Tracking, API-Ausgabe, Postprocessing und spätere Frontends folgen.

Entscheidend ist, das Projekt von Beginn an nicht als monolithisches Tool, sondern als Sammlung klar abgegrenzter, gemeinsam nutzbarer Teilkomponenten zu verstehen.
