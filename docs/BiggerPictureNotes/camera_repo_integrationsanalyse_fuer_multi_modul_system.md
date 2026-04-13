# Kamera-Repo Integrationsanalyse fuer Multi-Modul-System

## Zweck

Diese Note analysiert das bestehende Kamera-Repository gezielt im Hinblick auf die spaetere Einbettung in ein groesseres Multi-Modul-System.

Die Ausgangslesart ist dabei bewusst:
- nicht `Kamera-App`
- sondern `einbettbares Camera Subsystem`

mit den drei Schichten:
- `Camera Core / Subsystem`
- `Camera Integration Surface`
- `optionale Local Shell / VisionApp`

Die Analyse ist repo-nah und betrachtet reale vorhandene Strukturen, Services, Commands, Modelle, Persistenzpfade und Shell-Mechanismen.

---

## 1. Kurzfazit

Das Repository ist bereits deutlich naeher an einem einbettbaren `Camera Subsystem` als an einer klassischen Kamera-App.

### Architektonisch bereits tragfaehig
- headless-naher Kern ueber `vision_platform.bootstrap`, `CommandController`, `CameraService`, `SnapshotService`, `RecordingService`
- host- und CLI-steuerbare Integrationsbasis ueber `vision_platform.apps.camera_cli`
- transport-neutrale Status- und Command-Envelopes ueber `vision_platform.services.api_service`
- vorhandene Capability-, Traceability- und Audit-Pfade
- optionale Local Shell / wxShell als Companion-Schicht statt als einzige Betriebsform

### Wichtigste offene Integrationspunkte
- kein explizites Orchestrator-Lifecycle-Modell
- kein first-class Runtime-Event-Modell
- kein explizites Health-Modell, sondern vor allem Statusfelder plus Fehlertexte
- Zeitmodell real vorhanden, aber exportseitig zu flach
- Shell-Live-Sync ist eine brauchbare Zwischenloesung, aber keine tragfaehige Endarchitektur
- `vision_platform` ist strukturell noch nicht vollstaendig von `camera_app`-Implementierungen entkoppelt

### Gesamtbewertung
Das Repo ist als Ausgangsbasis fuer ein spaeteres `Camera Subsystem` gut geeignet.
Es ist aber noch nicht die fertige `Camera Integration Surface` eines groesseren Orchestrator-/Logging-/Safety-Systems.
Die groessten offenen Punkte liegen weniger in Preview/Snapshot/Recording selbst als in:
- Lifecycle-Sprache
- Event-Modell
- Health-Modell
- Zeit-Provenienz
- Trennung zwischen kameraeigener Persistenz und systemischem Logging

---

## 2. Commands / State / Events / Artifacts / Health

## Commands

### Bereits vorhanden
- `apply_configuration()` in `src/vision_platform/control/command_controller.py:62`
- `set_save_directory()` in `src/vision_platform/control/command_controller.py:87`
- `save_snapshot()` in `src/vision_platform/control/command_controller.py:96`
- `start_recording()` in `src/vision_platform/control/command_controller.py:114`
- `stop_recording()` in `src/vision_platform/control/command_controller.py:132`
- `start_interval_capture()` in `src/vision_platform/control/command_controller.py:150`
- `stop_interval_capture()` in `src/vision_platform/control/command_controller.py:173`
- `get_status()` in `src/vision_platform/control/command_controller.py:196`
- CLI-Adapter ueber `src/vision_platform/apps/camera_cli/camera_cli.py`
- Shell-Control-Adapter ueber `src/vision_platform/apps/local_shell/control_cli.py`

### Teilweise vorhanden / implizit
- `initialize()` und `shutdown()` in `src/camera_app/services/camera_service.py:26`
- Preview-Start ueber Stream-Service statt ueber zentrale Integration Surface
- Capability-Probe ueber `CameraService` und `CameraCapabilityService`, aber nicht als stabiler Integrations-Command

### Fehlt noch
- `Prepare`
- `Arm`
- `Abort`
- `Recover`
- `GetHealth`
- `GetCapabilities`
- explizite Trennung zwischen Modul-Lifecycle-Commands und kamera-lokalen Capture-Commands

## State

### Bereits vorhanden
- `SubsystemStatus` in `src/camera_app/models/subsystem_status.py:12`
- `CameraStatus` in `src/camera_app/models/camera_status.py:6`
- `RecordingStatus` in `src/camera_app/models/recording_status.py:7`
- `IntervalCaptureStatus` in `src/camera_app/models/interval_capture_status.py:7`
- transport-neutrales Status-Mapping ueber `src/vision_platform/services/api_service/status_payloads.py:87`

### Teilweise vorhanden / implizit
- Shell-spezifische Reflection-States und Companion-Snapshots ueber `src/vision_platform/services/companion_contract_service.py`
- Focus-/ROI-bezogene Zustandsausschnitte in Shell-Status, aber nicht als allgemeine Integrationssurface
- `can_*`-Flags in `SubsystemStatus` als primitive Readiness-Ableitungen

### Fehlt noch
- Lifecycle-State des Moduls
- Readiness mit Gruenden statt nur Bool-/`can_*`-Ableitungen
- Health-State als eigene Ebene
- Run-/Session-Kontext-State
- Restriction-/Lock-State als first-class Integrationsdaten

## Events

### Bereits vorhanden
- Artefaktnahe Run-Marker und Trace-Zeilen in `src/vision_platform/services/recording_service/traceability.py`
- Hardware-Audit-Ereignisse in `src/vision_platform/services/hardware_audit_service.py`
- Shell-Command-Result-Dateien und Status-Snapshots in `captures/wx_shell_sessions/...`

### Teilweise vorhanden / implizit
- `recording_log.csv` und `saved_artifact_traceability.csv` tragen Ereignischarakter, sind aber keine Runtime-Event-Oberflaeche
- `failure_reflection`, `recording_reflection`, `snapshot_reflection` in der Shell sind statusnahe Ergebnisprojektionen

### Fehlt noch
- first-class Runtime-Events wie:
  - `CameraSnapshotSaved`
  - `CameraRecordingStarted`
  - `CameraRecordingStopped`
  - `CameraFaulted`
  - `CameraHealthChanged`
  - `CameraConfigurationApplied`
  - `CameraStateChanged`

## Artifacts

### Bereits vorhanden
- Snapshot-Dateien aus `src/camera_app/services/snapshot_service.py:30`
- Recording-Frame-Dateien aus `src/camera_app/services/recording_service.py:86`
- `recording_log.csv` aus `src/vision_platform/services/recording_service/recording_log.py:7`
- `saved_artifact_traceability*.csv` aus `src/vision_platform/services/recording_service/traceability.py:13`
- `hardware_audit.jsonl` aus `src/vision_platform/services/hardware_audit_service.py:31`
- Shell-Bridge-Artefakte unter `captures/wx_shell_sessions/` aus `src/vision_platform/apps/local_shell/live_command_sync.py:36`

### Teilweise vorhanden / implizit
- Command-Result-Payloads enthalten Artefakt-Referenzen, aber nicht als explizite `ArtifactReference`-Typen
- Offline-Wiederverwendung ist vorbereitet, aber nicht als systemweites Artefaktmodell beschrieben

### Fehlt noch
- explizite Artefakt-Referenztypen fuer spaetere Systemintegration
- klare Trennung von Artefaktindex, Artefaktmetadaten und systemischem Logging

## Health

### Bereits vorhanden
- `CameraStatus.capabilities_available`
- `CameraStatus.capability_probe_error`
- `CameraStatus.last_error`
- `RecordingStatus.last_error`
- `IntervalCaptureStatus.last_error`
- Audit-Klassifikation ueber `HardwareAuditService`

### Teilweise vorhanden / implizit
- `can_*`-Felder in `SubsystemStatus`
- Shell-`failure_reflection`
- Interval-Capture-Warnungen ueber Fehlertext-Pfade

### Fehlt noch
- explizites `CameraHealth`
- `availability`
- `readiness`
- `degraded`
- `faulted`
- `heartbeat_missing`
- `trigger_unavailable`
- explizite Fehler-/Health-Taxonomie statt Freitextorientierung

---

## 3. Analyse der offenen Punkte 1-10

## 1. Lifecycle / Orchestrator-Kompatibilitaet

### Heute bereits ungefaehre Entsprechungen
- `Configure`:
  - `CommandController.apply_configuration()`
  - `CameraService.apply_configuration()`
- `Prepare`:
  - implizit ueber `CameraService.initialize()` plus optional `set_save_directory()` und `apply_configuration()`
- `Start`:
  - `start_recording()`
  - `start_interval_capture()`
- `Stop`:
  - `stop_recording()`
  - `stop_interval_capture()`
- `GetStatus`:
  - `get_status()`

### Luecken
- `Arm` fehlt als explizite Semantik vollstaendig
- `Abort` fehlt als eigener Pfad
- `Recover` fehlt als definierte Recovery-Sprache
- `GetHealth` fehlt als eigener Integrations-Call
- `GetCapabilities` fehlt als stabiler Integrations-Call
- `Prepare` ist heute eher technische Initialisierung als orchestratorfaehige Modulphase

### Kamera-lokal gedachte Commands, die fuer Orchestrator anders geraehmt werden muessen
- `set_save_directory()` ist heute subsystem-lokale Betriebslogik, nicht globaler Run-Kontext
- bounded `start_recording()` / `stop_recording()` sind heute capture-zentriert, nicht in einen Modul-Lifecycle eingebettet
- `start_interval_capture()` ist technisch vorhanden, aber im Gesamtprojekt keine offensichtliche Lifecycle-Hauptsprache
- `initialize()` / `shutdown()` sind Service-Operationen, aber noch nicht als Modul-Lifecycle-Fassade formuliert

### Architektonische Bewertung
Die heutige Struktur ist gut fuer direkte Host-Steuerung, aber noch nicht sauber als Orchestrator-Modul formuliert.
Es fehlt vor allem die Sprache fuer:
- Vorbereitungszustand
- Armierung
- Abbruch
- Recovery

## 2. Commands / State / Events / Artifacts / Health

### Commands
- bereits vorhanden: Controller-Commands, CLI-Commands, Shell-Control-Commands
- implizit: Initialisierung, Preview-Start, Capability-Probe
- fehlt: Lifecycle-Commands und explizite Health-/Capability-Abfragen

### State
- bereits vorhanden: `SubsystemStatus`, `CameraStatus`, `RecordingStatus`, `IntervalCaptureStatus`
- implizit: Shell-Reflections fuer Setup, Snapshot, Recording, Failure
- fehlt: Lifecycle-State, Run-/Session-State, Health-State, Restriction-State

### Events
- bereits vorhanden: trace-/auditartige Eventartefakte
- implizit: Shell-Result-Dateien und Statussnapshots
- fehlt: echte Runtime-Events als Integrationssurface

### Artifacts
- bereits vorhanden: Bilder, Serienframes, Audit- und Trace-Dateien
- implizit: Result-Payloads als Artefaktreferenztraeger
- fehlt: explizite Artefaktreferenztypen und saubere Abgrenzung zu Systemlogging

### Health
- bereits vorhanden: Statusflags, `last_error`, Capability-Warnings, Audit-Klassifikation
- implizit: `can_*`-Readiness und Shell-Failure-Reflection
- fehlt: explizites Health-Modell

## 3. Shell vs. Core

### Klar zum wiederverwendbaren Kamera-Kern gehoerig
- `src/vision_platform/bootstrap.py`
- `src/vision_platform/control/command_controller.py`
- `src/camera_app/services/camera_service.py`
- `src/camera_app/services/snapshot_service.py`
- `src/camera_app/services/recording_service.py`
- Stream-Services unter `src/vision_platform/services/stream_service/`
- Capability-Service unter `src/vision_platform/services/camera_capability_service.py`
- API-Payload-Mappings unter `src/vision_platform/services/api_service/`

### Klar zur VisionApp / Companion-Schicht gehoerig
- `src/vision_platform/apps/local_shell/wx_preview_shell.py`
- `src/vision_platform/apps/local_shell/control_cli.py`
- `src/vision_platform/apps/local_shell/live_command_sync.py`
- `src/vision_platform/apps/local_shell/labview_mapping.py`
- `src/vision_platform/apps/local_shell/camera_settings_service.py`

### Wo es noch Vermischung gibt
- `src/vision_platform/apps/local_shell/preview_shell_state.py` ist UI-agnostisch, liegt aber app-lokal
- `src/vision_platform/services/companion_contract_service.py` liegt in `services`, ist aber companion-spezifisch
- `vision_platform`-Kernpfade importieren noch direkt `camera_app`-Implementierungen

### Was heute noch eine saubere Lesart als `optional shell over core` behindert
- file-basierte Shell-Steuerung als zentrale Host-zu-Shell-Kollaborationsform
- shell-spezifische Reflection-Modelle in der Integrationssicht
- Restabhaengigkeit des `vision_platform`-Kerns auf `camera_app`

## 4. Logging und Artefakte

### Heute bereits vorhandene Kamera-Artefakte und Metadaten
- Snapshot-Datei
- Recording-Frame-Datei
- `recording_log.csv`
- `saved_artifact_traceability.csv`
- `hardware_audit.jsonl`
- Metadaten wie:
  - `frame_id`
  - `camera_timestamp`
  - `system_timestamp_utc`
  - `pixel_format`
  - Bildgroesse
  - `run_id`
  - Konfigurationskontext
  - ROI-/Focus-Metadaten

### Was eher lokal / kamera-intern gedacht ist
- `recording_log.csv` pro Save-Directory
- `saved_artifact_traceability.csv` pro Save-Directory
- Shell-Status- und Result-Dateien unter `captures/wx_shell_sessions/`

### Was gut an ein uebergeordnetes System-Logging anschliessbar waere
- `run_id`
- `saved_path`
- `save_directory`
- `file_stem`
- `file_extension`
- `camera_id`
- `camera_alias`
- `configuration_profile_id`
- `frame_id`
- `camera_timestamp`
- `system_timestamp_utc`
- ROI-/Focus-Metadaten
- Stop-Grund / Failure-Reflections

### Wo kameraeigene Persistenz und systemisches Logging noch vermischt sind
- `recording_log.csv` heisst Log, ist funktional aber eher Artefaktindex
- `saved_artifact_traceability.csv` ist Mischung aus Kontext, Run-Markern und Artefaktzeilen
- Shell-Result-Dateien transportieren teils IPC, teils Zustandsprojektion, teils quasi-Event-Information

### Gute Kandidaten fuer spaeteres systemweites Loggingmodell
- `SnapshotCommandResult.saved_path`
- `RecordingStatus.run_id`
- `TraceArtifactRow`
- `SubsystemStatus.configuration`
- `CameraStatus.camera_id`
- Shell-`failure_reflection`
- Shell-`snapshot_reflection`
- Shell-`recording_reflection`

## 5. Zeitmodell

### Welche Zeitinformationen heute real existieren
- `camera_timestamp`
- `frame_id`
- `timestamp_utc`
- `system_timestamp_utc`
- Recording-intern monotone Deadlines / Schedulingzeiten
- Interval-Capture-intern monotone Deadlines / Schedulingzeiten
- `run_id` mit Startzeitbezug fuer bounded recording
- Session-IDs fuer Local-Shell-Live-Sync

### Device timestamps / host timestamps / monotone Zeiten / frame indices
- device-nahe Zeit:
  - `camera_timestamp` aus Hardware-Frame bei Vimba X
  - `camera_timestamp = frame_counter` im Simulator
- host timestamps:
  - `timestamp_utc`
  - `system_timestamp_utc`
- monotone Zeit:
  - intern in Recording- und Interval-Capture-Services
- frame indices:
  - `frame_id`
  - Dateiserienindex

### Wo Zeit heute zu flach modelliert ist
- Persistenz exportiert im Wesentlichen nur `camera_timestamp` und `system_timestamp_utc`
- kein `clock_domain`
- keine `timestamp_quality`
- keine monotone Zeit im exportierten Modell
- kein strukturierter Zeitkontext fuer spaetere moduluebergreifende Korrelation

### Welche Stellen erweitert werden sollten
- `FrameMetadata` in `src/vision_platform/libraries/common_models/frame_models.py`
- `CapturedFrame` in `src/camera_app/models/captured_frame.py`
- `TraceArtifactRow` / Traceability-Logik in `src/vision_platform/services/recording_service/traceability.py`
- Status-/Event-/Artifact-DTOs der künftigen Integration Surface

## 6. Health / Safety-Anschluss

### Heute bereits brauchbare Health-Signale
- `camera.is_initialized`
- `camera.last_error`
- `camera.capabilities_available`
- `camera.capability_probe_error`
- `recording.last_error`
- `interval_capture.last_error`
- `can_*`-Flags im `SubsystemStatus`
- Audit-Warnings und Audit-Incidents ueber `HardwareAuditService`

### Gute Kandidaten fuer kuenftige Health-Felder
- `availability`:
  - `camera.is_initialized`
  - `camera_id`
  - `source_kind`
- `readiness`:
  - `can_apply_configuration`
  - `can_save_snapshot`
  - `can_start_recording`
- `degraded`:
  - `capability_probe_error`
  - `interval_capture`-Timingwarnungen
  - fehlende Capabilities bei Hardware
- `faulted`:
  - `camera.last_error`
  - `recording.last_error`
- `heartbeat_missing`:
  - heute nicht vorhanden
- `trigger_unavailable`:
  - heute nicht explizit vorhanden
- `recording_failed`:
  - implizit vorhanden ueber `recording.last_error`

### Wo die Sprache noch weiterentwickelt werden muss
Das Repo spricht heute stark in:
- `last_error`
- Warning-Strings
- Audit-Heuristiken

Fuer Safety-Anschluss braucht es staerker:
- Health-Zustaende
- Fault-Arten
- Degraded-Zustaende
- Readiness mit Gruenden

## 7. Integrationssurface

### Wenn aus dem heutigen Repo eine stabile `Camera Integration Surface` abgeleitet werden muesste

### Pflicht-Commands
- `PrepareCamera`
- `ApplyConfiguration`
- `SetSaveDirectory`
- `SaveSnapshot`
- `StartRecording`
- `StopRecording`
- `GetStatus`
- `GetHealth`
- `GetCapabilities`

### Pflicht-State-Felder
- `camera_id`
- `source_kind`
- `is_initialized`
- `is_acquiring`
- `configuration`
- `default_save_directory`
- `recording.is_recording`
- `recording.frames_written`
- `recording.run_id`
- `interval_capture.is_capturing`
- `can_*`-Faehigkeiten oder spaeter `readiness` mit Gruenden

### Pflicht-Events
- `CameraPrepared`
- `CameraConfigurationApplied`
- `CameraSnapshotSaved`
- `CameraRecordingStarted`
- `CameraRecordingStopped`
- `CameraFaulted`
- `CameraHealthChanged`

### Pflicht-Artifacts / Referenzen
- `saved_path`
- `save_directory`
- `file_name`
- `run_id`
- `frame_id`
- `camera_timestamp`
- `system_timestamp_utc`
- `camera_id`
- `configuration_profile_id`

### Pflicht-Health-Felder
- `availability`
- `readiness`
- `degraded`
- `faulted`
- `capabilities_available`
- `capability_probe_warning`
- `recording_failed`
- `last_error`

## 8. Uebergangsmechanismen

### Brauchbar als Uebergang
- file-basierte Shell-Steuerung in `src/vision_platform/apps/local_shell/live_command_sync.py`
- lokale Session-Bridge mit:
  - `active_session.json`
  - `commands.jsonl`
  - `results/*.json`
  - `status.json`
- `labview_mapping.py`
- Companion-Reflections fuer Setup/Snapshot/Recording/Failure
- `camera_app`-Shims unter `vision_platform`

### Sollte spaeter ersetzt werden
- file-basierte Shell-Steuerung als Integrationspfad fuer groesseres Multi-Modul-System
- lokale Session-Bridge als Endmodell fuer Host-/Orchestrator-Kommunikation
- app-zentrierte Reflection-Modelle als primaere Integrationssicht
- direkte `camera_app`-Abhaengigkeiten im `vision_platform`-Kern

### Kann wahrscheinlich bleiben
- `CameraSubsystem`-Bootstrap
- `CommandController` als Kernidee
- API-/Status-Payload-Mapping als Adapter-Schicht
- Capability-Service
- Traceability-/Artefaktlogik als subsystem-lokale Artefaktperspektive

## 9. Risiken

### Hoch
- kein first-class Runtime-Event-Modell
- kein explizites Lifecycle-/Orchestrator-Modell
- kein explizites Health-Modell
- Gefahr, dass die Shell-Bridge zur eigentlichen Integrationsoberflaeche einfriert

### Mittel
- Zeitmodell exportiert zu wenig Provenienz und Clock-Domain-Qualitaet
- `vision_platform` und `camera_app` sind noch nicht klar genug geschieden
- ROI/Focus/Preview-Zustaende sind nicht zentral genug ueber die kuenftige Integration Surface modelliert
- kameraeigene Artefaktlogs koennen mit systemischem Logging verwechselt werden

### Niedrig
- konkrete CLI-Envelope-Details
- konkrete `labview_mapping`-Zuschnitte
- UI-lokale Presenter- und Renderingplatzierung

## 10. Konkrete Empfehlungen

1. Fuehre eine explizite `CameraIntegrationSurface`-Fassade ueber Controller, Capability-Service, Status- und Health-Mapping ein.
2. Ergaenze ein kleines Lifecycle-Modell mit `prepare`, `arm`, `start`, `stop`, `abort`, `recover`.
3. Fuehre ein echtes `CameraHealth`-Modell ein.
4. Fuehre typed Runtime-Events ein, mindestens fuer Konfiguration, Snapshot, Recording, Fault und Health.
5. Erweitere `FrameMetadata` um strukturierten Zeitkontext mit `clock_domain`, `device_timestamp`, `host_utc`, `host_monotonic`, `timestamp_quality`.
6. Trenne Artefaktindex, Traceability und Systemlogging konzeptionell schaerfer.
7. Hebe `get_capabilities()` und `get_health()` zu stabilen Integrationscalls an.
8. Ziehe wiederverwendbare UI-agnostische Presenter-/Interaction-Teile aus `apps/local_shell` in eine allgemeinere Adapter-/Display-Schicht, falls sie wiederverwendet werden sollen.
9. Markiere `captures/wx_shell_sessions` und die JSONL-/JSON-Bridge explizit als Uebergangs-IPC.
10. Reduziere direkte `camera_app`-Imports aus dem `vision_platform`-Kern.

---

## 4. Priorisierte Liste der wichtigsten Luecken

### Hoch priorisiert
- fehlende Event-Oberflaeche
- fehlendes Lifecycle-/Orchestrator-Modell
- fehlendes explizites Health-Modell
- Uebergangs-IPC der Shell ist kein tragfaehiges Endmodell

### Mittel priorisiert
- Zeitmodell zu flach exportiert
- Artefaktlog vs. Systemlogging nicht sauber getrennt
- `vision_platform` vs. `camera_app` noch nicht klar genug
- ROI/Focus/Preview-State nicht zentral genug exportiert

### Niedrig priorisiert
- Envelope-Details der CLI
- spezifische Companion-/LabVIEW-Adapterformen
- Platzierung einzelner UI-agnostischer Presenter-Klassen

---

## 5. Konkrete Empfehlungen

1. Mache `vision_platform` zur echten primaeren Integrationsoberflaeche und baue die Kernimporte auf `camera_app` schrittweise ab.
2. Lege ein formales `CameraHealth`-Modell an und leite es aus `CameraStatus`, `SubsystemStatus` und Audit-Signalen ab.
3. Fuehre eine kleine Eventfamilie fuer Kamera-Runtime-Events ein.
4. Fuehre einen expliziten Lifecycle-Adapter fuer Orchestrator-nahe Nutzung ein.
5. Erweitere die Zeitmetadaten in `CapturedFrame` und `FrameMetadata`.
6. Definiere explizite `ArtifactReference`- und `ArtifactMetadata`-DTOs.
7. Trenne `recording_log.csv` als Artefaktindex klar vom spaeteren Systemloggingmodell.
8. Markiere und dokumentiere Shell-Live-Sync als Uebergangsmechanismus.
9. Ziehe wiederverwendbare Preview-/Interaction-Bausteine aus der App-Schicht heraus, wo sie wirklich subsystemisch sind.
10. Ergaenze `GetCapabilities` und `GetHealth` als stabile Surface-Calls.

---

## 6. Optional: Vorschlag fuer eine minimal tragfaehige `Camera Integration Surface v0.1`

### Commands
- `PrepareCamera`
- `ApplyConfiguration`
- `SetSaveDirectory`
- `SaveSnapshot`
- `StartRecording`
- `StopRecording`
- `GetStatus`
- `GetHealth`
- `GetCapabilities`

### State
- `camera_id`
- `source_kind`
- `availability`
- `readiness`
- `is_acquiring`
- `configuration`
- `save_directory`
- `recording_state`
- `active_run_id`
- `last_fault_kind`
- `last_fault_message`

### Events
- `CameraPrepared`
- `CameraConfigurationApplied`
- `CameraSnapshotSaved`
- `CameraRecordingStarted`
- `CameraRecordingStopped`
- `CameraFaulted`
- `CameraHealthChanged`

### Artifacts
- `artifact_path`
- `artifact_kind`
- `run_id`
- `frame_id`
- `camera_timestamp`
- `system_timestamp_utc`
- `camera_id`
- `configuration_profile_id`

### Health
- `availability`
- `readiness`
- `degraded`
- `faulted`
- `capabilities_available`
- `capability_probe_warning`
- `recording_failed`
- `last_error`

---

## Schluss

Die richtige Lesart des bestehenden Repositories ist nicht:
- `nur eine Kamera-App`

sondern:
- `ein bereits weit entwickeltes Kamera-Subsystem mit headless-nahem Kern, vorhandener Integrationsbasis und optionaler Companion-Schicht`.

Die naechste Entwicklungsstufe fuer die Einbettung in ein groesseres Multi-Modul-System liegt deshalb nicht primaer in neuen Aufnahmefunktionen, sondern in:
- Lifecycle-Sprache
- Event-Modell
- Health-Modell
- Zeit-Provenienz
- Integrationssurface-Klarheit
- und sauberer Trennung zwischen subsystem-lokalen Artefakten und systemischem Logging.
