# camera_integrationsvorstufe_operationalisierung_und_erste_wps

## 1. Kurzfazit

Die Integrationsvorstufe sollte jetzt als **kleine, explizite Schicht ueber dem bestehenden Kern** gelesen werden, nicht als neue Technikplattform.

Der kleinste sinnvolle erste Schnitt ist:
- vorhandenen Kern nicht umbauen
- vorhandene Host-/Status-/Payload-Logik nicht ersetzen
- stattdessen eine explizite Surface-Sicht ueber bereits existierende Bausteine legen
- danach gezielt `GetHealth`, `GetCapabilities`, `CameraHealth` und die minimale Eventfamilie nachziehen

Der richtige erste Fokus ist also:

**nicht neues Verhalten bauen, sondern vorhandene Repo-Realitaet in eine explizite Integrationsvorstufe ueberfuehren**

---

## 2. Operationalisierung der Integrationsvorstufe

### Surface v0.1

#### Heute vorhanden

- `vision_platform.bootstrap`
- `vision_platform.control.command_controller.CommandController`
- `camera_app.services.camera_service.CameraService`
- `camera_app.services.snapshot_service.SnapshotService`
- `camera_app.services.recording_service.RecordingService`
- `vision_platform.services.api_service`
- Statusmodelle:
  - `SubsystemStatus`
  - `CameraStatus`
  - `RecordingStatus`
  - `IntervalCaptureStatus`
- CLI:
  - `vision_platform.apps.camera_cli`

#### Direkt wiederverwendbar

- `CommandController` als faktische v0.1-Command-Surface
- `api_service`-Payloads als Basis fuer surface-lesbare DTO-Sicht
- vorhandene Statusmodelle als Rohmaterial fuer pollbaren State
- vorhandene Snapshot-/Recording-Resultate als Basis fuer Artifact-Sicht

#### Zu praezisieren

- explizite Surface-Definition:
  - welche Commands zur Surface gehoeren
  - welcher pollbare State minimal verbindlich ist
  - welche Result-/Payload-Formen Surface und welche nur Adapterformen sind
- Trennung zwischen:
  - Surface
  - Adapter
  - shellnaher Reflection

#### Spaeter

- finale Transportform
- finale DTO-Familien fuer alle Adapter
- vollstaendige Orchestrator-Lifecycle-Sprache

### Health

#### Heute vorhanden

- `last_error`-Felder
- `can_*`-Flags
- capability-bezogene Warnungen
- Audit-Signale
- failure-reflection-Pfade im Companion-Betrieb

#### Direkt wiederverwendbar

- `CameraStatus`
- `SubsystemStatus`
- `RecordingStatus`
- `IntervalCaptureStatus`
- `HardwareAuditService`-nahe Signale

#### Zu praezisieren

- ein explizites `CameraHealth`-Modell mit:
  - `availability`
  - `readiness`
  - `degraded`
  - `faulted`
  - `last_error`
  - `capabilities_available`
  - `capability_probe_warning`
  - optional ableitbar: `recording_failed`

#### Spaeter

- feinere Fault-Taxonomie
- `heartbeat_missing`
- `trigger_unavailable`
- Safety-nahe Klassifikation ueber reinen Camera-Scope hinaus

### Events

#### Heute vorhanden

- eventartiger Charakter in:
  - `saved_artifact_traceability.csv`
  - `recording_log.csv`
  - `hardware_audit.jsonl`
  - shellnahen Result-/Status-Dateien

#### Direkt wiederverwendbar

- bestehende Snapshot-/Recording-/Konfigurationsfluesse als Producer-Orte
- vorhandene Result-Payloads als Ausgangspunkt fuer Event-Benennung

#### Zu praezisieren

- minimale Runtime-Eventfamilie:
  - `CameraConfigurationApplied`
  - `CameraSnapshotSaved`
  - `CameraRecordingStarted`
  - `CameraRecordingStopped`
  - `CameraFaulted`
  - `CameraHealthChanged`
- klare Trennung:
  - Event != Artefaktlog
  - Event != Status
  - Event != shellnahes Resultfile

#### Spaeter

- Event-Transport
- Event-Bus
- Subscription-/Delivery-Semantik

### Artifacts

#### Heute vorhanden

- Snapshot-Dateien
- Recording-Artefakte
- `recording_log.csv`
- `saved_artifact_traceability.csv`
- artifactnahe Felder in Result- und Statuspfaden

#### Direkt wiederverwendbar

- Snapshot-/Recording-Ergebnisse
- Traceability-Zeilen
- `run_id`, `frame_id`, `saved_path`, `camera_timestamp`, `system_timestamp_utc`

#### Zu praezisieren

- minimale ArtifactReference-Sicht:
  - `artifact_path`
  - `artifact_kind`
  - `save_directory`
  - `file_name`
  - `run_id`, falls vorhanden
  - `frame_id`, falls vorhanden
  - `camera_id`, falls vorhanden
  - Zeitkontext
- harte Lesart:
  - subsystemlokale Artefaktlogik != Gesamtlogging

#### Spaeter

- explizite `ArtifactReference`-/`ArtifactMetadata`-DTOs
- sauberere Trennung von Artefaktindex, Traceability und Audit

### Zeitkontext

#### Heute vorhanden

- `camera_timestamp`
- `system_timestamp_utc`
- `frame_id`
- interne monotone Zeiten in Recording-/Interval-Logik

#### Direkt wiederverwendbar

- Zeitfelder in `CapturedFrame`
- Zeitfelder in `FrameMetadata`
- Traceability-/Recording-Log-Pfade

#### Zu praezisieren

- minimaler Zeitkontext:
  - `device_timestamp`
  - `host_utc`
  - `host_monotonic`
  - `frame_id`
  - `time_source` oder `time_quality`

#### Spaeter

- vollstaendiges Clock-Domain-Modell
- systemweite Zeitkorrelation ueber mehrere Module

### Companion-/Uebergangsgrenzen

#### Heute vorhanden

- `apps/local_shell`
- `captures/wx_shell_sessions`
- file-basierte Shell-Live-Sync
- companion-spezifische Reflection-Pfade

#### Direkt wiederverwendbar

- Companion-Betrieb als aktueller Nutzungsmodus
- Shell als sichtbarer Consumer des Kerns

#### Zu praezisieren

- Shell ist nicht primaere Surface
- Shell-Result-/Status-Dateien sind keine Runtime-Endarchitektur
- Shell-Bridge ist Uebergang, nicht Zielmodell

#### Spaeter

- host-neutralere Command-/Session-Seams
- Abbau historischer Restkopplungen

---

## 3. WP-01 bis WP-04 in voller Struktur

### WP-01

**Titel**  
Camera Integration Surface v0.1 explizit machen

**Ziel**  
Die vorhandenen Commands, Statusmodelle, Payloads und Service-Einstiegspunkte als kleine, explizite `Camera Integration Surface v0.1` rahmen.

**Warum jetzt**  
Weil der Kern bereits da ist, aber seine Aussenflaeche noch zu implizit gelesen wird. Ohne diesen Schritt laufen Health, Events und spaetere Integrationslogik wieder in uneinheitliche Richtungen.

**Scope**
- vorhandene Surface-Bausteine explizit benennen
- verbindliche Minimaldefinition fuer:
  - Commands
  - State
  - Events
  - Artifacts
  - Health
- vorhandene Klassen und Services auf diese Sicht abbilden
- klare Trennung zwischen Surface, Adapter und Companion-Reflection

**Explizit nicht Teil dieses WPs**
- neue Laufzeitarchitektur
- Event-Bus
- neue Transportadapter
- Ersetzung der Shell-Bridge
- Umbau der Kernservices

**Betroffene Repo-Bereiche / Dateien / Services**
- `vision_platform.control.command_controller`
- `vision_platform.services.api_service`
- `camera_app.services.camera_service`
- `camera_app.services.snapshot_service`
- `camera_app.services.recording_service`
- Statusmodelle unter `camera_app.models`
- `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`

**Abhaengigkeiten**
- `camera_integration_surface_v0.1.md`
- `camera_subsystem_role_and_boundaries.md`

**Risiken**
- zu generisch formuliert und damit fuer die Repo-Arbeit wertlos
- Surface mit Adapterformen vermischt
- shellnahe Reflection unbemerkt als Surface missverstanden

**Erwartetes Ergebnis**
- eine verbindliche v0.1-Surface-Referenz
- klare Liste, was bereits Surface ist und was nur Adapter oder Uebergang ist

**Wie dieses WP auf die Integrationsvorstufe einzahlt**
- es ist der eigentliche Startpunkt der Vorstufe
- ohne dieses WP bleiben alle Folgearbeiten begrifflich unscharf

### WP-02

**Titel**  
GetHealth und GetCapabilities als echte Surface-Calls schaerfen

**Ziel**  
Capability- und health-nahe Bestandslogik so explizit machen, dass sie als echte Surface-Bestandteile gelesen und spaeter konsistent genutzt werden koennen.

**Warum jetzt**  
Weil `GetHealth` und `GetCapabilities` die kleinste sinnvolle Erweiterung der bestehenden Surface sind, die schon jetzt spaetere Orchestrator-, Logging- und Safety-Anschlussfaehigkeit verbessert, ohne die aktuelle Phase umzubauen.

**Scope**
- vorhandene capability-nahe Logik identifizieren und als Surface-call rahmen
- vorhandene health-nahe Rohsignale identifizieren
- minimale Ergebnisform fuer `GetHealth` und `GetCapabilities` definieren
- bestehende Command-/Status-/Payload-Sicht daran ausrichten

**Explizit nicht Teil dieses WPs**
- vollstaendige Lifecycle-Sprache
- vollstaendige Safety-Politik
- komplexes Capability-Profil-Management
- neue Transportarchitektur

**Betroffene Repo-Bereiche / Dateien / Services**
- `vision_platform.control.command_controller`
- capability-nahe Services
- `vision_platform.services.api_service`
- `CameraStatus`
- `SubsystemStatus`
- `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`

**Abhaengigkeiten**
- WP-01 sollte zuerst die Surface definieren
- vorhandene capability- und statusnahe Logik muss lesbar inventarisiert sein

**Risiken**
- `GetHealth` bleibt nur umbenannter Status
- `GetCapabilities` wird zu internem Detail statt stabilem Surface-call
- zu viel Endarchitektur in die Calls hineingedacht

**Erwartetes Ergebnis**
- klar benannte Surface-Calls `GetHealth` und `GetCapabilities`
- kleine, stabile Minimalfelder dafuer
- weniger Drift zwischen impliziter Logik und explizitem Integrationsvertrag

**Wie dieses WP auf die Integrationsvorstufe einzahlt**
- es macht zwei der wichtigsten noch fehlenden Surface-Bestandteile explizit
- es schafft die Bruecke zwischen heutigem Repo-Zustand und spaeterem Integrationsbedarf

### WP-03

**Titel**  
CameraHealth-Modell einfuehren

**Ziel**  
Ein kleines, explizites `CameraHealth`-Modell definieren, das ueber `last_error` und `can_*` hinausgeht, ohne schon Supervisor-Logik zu bauen.

**Warum jetzt**  
Weil Health die zentrale Bruecke ist zwischen:
- Camera intern
- spaeterem Orchestrator
- spaeterem Logging
- spaeteren Safety-Konsumenten

Wenn dieser Schritt zu spaet kommt, verfestigt sich wieder Fehlertext- und Flagdenken.

**Scope**
- `CameraHealth` minimal definieren
- Ableitungsbasis aus vorhandenem Statusbestand festlegen
- minimale Health-Felder festziehen:
  - `availability`
  - `readiness`
  - `degraded`
  - `faulted`
  - `last_error`
  - capability-bezogene Warnsicht
- Abgrenzung zu Safety-Bewertung explizit festhalten

**Explizit nicht Teil dieses WPs**
- globale Safety-Politik
- Supervisor-Reaktionen
- detaillierte Fault-Taxonomie
- Event-Bus fuer Health-Aenderungen

**Betroffene Repo-Bereiche / Dateien / Services**
- `CameraStatus`
- `SubsystemStatus`
- `RecordingStatus`
- `IntervalCaptureStatus`
- capability-nahe Services
- auditnahe Warn-/Incident-Pfade
- `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`

**Abhaengigkeiten**
- WP-01
- sinnvollerweise vorbereitet durch WP-02

**Risiken**
- Health wird zu gross und zu abstrakt
- Health wird mit globaler Safety vermischt
- Health bleibt nur neue Huelle um `last_error`

**Erwartetes Ergebnis**
- kleines, explizites `CameraHealth`
- klare Ableitungslogik aus vorhandenem Repo-Bestand
- bessere Surface-Lesbarkeit ohne Architekturueberbau

**Wie dieses WP auf die Integrationsvorstufe einzahlt**
- es stabilisiert die Surface dort, wo heute die groesste semantische Luecke ist
- es bereitet spaetere Orchestrator- und Safety-Anschluesse vor, ohne sie vorwegzunehmen

### WP-04

**Titel**  
Minimale Runtime-Eventfamilie vorbereiten

**Ziel**  
Die erste Runtime-Eventfamilie als echte Integrationskategorie festhalten und an den vorhandenen Flows verankern, ohne schon Event-Infrastruktur zu bauen.

**Warum jetzt**  
Weil das Repo heute schon eventartigen Charakter produziert, aber noch alles zwischen:
- Traceability
- Status
- Result-Payload
- Audit
- Companion-Dateien

vermischt. Diese semantische Trennung sollte frueh erfolgen.

**Scope**
- minimale Runtime-Eventfamilie benennen
- Producer-Orte im bestehenden Repo benennen
- Trennung zwischen:
  - Event
  - State
  - Artifact
  - shellnahem Result
  klar festhalten
- erste strukturierte Anschlussfaehigkeit dokumentieren

**Explizit nicht Teil dieses WPs**
- Event-Bus
- Delivery-Garantien
- Subscription-Modell
- globale Logging-Architektur

**Betroffene Repo-Bereiche / Dateien / Services**
- `CommandController`
- Snapshot-/Recording-Flows
- `saved_artifact_traceability.csv`
- `recording_log.csv`
- `hardware_audit.jsonl`
- shellnahe Result-/Status-Dateien
- `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`

**Abhaengigkeiten**
- WP-01
- WP-03 ist hilfreich, weil `CameraHealthChanged` sonst semantisch zu schwach bleibt

**Risiken**
- Event-Sprache bleibt zu theoretisch
- Artefaktlogs werden weiter als Event-Ersatz gelesen
- der Schritt kippt in Bus-/Transportdesign

**Erwartetes Ergebnis**
- klar benannte minimale Runtime-Eventfamilie
- klar benannte Producer-Orte
- saubere Trennung von Event, State, Artifact und Companion-Datei

**Wie dieses WP auf die Integrationsvorstufe einzahlt**
- es macht die v0.1-Surface erstmals mehrdimensional lesbar
- es verhindert, dass spaetere Gesamtintegration auf impliziten Pseudo-Events aufbaut

---

## 4. Optional WP-05 bis WP-07 kurz

### WP-05

**Titel**  
Artefaktreferenzen und Artefaktgrenzen schaerfen

Kurz:
- Artefaktreferenzen als explizite Surface-Sicht aus Snapshot-/Recording-/Traceability-Bestand ableiten
- subsystemlokale Artefaktlogik klar gegen Gesamtlogging abgrenzen

### WP-06

**Titel**  
Minimalen Zeitkontext strukturieren

Kurz:
- `device_timestamp`, `host_utc`, `host_monotonic`, `frame_id`, `time_source/time_quality` als kleinen verbindlichen Zeitkontext festziehen
- noch kein grosses Clock-Domain-System bauen

### WP-07

**Titel**  
Companion-Bridge als Uebergang explizit markieren

Kurz:
- shellnahe Reflection- und file-basierte Bridge in Doku und Lesart entzaubern
- nicht ersetzen, aber klar als Zwischenzustand rahmen

---

## 5. Vorschlag fuer Roadmap-Anpassung

Die vorhandene Roadmap sollte nicht ersetzt, sondern um eine **explizite Integrationsvorstufe innerhalb der aktuellen Phase** erweitert werden.

Empfehlung:
- keine neue grosse Gesamtphase
- keine komplette Umnummerierung
- stattdessen in der aktuellen Phase einen sichtbaren Vor-Schritt ergaenzen

Die Lesart sollte sein:

### Kurzfristig

- `Camera Integration Surface v0.1`
- Rollen-/Grenzenklarheit
- minimales Health-Modell
- minimaler Zeitkontext
- Shell-Bridge als Uebergang markieren

### Mittelfristig

- Runtime-Events ausbauen
- Lifecycle-Sprache erweitern
- Artefakt-/Logging-Grenzen schaerfen
- Orchestrator-Anschlussfaehigkeit verbessern

### Noch nicht festzurren

- finaler Transport
- finaler Event-Bus
- komplette Safety-Politik
- komplette historische Entkopplung
- grosse Endarchitektur im Repo

Wenn diese Operationalisierung spaeter in konkrete Repo-Arbeit ueberfuehrt wird, ist der naechste Schritt nicht mehr eine weitere Architektur-Note, sondern die Ueberfuehrung von WP-01 bis WP-04 in echte Workpackage-Dateien oder in einen geschaerften Abschnitt von `docs/WORKPACKAGES.md`.

---

## 6. Wichtigste Risiken / Stolperstellen

- Die Shell-Bridge bleibt faktisch die eigentliche Surface, obwohl sie nur Uebergang sein soll.
- `GetHealth` wird nur ein umbenannter Status-Auszug und kein echter Surface-Bestandteil.
- `CameraHealth` wird zu gross oder zu safety-nah.
- Runtime-Events werden wieder nur als CSV-/JSON-Dateien beschrieben, nicht als eigene Integrationskategorie.
- Artefaktlogik wird weiter mit Gesamtlogging verwechselt.
- die Integrationsvorstufe wird zu abstrakt beschrieben und bleibt damit fuer echte Repo-Arbeit folgenlos.
- die Integrationsvorstufe wird zu gross gedacht und kippt dadurch doch wieder in Endarchitekturplanung.
