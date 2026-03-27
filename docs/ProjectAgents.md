# Codex-Agent Briefing – Reorganisation des bestehenden Kamera-Stream-Repos zur modularen Vision-Plattform

## Ziel

Das bestehende Python-Repository enthält bereits funktionierende Teile für Kamerastream, Livebildanzeige und Bildspeicherung. Dieses Repository soll **nicht** durch ein separates neues Projekt ersetzt werden, sondern als Grundlage für eine **modulare Vision-Plattform** weiterentwickelt werden.

Die Aufgabe besteht **zunächst nicht** darin, alle neuen Features vollständig zu implementieren, sondern darin, das bestehende Repository so zu reorganisieren, dass es eine tragfähige Basis für folgende Ausbaupfade bildet:

- Kamera parametrieren
- Kamera streamen
- Bilder speichern
- Livebild anzeigen
- ROI-Masken interaktiv definieren
- Fokus global und lokal bewerten
- Kanten-/Trackingansätze ergänzen
- Analysewerte später per API oder Feed bereitstellen
- spätere Desktop-, Web- und Mobile-Frontends vorbereiten
- spätere C#-Portierung zentraler Kernmodule erleichtern

---

## Wichtigste Arbeitsregel

**Kein Big-Bang-Refactoring.**  
Das bestehende Projekt soll **schrittweise** reorganisiert werden. Nach jeder größeren Umstrukturierung soll der vorhandene lauffähige Kern möglichst erhalten bleiben oder zeitnah wiederhergestellt werden.

---

## Primäre Ziele der aktuellen Aufgabe

1. Das bestehende Repository analysieren und die aktuelle Struktur dokumentieren.
2. Eine neue Zielstruktur für das Repository anlegen.
3. Bestehende Funktionen logisch in neue Modulbereiche überführen.
4. Bereits vorhandene Kamera-, Stream-, Anzeige- und Speicherlogik in eine sauberere Struktur bringen.
5. Platzhalter oder minimale Grundmodule für spätere Erweiterungen anlegen:
   - ROI
   - Fokus
   - gemeinsame Datenmodelle
   - API-Vorbereitung
6. Die Reorganisation so durchführen, dass das Projekt weiterhin in Python gut nutzbar bleibt, aber architektonisch möglichst C#-kompatibel ist.

---

## Was ausdrücklich **nicht** sofort getan werden soll

- nicht sofort alle neuen Features vollständig implementieren
- nicht sofort Desktop-, Web- und Mobile-Frontends bauen
- nicht sofort das gesamte UI neu schreiben
- nicht sofort die API vollständig definieren
- nicht sofort Tracking- oder Rissspitzenlogik ausimplementieren
- nicht spontan große fachliche Logik ändern, wenn der bestehende Code bereits funktioniert

Die Aufgabe ist **zuerst Struktur- und Architekturarbeit**, nicht Funktionsmaximierung.

---

## Arbeitsweise

## 1. Zuerst Bestandsaufnahme

Bevor Dateien massiv verschoben werden:

- analysiere die aktuelle Repo-Struktur
- identifiziere die existierenden Einstiegspunkte
- identifiziere vorhandene Kamera-, Stream-, Anzeige- und Speicherlogik
- dokumentiere problematische Kopplungen
- dokumentiere globale Zustände, harte Abhängigkeiten und technische Schulden
- erstelle eine kurze Migrationsübersicht

Erzeuge dazu im Repo einen Dokumentationsbereich, z. B.:

- `docs/project_overview.md`
- `docs/current_state.md`
- `docs/target_structure.md`
- `docs/migration_plan.md`

---

## 2. Zielstruktur anlegen

Lege eine neue, modulare Repo-Struktur an. Falls nötig, passe Namen pragmatisch an den Bestand an, aber die Richtung soll ungefähr so aussehen:

```text
repo/
├─ apps/
├─ libraries/
├─ services/
├─ integrations/
├─ configs/
├─ docs/
├─ tests/
└─ tools/
```
Bedeutung der Bereiche
apps/

Startbare Anwendungen oder Prototypen, z. B.:

OpenCV-Prototyp
später API-Server
später Postprocess-Tool
libraries/

Wiederverwendbare Kernlogik ohne direkte UI- oder Hardwarebindung, z. B.:

gemeinsame Datenmodelle
ROI-Grundlagen
Fokus-Grundlagen
Bild-/Geometriehilfen
services/

Anwendungsnahe Logik und Orchestrierung, z. B.:

Stream-Service
Recording-Service
später Fokus-Service
integrations/

Anbindung an externe Systeme oder SDKs, z. B.:

Kameraschnittstelle
spätere Aktorikadapter
configs/

Konfigurationen für verschiedene Betriebsarten

docs/

Architektur-, Migrations- und Projektbeschreibungen

tests/

Unit- und Integrationstests

tools/

Hilfsskripte, Benchmarks, Dev-Werkzeuge

3. Bestehenden Code logisch einordnen

Führe die bestehenden Funktionen kontrolliert in diese Struktur über.

Besonders wichtige vorhandene Bereiche

Diese drei Themenblöcke sind aktuell die erste stabile Basis und sollen als solche behandelt werden:

Kamera / Frame-Erzeugung
Live-Stream / Anzeige
Bildspeicherung / Recording

Diese Bereiche sollen zuerst sauber gekapselt werden.

4. Zielarchitektur für die erste Reorganisationsstufe

Die Architektur soll bereits jetzt in Schichten gedacht werden:

Presentation / UI

Verantwortlich für:

Bildanzeige
Bedienung
Overlays
Interaktive Werkzeuge
Viewport-, Zoom-, Pan- und fit-to-window-Verhalten
Application / Services

Verantwortlich für:

Workflows
Start/Stop
Weitergabe von Frames
Koordination zwischen Anzeige, Analyse und Speicherung
Domain / Core

Verantwortlich für:

sprachneutrale Datenmodelle
ROI-Konzepte
Fokusmetriken
spätere Kanten-/Trackinglogik
Infrastructure / Integrations

Verantwortlich für:

Kamera-SDK
Dateisystem
spätere API-/Netzwerkadapter

Zusatzregel für Preview und Anzeige:
Bildschirmauflösung, Fenstergröße, Zoomfaktor, Pan-Offset, fit-to-window und displayseitige Overlay-Transformationen gehören nicht in den Kamera- oder Recording-Kern. Solche Darstellungsregeln sollen in der Presentation/UI-Schicht oder in einer eng daran gekoppelten Display-Adapter-Schicht liegen.

Für operatornahe Preview-Bedienung gilt dieselbe Regel: Statusleisten, Menü- oder Kontrollbänder, Maus-/Tastaturinteraktion für Crosshair, ROI-Werkzeuge, Fokusanzeige, Snapshot-Buttons oder sensorbezogene UI-Eingaben gehören in die UI-/Display-Schicht und nicht in den Kamera- oder Analysekern.

Diese Trennung muss nicht sofort in perfekter Lehrbuchform umgesetzt werden, aber die Richtung soll klar erkennbar sein.

5. C#-Kompatibilität berücksichtigen

Die neue Struktur soll spätere Portierung oder Parallelentwicklung in C# erleichtern.

Deshalb bitte beachten
Kernlogik nicht in UI-Code einbetten
Hardwarezugriff nicht mit Analysecode vermischen
klare Datenobjekte statt lose Dict-Kaskaden bevorzugen
keine unnötig Python-spezifischen Architekturmuster im Kern
klar benannte Klassen, Services und Modelle verwenden
Funktionen mit gut definierter Ein- und Ausgabe bevorzugen
ROI, FrameData, Analyse-Requests und Analyse-Ergebnisse als explizite Modelle anlegen
Nicht erwünscht
ein neuer Monolith
unstrukturierte utils.py als Sammelbecken
stark versteckte Seiteneffekte
UI-Callbacks, die direkt Hardware und Analyse zugleich steuern
6. Gemeinsame Basismodelle vorbereiten

Lege in libraries/ oder einem vergleichbaren Kernbereich grundlegende Modelle an, auch wenn sie zunächst minimal sind.

Vorschlag
FrameData
FrameMetadata
RoiDefinition
RoiMask
FocusRequest
FocusResult

Diese Modelle dürfen in der ersten Stufe einfach gehalten sein, sollen aber die spätere Plattformstruktur vorbereiten.

7. ROI- und Fokus-Erweiterung vorbereiten

Es soll noch nicht alles vollständig implementiert werden, aber die Struktur dafür soll angelegt werden.

ROI

Das System soll perspektivisch interaktive Masken unterstützen:

Rechteck
Ellipse
Freihand

Daher soll ROI nicht nur als Crop gedacht werden, sondern als Kombination aus:

geometrischer Definition
daraus ableitbarer Pixelmaske
Fokus

Das Fokusmodul soll perspektivisch mit dem bestehenden Kamerastream kompatibel sein und später sowohl auf:

Liveframes
Snapshots
Offline-Bildern

arbeiten können.

Lege dafür bitte eine sinnvolle Grundstruktur an, ohne schon alle Fokusmethoden vollständig umzusetzen.

8. Bestehendes Livebild-Projekt als Basis erhalten

Die bestehende Livebildanzeige ist wertvoll und soll nicht unnötig zerstört werden.

Ziel

Das bisherige Kamera-/Stream-/Speicherprojekt soll in die neue Struktur überführt werden und weiterhin der Ausgangspunkt des Systems bleiben.

Deshalb
vorhandene Funktionalität möglichst erhalten
bestehende Run- und Testpfade nachvollziehbar halten
nach Refactoring möglichst wieder lauffähigen OpenCV-Prototyp bereitstellen
bestehende Features erst stabilisieren, dann erweitern
9. Empfohlene erste Teilprojekte im Repo

Bitte richte mindestens folgende Bereiche ein oder bereite sie vor:

apps/opencv_prototype/

enthält den aktuellen oder migrierten prototypischen Einstiegspunkt für:

Kamera starten
Livebild anzeigen
Bilder speichern
integrations/camera/

enthält kamera- oder SDK-spezifische Anbindung

services/stream_service/

enthält Streaming- und Frame-Verteilungslogik

services/recording_service/

enthält Speicher- und Aufnahmefunktionalität

libraries/common_models/

gemeinsame Datenmodelle

libraries/roi_core/

Platz für ROI-Definition, ROI-Maske, ROI-Hilfslogik

libraries/focus_core/

Platz für Fokus-Grundstruktur

Diese Module dürfen anfangs noch leichtgewichtig sein, sollen aber sauber benannt und dokumentiert werden.

10. Dokumentation, die angelegt werden soll

Erzeuge oder aktualisiere folgende Markdown-Dateien:

docs/project_overview.md

Kurze Beschreibung des Zielsystems und der Modulbereiche.

docs/current_state.md

Beschreibung des aktuellen Bestands:

was existiert bereits
was funktioniert
wo sind enge Kopplungen
was sind Risiken
docs/target_structure.md

Neue Zielstruktur mit kurzer Beschreibung je Hauptordner.

docs/migration_plan.md

Schrittweise geplante Migration:

Phase 1: Struktur schaffen
Phase 2: vorhandene Kernlogik verschieben/kapseln
Phase 3: ROI-/Fokus-Vorbereitung
Phase 4: weitere Erweiterungen
optional: docs/architecture_principles.md

Grundprinzipien:

modular
UI getrennt von Kernlogik
hardwareunabhängige Kernmodelle
C#-kompatible Richtung
11. Tests und Lauffähigkeit

Wenn bereits Tests existieren:

migriere sie so weit wie sinnvoll mit
passe Imports an
breche keine funktionierende Testlandschaft unnötig auf

Wenn kaum Tests existieren:

lege wenigstens minimale Smoke-Tests oder Startprüfungen an
dokumentiere, welche Funktionalität nach der Reorganisation manuell geprüft werden soll
Besonders wichtig

Nach der ersten Umstrukturierung soll möglichst mindestens Folgendes noch funktionieren oder wiederhergestellt werden:

Kamera-/Frame-Initialisierung
Livebildanzeige
Bildspeicherung oder Snapshot
ein startbarer Prototyp-Einstiegspunkt
12. Vorgehensreihenfolge

Bitte in dieser Reihenfolge arbeiten:

Phase 1 – Analyse
Repo-Struktur lesen
Bestand dokumentieren
Problemzonen identifizieren
Phase 2 – Zielstruktur anlegen
neue Ordner erstellen
Dokumentation ergänzen
noch nicht alles verschieben
Phase 3 – Vorhandene Kernbereiche migrieren
Kamera-/Integrationslogik
Stream-/Frame-Logik
Recording-/Speicherlogik
OpenCV-Prototyp-Einstiegspunkt
Phase 4 – Platzhalter und Basismodelle ergänzen
gemeinsame Modelle
ROI-Grundmodule
Fokus-Grundmodule
Phase 5 – Bereinigung
Imports korrigieren
alte Pfade reduzieren
doppelte Hilfsfunktionen identifizieren
README bzw. Startanleitung aktualisieren
13. Erwartetes Ergebnis

Am Ende dieser Aufgabe wird nicht erwartet, dass die gesamte Vision-Plattform fertig ist.

Erwartet wird stattdessen:

ein erkennbar neu strukturiertes Repository
eine dokumentierte Zielarchitektur
ein migrierter und weiterhin nutzbarer Basiskern
klar vorbereitete Erweiterungspunkte für ROI, Fokus und spätere Analyse
eine Struktur, die weiteres Wachstum kontrolliert ermöglicht
14. Ausgabeformat der Arbeit

Bitte liefere am Ende eine strukturierte Zusammenfassung mit:

Analyse des bisherigen Zustands
durchgeführten Strukturänderungen
neu angelegten Modulbereichen
verschobenen oder angepassten Dateien
offenen Punkten / Risiken
konkreten nächsten empfohlenen Schritten

Wenn möglich, zusätzlich:

kurze Baumstruktur des neuen Repos
Hinweise, was jetzt lauffähig ist
Hinweise, was bewusst nur vorbereitet, aber noch nicht implementiert wurde
15. Wichtigster Leitgedanke

Dieses Repository soll von einem funktionalen Kamera-/Stream-Projekt zu einer modularen, erweiterbaren Vision-Plattform entwickelt werden.

Die Reorganisation soll:

pragmatisch,
schrittweise,
dokumentiert,
und ohne unnötige Zerstörung bestehender Funktionalität

erfolgen.


Darunter kannst du Codex noch diese kurze Arbeitsanweisung setzen:

```markdown
## Arbeitsanweisung

Bitte beginne mit einer Bestandsaufnahme des bestehenden Repositories und schlage danach eine konkrete Migrationsstrategie vor, bevor du größere Dateioperationen ausführst. Anschließend setze die Reorganisation schrittweise um und dokumentiere jede relevante strukturelle Entscheidung in `docs/`.
```

## 16. Modulare Arbeitsorganisation

Das Repository soll nicht nur technisch, sondern auch organisatorisch als Sammlung eigenständiger Module aufgebaut werden.

### Grundregel

Jedes größere Modul ist als separater Arbeitsbereich zu behandeln, der perspektivisch auch unabhängig von einem eigenen Agentenlauf oder einem spezialisierten Sub-Agenten bearbeitet werden kann.

### Für jedes wesentliche Modul anlegen

Für jedes relevante Modul soll ein eigener Ordnerbereich mit begleitender Dokumentation entstehen. Jedes Modul soll mindestens folgende Dateien enthalten:

- `README.md`
- `STATUS.md`
- `ROADMAP.md`

### Bedeutung der Dateien

#### `README.md`
Beschreibt:
- Ziel des Moduls
- Verantwortungsbereich
- zentrale Funktionen
- Inputs und Outputs
- Abhängigkeiten zu anderen Modulen
- Start- oder Nutzungshinweise, falls sinnvoll

#### `STATUS.md`
Beschreibt:
- aktuellen Umsetzungsstand
- was bereits funktioniert
- was teilweise umgesetzt ist
- bekannte Probleme
- technische Schulden
- offene Risiken

#### `ROADMAP.md`
Beschreibt:
- nächste sinnvolle Schritte
- geplante Ausbaustufen
- priorisierte Features
- spätere Integrationen
- Themen, die noch bewusst zurückgestellt sind

### Modulorientierte Struktur

Bitte schneide die Struktur so, dass insbesondere folgende Module als eigenständige Bereiche erkennbar werden:

- Kamera / Integration
- Stream / Frame-Verteilung
- Recording / Speicherung
- Anzeige / OpenCV-Prototyp
- gemeinsame Datenmodelle
- ROI-Grundlagen
- Fokus-Grundlagen
- später Tracking / Kantenanalyse
- später API / externe Schnittstellen

### Organisatorisches Ziel

Die Struktur soll so beschaffen sein, dass spätere Arbeiten gezielt pro Modul delegiert oder von getrennten Agenten bearbeitet werden können, ohne dass jedes Mal das gesamte Repository neu verstanden werden muss.
