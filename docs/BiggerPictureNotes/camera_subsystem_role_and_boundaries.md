# camera_subsystem_role_and_boundaries

## Zweck

Diese Note legt fuer das bestehende Kamera-Repository die Rollen- und Grenzlesart fest, die fuer die Integrationsvorstufe benoetigt wird.

Sie beantwortet nicht die komplette Endarchitektur des Gesamtprojekts.
Sie legt nur verbindlich fest, wie das heutige Repo jetzt gelesen werden soll, damit die aktuelle Phase stabil bleibt und spaetere Gesamtintegration nicht verbaut wird.

---

## Camera Core / Subsystem

Als `Camera Core / Subsystem` ist im heutigen Repo vor allem zu lesen:

- `vision_platform.bootstrap`
- `vision_platform.control.command_controller`
- `camera_app.services.camera_service`
- `camera_app.services.snapshot_service`
- `camera_app.services.recording_service`
- `vision_platform.services.stream_service`
- capability-nahe Servicepfade
- die kameraorientierten Modelle fuer Status, Requests, Frames und Recording

### Bedeutet architektonisch

Hier liegt die kameraeigene Fach- und Laufzeitlogik:
- Kamerazugriff
- Initialisierung
- Konfiguration
- Snapshot
- Recording
- Akquisition
- kameraeigene Status- und Fehlerlagen

Diese Schicht ist der eigentliche Subsystem-Kern.

---

## Camera Integration Surface

Als `Camera Integration Surface` ist im heutigen Repo zu lesen:

- `CommandController` als host-neutrale Command-Linie
- `vision_platform.services.api_service` als transportnahe Status-/Payload-Schicht
- die lesbaren Statusmodelle
- die spaeter explizit zu machenden Kategorien:
  - `Commands`
  - `State`
  - `Events`
  - `Artifacts`
  - `Health`

### Bedeutet architektonisch

Die Integration Surface ist die fachlich lesbare Aussenflaeche des Kamera-Subsystems.

Sie ist nicht identisch mit:
- CLI
- REST
- LabVIEW-Mapping
- Shell-IPC

Diese sind Adapter ueber der Surface.

---

## Optionale Companion-Schicht / VisionApp

Als `Companion-Schicht` ist im heutigen Repo vor allem zu lesen:

- `vision_platform.apps.local_shell`
- `captures/wx_shell_sessions`
- shellnahe Reflection- und Control-Pfade
- OpenCV-/lokale Frontendpfade

### Bedeutet architektonisch

Die lokale Shell ist:
- wichtiger Consumer
- praktische Companion-Betriebsform
- Debug-/Diagnose- und Setup-Oberflaeche

Sie ist aber nicht:
- Besitzschicht des Kamera-Verhaltens
- primaere Definition des Modulzustands
- Endarchitektur der Gesamtintegration

Die richtige Lesart ist daher:

`Companion ueber Core`, nicht `App besitzt Modul`.

---

## Was klar Uebergangsmechanismus ist

Folgende Dinge sind im heutigen Repo als Uebergang, nicht als Zielarchitektur, zu lesen:

- file-basierte Shell-Live-Sync-Bridge
- `captures/wx_shell_sessions` als IPC- und Reflexionspfad
- shell-spezifische Reflection-Payloads als Zustandsprojektionen
- Mischformen, in denen Eventcharakter, Statusprojektion und Artefaktspuren in denselben Pfaden auftauchen
- direkte Restabhaengigkeiten von `vision_platform` auf `camera_app`, soweit sie nur aus der Migrationslage entstehen

Diese Dinge duerfen in der aktuellen Phase bleiben.
Sie duerfen aber nicht stillschweigend die Zielarchitektur definieren.

---

## Abgrenzung zu Orchestrator

Das Camera-Subsystem ist orchestrierbar, aber nicht selbst der Orchestrator.

### Camera liefert

- Commands
- State
- spaeter Runtime-Events
- Artifacts
- Health

### Orchestrator verantwortet

- moduluebergreifende Ablaufregie
- Lebenszyklusabhaengigkeiten zwischen Modulen
- Reaktion auf Faults und Degraded-Zustaende im Gesamtsystem

Wichtige Lesart:

Die heutige hostnahe Command-Sprache ist eine brauchbare Vorstufe, aber noch nicht die vollstaendige Orchestrator-Sprache.

---

## Abgrenzung zu Logging

Das Camera-Subsystem ist Artefaktproduzent, aber nicht das systemweite Logging.

### Camera verantwortet

- Snapshot- und Recording-Artefakte
- artefaktnahe Metadaten
- lokale Traceability
- kameraeigene Zeit- und Konfigurationskontexte

### Systemweites Logging verantwortet spaeter

- moduluebergreifende Korrelation
- Session- und Run-Einordnung
- gemeinsame Audit-Chronik
- Rekonstruktion ueber mehrere Module

Wichtige Lesart:

`recording_log`, `saved_artifact_traceability` und aehnliche Pfade sind subsystemlokale Nachvollziehbarkeit, nicht automatisch das zentrale Loggingmodell.

---

## Abgrenzung zu Safety

Das Camera-Subsystem kann Safety-relevante Signale liefern, ist aber nicht das Safety-Modul.

### Camera kann exportieren

- `faulted`
- `degraded`
- `last_error`
- capability-bezogene Warnsignale
- spaeter gegebenenfalls `heartbeat_missing`, `trigger_unavailable`, `recording_failed`

### Safety verantwortet spaeter

- Priorisierung und Bewertung dieser Signale im Gesamtsystem
- Supervisor-Reaktionen
- globale Safety-Politik

Wichtige Lesart:

Camera liefert Signale.
Safety bewertet die Systemrelevanz.

---

## Kurzfristig verbindliche Rollenlesart

Fuer die aktuelle Repo-Phase sollte verbindlich gelten:

1. `Camera Core / Subsystem`
   - ist der wiederverwendbare Kern

2. `Camera Integration Surface`
   - ist die kleinste explizite Integrationsvorstufe ueber dem Kern

3. `Companion-Schicht / VisionApp`
   - ist ein wichtiger Consumer und aktueller Betriebsmodus
   - aber nicht die Besitzschicht des Kamera-Moduls

4. `Shell-Bridge`
   - ist ein Uebergangsmechanismus

Diese vier Lesarten reichen aus, um die aktuelle Hybrid-Companion-Phase zu stabilisieren und die spaetere Gesamtintegration vorzubereiten.

---

## Was kurzfristig verbindlich nicht passieren soll

Die folgende Negativliste ist fuer die aktuelle Repo-Arbeit verbindlich.

- Die Shell darf nicht zur primaeren `Camera Integration Surface` umgedeutet werden.
- subsystemlokale Traceability darf nicht als systemweites Logging gelesen werden.
- Orchestrator-Logik darf nicht in das Camera-Subsystem hineingezogen werden.
- Safety-Bewertung darf nicht in das Camera-Subsystem hineingezogen werden.
- shellnahe Reflection-Pfade duerfen nicht stillschweigend den eigentlichen Modulzustand definieren.
- der aktuelle Uebergangs-IPC-Pfad darf nicht als Zielarchitektur eingefroren werden.

---

## Ergebnis

Die zentrale Grenzentscheidung fuer das bestehende Repo lautet:

Das Repo ist nicht als `Kamera-App mit etwas Host-Steuerung` zu lesen.

Es ist zu lesen als:
- `Camera Core / Subsystem`
- `Camera Integration Surface`
- `optionale Companion-Schicht`

mit einer Reihe bewusst markierter Uebergangsmechanismen.

Diese Lesart ist die notwendige Vorstufe, bevor spaetere Lifecycle-, Event-, Health- und Logging-Ausbaustufen sauber anschliessen koennen.
