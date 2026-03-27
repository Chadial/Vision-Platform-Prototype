Arbeite in diesem Repository als Reorganisations- und Architektur-Agent für eine modulare Vision-Plattform.

WICHTIG: Verwende die bestehenden Root-Dokumente als verbindliche Referenz und vermeide inhaltliche Dopplung:
- `ProjectDescription.md` = fachliche Quelle der Wahrheit für Zielbild, Module, Use Cases, Nicht-Ziele, Architekturprinzipien, Arbeitspakete, MVP und Ausbaupfade
- `GlobalRoadmap.md` = Master-Roadmap für Entwicklungsphasen, Technologiepfade und Priorisierung
- `ProjectAgents.md` = Arbeitsanweisung für Reorganisation, Modulbildung, Dokumentationspflichten und schrittweises Vorgehen

Wenn es Widersprüche gibt, gilt diese Priorität:
1. `ProjectDescription.md`
2. `ProjectAgents.md`
3. `GlobalRoadmap.md`

DEINE AUFGABE:
Führe das bestehende Kamera-/Stream-/Speicher-Repository schrittweise in eine modulare Vision-Plattform über, ohne unnötig funktionierenden Bestand zu zerstören. Reorganisiere das Repo so, dass es die in `ProjectDescription.md` definierte Plattformstruktur vorbereitet und gleichzeitig die in `GlobalRoadmap.md` beschriebene Entwicklungslogik sinnvoll weiterführt. Nutze `ProjectAgents.md` als operatives Vorgehensmodell.

ARBEITSPRINZIPIEN:
- Kein Big-Bang-Refactoring
- Bestehende Funktionalität möglichst erhalten oder zeitnah wiederherstellen
- Erst analysieren, dann Zielstruktur anlegen, dann kontrolliert migrieren
- UI, Hardwarezugriff, Kernlogik und spätere Schnittstellen sauber trennen
- Python-Prototyping erhalten, aber Kernstrukturen C#-kompatibel anlegen
- Keine monolithische `utils.py`-Welt aufbauen
- Keine unnötige Doppelbeschreibung dessen, was bereits in den drei Root-Dokumenten steht

KONKRETE ZIELE DIESER RUNDE:
1. Lies und berücksichtige `ProjectDescription.md`, `GlobalRoadmap.md` und `ProjectAgents.md`.
2. Analysiere die aktuelle Repo-Struktur und dokumentiere den Ist-Zustand.
3. Lege eine neue modulare Zielstruktur für das Repository an.
4. Migriere vorhandene Kernbereiche kontrolliert:
   - Kamera-/Integrationslogik
   - Stream-/Frame-Logik
   - Recording-/Speicherlogik
   - bestehender OpenCV-Prototyp oder vergleichbarer Einstiegspunkt
5. Lege vorbereitende Basismodule an für:
   - gemeinsame Datenmodelle
   - ROI-Grundlagen
   - Fokus-Grundlagen
6. Sorge dafür, dass das Repository nicht nur technisch, sondern auch organisatorisch modular wird.

MODULARE ORGANISATION IST PFLICHT:
Jedes größere Modul ist als eigenständiger Arbeitsbereich zu behandeln, der später separat weiterentwickelt oder durch einen eigenen Agentenlauf bearbeitet werden kann.

Für jedes wesentliche Modul müssen mindestens diese Dateien existieren:
- `README.md`
- `STATUS.md`
- `ROADMAP.md`

Lege diese Struktur nicht nur für bereits aktive Module an, sondern auch für klar vorbereitete Erweiterungsmodule, wenn das sinnvoll ist.

MINDESTENS FOLGENDE MODULBEREICHE SOLLEN ERKENNBAR SEIN ODER VORBEREITET WERDEN:
- `integrations/camera/`
- `services/stream_service/`
- `services/recording_service/`
- `apps/opencv_prototype/`
- `libraries/common_models/`
- `libraries/roi_core/`
- `libraries/focus_core/`

Spätere oder vorbereitete Bereiche dürfen ebenfalls strukturell angelegt werden, wenn dies sauber und leichtgewichtig erfolgt:
- `libraries/tracking_core/`
- `services/api_service/`
- `apps/postprocess_tool/`
- `apps/desktop_app/`

GLOBALROADMAP ANPASSEN:
Passe `GlobalRoadmap.md` an die Plattformsicht aus `ProjectDescription.md` an, ohne die bisherige Python->C#->WebUI-Entwicklungslinie zu verlieren.

Dabei gilt:
- `GlobalRoadmap.md` soll von einer kamera-zentrierten Roadmap zu einer plattformweiten Master-Roadmap werden
- die vorhandene Python/C#/WebUI-Logik soll erhalten bleiben, aber als Technologie- und Evolutionspfad innerhalb der größeren Plattform erscheinen
- nimm die Plattformmodule sichtbar in die Roadmap auf:
  - Kamera / Integration
  - Stream / Frame-Pipeline
  - Recording / Speicherung
  - Anzeige / Interaktion / Overlay
  - ROI / Masken
  - Fokus global / lokal
  - Kanten / Tracking / Driftlogik
  - API / Feed / externe Systeme
  - Postprocess
  - mehrere Frontends
- ergänze die Reorganisation des bestehenden Repos als frühe Phase
- verlagere modulnahe Detailplanung perspektivisch in die jeweiligen Modul-`ROADMAP.md`
- `GlobalRoadmap.md` bleibt die Master-Roadmap, nicht das Detailarbeitsblatt jedes Moduls

ROOT-DOKUMENTATION ERGÄNZEN ODER AKTUALISIEREN:
Lege oder aktualisiere diese Dateien:
- `docs/project_overview.md`
- `docs/current_state.md`
- `docs/target_structure.md`
- `docs/migration_plan.md`
- optional `docs/architecture_principles.md`
- zusätzlich `MODULE_INDEX.md` im Repo-Root

`MODULE_INDEX.md` soll kurz und klar enthalten:
- vorhandene Root-Leitdokumente
- aktuelle aktive Module
- vorbereitete spätere Module
- kurzer Reifegrad / Status pro Modul
- Verweis auf jeweilige `README.md`, `STATUS.md`, `ROADMAP.md`

INHALT DER MODULDOKUMENTE:
`README.md`
- Ziel des Moduls
- Verantwortungsbereich
- zentrale Funktionen
- Inputs / Outputs
- Abhängigkeiten
- Start- oder Nutzungshinweise, falls sinnvoll

`STATUS.md`
- aktueller Umsetzungsstand
- was bereits funktioniert
- was teilweise umgesetzt ist
- bekannte Probleme
- technische Schulden
- Risiken

`ROADMAP.md`
- nächste sinnvolle Schritte
- priorisierte Features
- spätere Integrationen
- bewusst zurückgestellte Themen

TESTS UND LAUFFÄHIGKEIT:
- Breche bestehende lauffähige Kernfunktionen nicht unnötig
- Passe Imports und Startpfade nach der Reorganisation an
- Wenn Tests existieren, migriere sie sinnvoll mit
- Wenn kaum Tests existieren, ergänze minimale Smoke-Tests oder dokumentiere manuelle Prüfpfade
- Nach dieser Runde soll möglichst mindestens Folgendes noch funktionieren oder wiederhergestellt sein:
  - Kamera-/Frame-Initialisierung
  - Livebildanzeige
  - Snapshot oder Bildspeicherung
  - ein startbarer prototypischer Einstiegspunkt

ARBEITSREIHENFOLGE:
Phase 1 – Analyse
- Repo-Struktur lesen
- bestehende Einstiegspunkte identifizieren
- Kamera-, Stream-, Anzeige- und Speicherlogik identifizieren
- Kopplungen, globale Zustände und Risiken dokumentieren

Phase 2 – Zielstruktur anlegen
- neue Ordner anlegen
- Dokumentation vorbereiten
- Modulbereiche und Modul-Dokumente anlegen
- noch nicht blind alles verschieben

Phase 3 – Vorhandene Kernbereiche migrieren
- Kamera-/Integrationslogik
- Stream-/Frame-Logik
- Recording-/Speicherlogik
- OpenCV-Prototyp-Einstiegspunkt

Phase 4 – Basismodelle und vorbereitende Kernmodule ergänzen
- gemeinsame Modelle
- ROI-Grundmodule
- Fokus-Grundmodule
- Root-Index und Modul-Dokumentation konsolidieren

Phase 5 – Bereinigung
- Imports korrigieren
- alte Pfade reduzieren
- unnötige Doppelungen identifizieren
- Startanleitung und Moduldokumente aktualisieren
- GlobalRoadmap synchronisieren

WICHTIGE INHALTLICHE LEITLINIEN:
- Nutze `ProjectDescription.md` als fachliche Referenz für Plattformmodule, Betriebsmodi, Architekturprinzipien, Voraussetzungen, Risiken, MVP und Ausbaupfade
- Nutze `GlobalRoadmap.md` als Entwicklungsrahmen, aber erweitere sie auf die Plattformsicht
- Nutze `ProjectAgents.md` als direkte Handlungsanweisung für Reorganisation und Modulorganisation
- Wiederhole diese Inhalte nicht unnötig, sondern verweise implizit durch konsistente Struktur und passende Dokumente darauf

ERWARTETES ERGEBNIS DIESER RUNDE:
- erkennbar neu strukturierte Repo-Basis
- aktualisierte plattformweite `GlobalRoadmap.md`
- ergänztes `MODULE_INDEX.md`
- erste sauber definierte Modulbereiche
- pro Modul `README.md`, `STATUS.md`, `ROADMAP.md`
- dokumentierter Ist-Zustand, Zielzustand und Migrationspfad
- migrierter und weiterhin nutzbarer Basiskern
- klar vorbereitete Erweiterungspunkte für ROI, Fokus und spätere Analyse

AUSGABEFORMAT AM ENDE:
Liefere eine strukturierte Zusammenfassung mit:
1. Analyse des bisherigen Zustands
2. durchgeführten Strukturänderungen
3. neu angelegten Modulbereichen
4. verschobenen oder angepassten Dateien
5. Änderungen an `GlobalRoadmap.md`
6. angelegtem `MODULE_INDEX.md`
7. offenen Punkten / Risiken
8. konkreten nächsten empfohlenen Schritten
9. kurzer Baumstruktur des neuen Repos
10. Hinweis, was jetzt lauffähig ist und was bewusst nur vorbereitet wurde

Beginne mit einer Bestandsaufnahme und einer kurzen Migrationsstrategie, bevor du größere Dateioperationen ausführst.