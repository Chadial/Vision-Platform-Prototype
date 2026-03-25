# Roadmap Kamera-Software: Python -> C# -> WebUI

## Zielbild

Eine skalierbare Kamera-Architektur, die:

- kurzfristig in **Python** schnell zum Laufen gebracht wird
- mittelfristig in **C# / Visual Studio** vom Team uebernommen werden kann
- langfristig eine **WebUI** fuer Desktop, Tablet und Smartphone erlaubt
- sauber mit der **AMB-Control-Software** zusammenarbeitet
- Snapshot und "Video"-Speicherung inklusive frei vorgebbarem Speicherpfad unterstuetzt
- einen klar getrennten Pfad fuer **echte Hardware** und **Simulation/Demo-Betrieb** erlaubt

---

## Leitprinzip

Nicht sofort alles gleichzeitig lernen und bauen.

Stattdessen in dieser Reihenfolge:

1. **Kamera verstehen**
2. **funktionierenden Prototyp bauen**
3. **Code sauber strukturieren**
4. **gleiche Struktur in C# nachziehen**
5. **spaeter WebUI darueberlegen**

---

## Architektur-Ziel in einem Satz

Die Kamera- und Recording-Logik soll **vom UI entkoppelt** werden, sodass spaeter wahlweise

- eine lokale Desktop-Anwendung
- eine integrierte AMB-Software-Loesung
- oder eine WebUI

darauf aufsetzen kann.

Dasselbe sollte fuer die Bildquelle gelten:

- echte Kamerahardware
- simulierte Testquelle
- Demoquelle auf Basis echter Beispielbilder

sollen moeglichst ueber dieselbe Kernlogik laufen.

---

## Roadmap-Phasen

| Phase | Fokus | Ziel | Primaeres Tool |
|---|---|---|---|
| 1 | Kamera zum Laufen bringen | Livebild, Snapshot, Speichern | PyCharm + Python |
| 2 | Python sauber strukturieren | Services, Requests, Logging, Recording | PyCharm |
| 2a | Simulationspfad | Hardwarefreie Entwicklung, Tests und Demos | Python |
| 3 | AMB-nahe Schnittstelle modellieren | externe Kommandos, Save Path, Status | Python |
| 3a | Optionaler Transport-/Payload-Vertrag | nur bei Bedarf: hostspezifische DTOs oder API-Payloads | spaeter mit C# mitdenken |
| 4 | C#-Uebertragung | teamfaehiges Kamera-Subsystem | Visual Studio |
| 5 | Integration in AMB-Software | direkte Steuerung aus Hauptsoftware | C# |
| 6 | WebUI-faehige Architektur | Browser, Tablet, Mobil | .NET / Web |

---

## Phase 1 - Python / PyCharm / Kamera-MVP

### Ziel

Ein kleiner, funktionierender Prototyp mit:

- Kamera finden
- Livebild anzeigen
- Snapshot speichern
- einfachen Kameraeinstellungen
- erstem Logging

### Lernfokus

- Python-Grundlagen
- PyCharm bedienen
- Virtual Environment
- SDK installieren
- OpenCV oder einfacher Preview-Weg
- Debugging

### Ergebnis

Ein erstes Testprogramm wie:

- `main.py`
- `camera_test.py`

Mit Funktionen:

- Start Live Preview
- Taste oder Befehl fuer Snapshot
- Bildspeicherung in lokalen Ordner
- einfacher Log-Eintrag

### Wichtig

Hier geht es **nicht** um schoene Software, sondern um:

- Kamera verstehen
- SDK verstehen
- Datenfluss verstehen

Wenn die Hardware nicht verfuegbar ist, ist ein kleiner Simulationspfad sinnvoll, um Datenfluss, Logging und Speicherverhalten trotzdem weiterentwickeln zu koennen.

---

## Phase 2 - Python-Prototyp sauber strukturieren

### Ziel

Vom Skript zur kleinen Softwarestruktur wechseln.

### Modulidee

```text
camera_app/
|- main.py
|- models.py
|- camera_config.py
|- camera_driver.py
|- preview_service.py
|- recording_service.py
|- log_service.py
|- images/
`- logs/
```

### Zielklassen

- `CameraConfiguration`
- `SnapshotRequest`
- `RecordingRequest`
- `CameraStatus`
- `PreviewFrameInfo`

### Zielservices

- `CameraDriver`
- `PreviewService`
- `RecordingService`
- `LogService`

### Ergebnis

Python kann dann bereits:

- Konfiguration anwenden
- Snapshot speichern
- Recording starten / stoppen
- Speicherpfad entgegennehmen
- Status zurueckgeben
- Preview und Recording trennen
- zwischen echter Kamera und Simulation unterscheiden, ohne die Service-Struktur zu aendern

---

## Phase 2a - Simulationspfad fuer Entwicklung und Demo

### Ziel

Ein simulierter Kamerapfad soll Preview, Snapshot und Recording auch ohne angeschlossene Kamera ermoeglichen.

### Nutzen

- Entwicklung laeuft weiter, wenn Hardware nicht verfuegbar ist
- Demo-Szenarien koennen stabil vorbereitet werden
- Service- und Loggingverhalten kann ohne Kamera validiert werden
- echte Beispielbilder koennen fuer realistische Demos genutzt werden

### Anforderungen

- eigene Driver-Implementierung getrennt vom SDK-Treiber
- wahlweise deterministische Testframes oder Beispielbild-Sequenzen
- identische Nutzung ueber `CameraDriver`, `SnapshotService`, `PreviewService` und `RecordingService`
- klar erkennbar, ob echte Hardware oder Simulation verwendet wird

---

## Phase 3 - Schnittstelle zur AMB-Software gedanklich vorbereiten

### Ziel

Die Kamera-Software nicht als isoliertes Tool denken, sondern als Subsystem der AMB-Control-Software.

### Eingehende Befehle aus AMB-Software

- Konfiguration setzen
- Speicherpfad setzen
- Snapshot ausloesen
- Recording starten
- Recording stoppen
- Status abfragen

### Daraus abgeleitete Methoden

ApplyConfiguration(config)
SetSaveDirectory(path)
SaveSnapshot(request)
StartRecording(request)
StopRecording()
GetStatus()

### Vorteil

Schon der Python-Prototyp wird so gebaut, dass seine Struktur spaeter gut nach C# portierbar ist.

### Phase 3a - optionaler Hinweis fuer spaetere Host-/API-Vertraege

Falls spaeter ein ganz konkreter Transportvertrag gebraucht wird, zum Beispiel:

- JSON-Payloads
- C#-DTOs
- klar versionierte Request-/Response-Vertraege

dann ist das **kein Pflichtteil der Python-Phase 3**.

Das ist eher ein **optional vorgezogener Vorgriff auf Phase 4**, wenn die C#-Uebertragung oder eine konkrete Host-Integration ihn wirklich braucht.

---

## Phase 4 - Uebertragung nach C# / Visual Studio

### Ziel

Ein teamfaehiges Kamera-Subsystem in C#.

### Lernfokus

- C#-Klassen
- Interfaces
- Projekte / Solutions
- Visual Studio
- Events / Callbacks
- Logging
- grundlegende Threading-/Async-Konzepte

### Zielstruktur in C#

- `ICameraDriver`
- `CameraService`
- `RecordingService`
- `SnapshotService`
- `CameraConfiguration`
- `RecordingRequest`
- `CameraStatus`

### Reihenfolge

1. Kamera finden
2. Snapshot
3. Preview
4. Recording starten/stoppen
5. Save Path / Dateinamenslogik
6. Statusmodell
7. AMB-Integration

### Optionaler Hinweis aus Phase 3a

Falls ein konkreter Host-, API- oder Integrationsvertrag benoetigt wird, ist hier der passende Zeitpunkt, um:

- C#-DTOs fuer Requests und Responses festzulegen
- Feldnamen und Datentypen verbindlich zu machen
- spaetere JSON- oder IPC-Payloads sauber abzuleiten

### Ergebnis

Ein eigenstaendiges Kamera-Modul, das spaeter direkt vom Team wartbar ist.

---

## Phase 5 - Integration in die AMB-Control-Software

### Ziel

Die AMB-Software wird Master, die Kamera ist ein Subsystem.

### Rollenverteilung

| Systemteil | Rolle |
| --- | --- |
| AMB-Control-Software | gibt Befehle und Parameter vor |
| Kamera-Modul | fuehrt Preview, Snapshot, Recording, Logging aus |
| Dateisystem | speichert Bilder / Serien / Logs |

### Typische Steuerdaten aus AMB

- Save Path
- Dateinamensschema
- Snapshot-Befehl
- Start/Stop Recording
- Metadaten zum Versuch
- ggf. Trigger-Informationen

### Ziel

Kein loses Paralleltool, sondern eine sauber eingebundene Funktion innerhalb des Gesamtsystems.

---

## Phase 6 - WebUI-faehige Architektur

### Ziel

Spaeter soll dieselbe Kernlogik auch von einer Weboberflaeche aus bedient werden koennen.

### Wichtig

Die WebUI wird **nicht** zuerst gebaut.  
Sie wird spaeter auf eine bereits saubere Service-Struktur gesetzt.

### Dafuer muss heute schon getrennt werden

- **Kernlogik**
- **Hardware-Anbindung**
- **UI**

### Spaetere Zielkanaele

- Desktop-Browser
- Tablet
- Smartphone
- ggf. interne Netzwerknutzung

### Was die WebUI spaeter koennen soll

- Livebild anzeigen
- Status anzeigen
- Snapshot ausloesen
- Recording starten/stoppen
- Konfigurationswerte aendern
- Speicherpfade und Dateinamen kontrollieren

---

## Begriffssortierung fuer spaetere .NET-Webwelt

| Begriff | Bedeutung fuer dich |
| ------------------ | --------------------------------------------- |
| Backend | enthaelt Kamera- und Recording-Logik |
| API | Befehlszugang fuer UI oder andere Software |
| WebUI | sichtbare Oberflaeche im Browser |
| Echtzeit-Updates | Statusaenderungen ohne manuelles Aktualisieren |
| responsiv | Layout passt sich Tablet / Handy / Desktop an |
| modularer Monolith | eine Anwendung, aber intern sauber getrennt |

### Vereinfachte mentale Sortierung

- **Kernlogik** = was die Kamera tun kann
- **Schnittstelle** = wie andere Software Befehle gibt
- **UI** = wie ein Mensch das bedient
- **WebUI** = UI im Browser statt klassischem Desktopfenster

---

## Lernpfad

## 1. Jetzt sofort lernen

- Python-Basis
- PyCharm
- Kamera-SDK-Grundlagen
- Bildanzeige
- Snapshot / Speichern
- Logging

## 2. Danach lernen

- Python-Klassen sauber strukturieren
- Requests / Statusmodelle
- Service-Denken
- Trennung von Preview und Recording
- Trennung von echter Hardware und Simulation

## 3. Danach lernen

- Visual Studio
- C#-Klassen und Interfaces
- Portierung der Python-Struktur nach C#

## 4. Erst spaeter lernen

- .NET-Webkonzepte
- WebUI
- Browserbedienung
- responsive Layouts

---

## Empfohlene Milestones

| Milestone | Beschreibung | Ergebnis |
| --------- | -------------------------- | ---------------------------------------- |
| M1 | Kamera laeuft in Python | Livebild sichtbar |
| M2 | Snapshot funktioniert | Einzelbild speicherbar |
| M3 | Save Path steuerbar | Bilder landen kontrolliert im Zielordner |
| M4 | Recording-Grundfunktion | Bildserie / "Video"-aehnliche Speicherung |
| M5 | Python sauber strukturiert | Services + Modelle vorhanden |
| M5a | Simulationspfad vorhanden | Demo- und Testbetrieb auch ohne Hardware |
| M6 | C#-Port Grundgeruest | Kamera-Modul in Visual Studio |
| M7 | AMB-Ansteuerung | Befehle aus Hauptsoftware moeglich |
| M8 | WebUI-Vorbereitung | Architektur dafuer sauber genug |
| M9 | erste WebUI | Browseransicht mit Status + Preview |

## Minimaler Umsetzungsplan

### Kurzfristig

- Python in PyCharm
- Kamera-Prototyp
- Livebild
- Snapshot
- Save Path
- Logging
- bei Bedarf Simulationsquelle oder Beispielbildquelle fuer Demos und testsichere Entwicklung

### Mittelfristig

- gleiche Struktur in C#
- Teamkompatibles Kamera-Modul
- AMB-Integration

### Langfristig

- WebUI
- Tablet-/Mobil-Unterstuetzung
- UI austauschbar, Kern bleibt gleich

---

## Entscheidungsregel

Wenn unklar ist, was als Naechstes kommt, dann gilt:

**Immer zuerst den naechsten technisch verwertbaren Baustein bauen, nicht die spaetere Idealwelt.**

Also jetzt:

1. Kamera laeuft
2. Snapshot laeuft
3. Speichern laeuft
4. Recording laeuft
5. Simulationspfad fuer hardwarefreie Entwicklung steht
6. Struktur wird sauber
7. erst dann C#
8. erst dann WebUI

---

## Konkrete naechste Schritte

### Naechster praktischer Schritt

- PyCharm-Projekt anlegen
- Kamera-SDK lokal testen
- erstes Minimalprogramm fuer Livebild und Snapshot bauen

### Danach

- Modulstruktur definieren
- Requests und Statusobjekte anlegen
- Save-Path von aussen uebergebbar machen
- Simulationspfad fuer Preview, Snapshot und Recording vorbereiten

### Danach

- Portierungsplan nach C# vorbereiten

---

## Merksatz

**Python ist dein schneller Lern- und Prototypingpfad.  
C# ist dein teamfaehiger Produktpfad.  
WebUI ist deine spaetere Skalierungsschicht.**
