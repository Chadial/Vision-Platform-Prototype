# camera_integration_surface_v0.1

## Zweck

Diese Note definiert die kleine, belastbare `Camera Integration Surface v0.1` fuer das bestehende Kamera-Repository.

Sie ist bewusst eine Vorstufe:
- klein genug, um die aktuelle `Hybrid Companion`-Phase nicht umzuschmeissen
- verbindlich genug, um spaetere Gesamtintegration nicht wieder offenlaufen zu lassen

Sie legt keine Endarchitektur fest fuer:
- Transport
- Event-Bus
- Gesamt-Orchestrator
- systemweites Logging

Sie legt nur die minimale Camera-Sicht fest, auf die sowohl die aktuelle Repo-Phase als auch spaetere Gesamtintegration sauber aufsetzen koennen.

---

## Repo-nahe Ausgangsbasis

Die Surface v0.1 setzt direkt auf vorhandenen Strukturen des Repos auf:
- `vision_platform.bootstrap`
- `vision_platform.control.command_controller.CommandController`
- `camera_app.services.camera_service.CameraService`
- `camera_app.services.snapshot_service.SnapshotService`
- `camera_app.services.recording_service.RecordingService`
- `vision_platform.services.api_service`
- bestehende Statusmodelle wie `SubsystemStatus`, `CameraStatus`, `RecordingStatus`, `IntervalCaptureStatus`

Diese Surface v0.1 ersetzt diese Bausteine nicht.
Sie rahmt sie als minimalen Integrationsvertrag.

---

## Repo-nahe Mapping-Sicht fuer WP93

Diese Tabelle macht die Surface v0.1 fuehrend statt nur beschreibend.

`category` bedeutet:
- `Surface`: gehoert zur minimalen Camera-Integrationsoberflaeche
- `Adapter`: transport-, CLI- oder API-nahe Form ueber der Surface
- `Companion-only`: legitime lokale Shell-/UI-/Reflection-Sicht
- `Transition-only`: pragmatischer Zwischenzustand, nicht Zielzustand

`action` bedeutet:
- `keep as-is`
- `rename in docs`
- `narrow`
- `defer`
- `promote to surface later`

| Repo-Element | Rolle in v0.1 | Category | Source of truth | Action |
| --- | --- | --- | --- | --- |
| `CommandController.apply_configuration()` | `ApplyConfiguration` command meaning | `Surface` | `vision_platform.control.command_controller.CommandController` | `keep as-is` |
| `CommandController.set_save_directory()` | `SetSaveDirectory` command meaning | `Surface` | `vision_platform.control.command_controller.CommandController` | `keep as-is` |
| `CommandController.save_snapshot()` | `SaveSnapshot` command meaning | `Surface` | `vision_platform.control.command_controller.CommandController` | `keep as-is` |
| `CommandController.start_recording()` | `StartRecording` command meaning | `Surface` | `vision_platform.control.command_controller.CommandController` | `keep as-is` |
| `CommandController.stop_recording()` | `StopRecording` command meaning | `Surface` | `vision_platform.control.command_controller.CommandController` | `keep as-is` |
| `CommandController.get_status()` | `GetStatus` command meaning | `Surface` | `vision_platform.control.command_controller.CommandController` plus `SubsystemStatus` | `keep as-is` |
| `SubsystemStatus` | pollbarer subsystemweiter Minimalzustand | `Surface` | `camera_app.models.subsystem_status` via `vision_platform.models` | `narrow` |
| `CameraStatus` | camera-nahe State-Basis | `Surface` | `camera_app.models.camera_status` via `vision_platform.models` | `narrow` |
| `RecordingStatus` | recording-nahe State-Basis | `Surface` | `camera_app.models.recording_status` via `vision_platform.models` | `narrow` |
| `IntervalCaptureStatus` | interval-capture-nahe State-Basis | `Surface` | `camera_app.models.interval_capture_status` via `vision_platform.models` | `defer` |
| `vision_platform.services.api_service.status_payloads` | API-/polling-nahe Statusform | `Adapter` | `vision_platform.services.api_service.status_payloads` | `rename in docs` |
| `vision_platform.services.api_service.command_payloads` | API-/CLI-nahe Envelope ueber Surface-Bedeutung | `Adapter` | `vision_platform.services.api_service.command_payloads` | `rename in docs` |
| `vision_platform.services.companion_contract_service` | shell-unabhaengige Companion-Envelope fuer den aktuellen Hybrid-Pfad | `Adapter` | `vision_platform.services.companion_contract_service` | `narrow` |
| `apps/camera_cli/camera_cli.py` success envelopes | CLI-nahe Ergebnisdarstellung | `Adapter` | `vision_platform.apps.camera_cli.camera_cli` | `rename in docs` |
| `apps/local_shell/live_command_sync.py` result files | file-basierte Shell-Bridge fuer offenen Session-Betrieb | `Transition-only` | `vision_platform.apps.local_shell.live_command_sync` | `defer` |
| `apps/local_shell/labview_mapping.py` | Stage-2-hostnahe Leseschicht fuer den aktuellen Companion-Pfad | `Companion-only` | `vision_platform.apps.local_shell.labview_mapping` | `keep as-is` |
| `apps/local_shell` published status / reflection blocks | legitime lokale Companion-Sicht | `Companion-only` | `vision_platform.apps.local_shell.wx_preview_shell` | `keep as-is` |
| `saved_artifact_traceability.csv` | lokale Artefakt-Traceability | `Adapter` | storage-/traceability path im bestehenden Repo | `rename in docs` |
| `recording_log.csv` | recording-nahe Artefakt-/Ablaufspur | `Adapter` | recording/logging path im bestehenden Repo | `rename in docs` |
| `hardware_audit.jsonl` | hardware- und incident-nahe Auditspur | `Adapter` | `vision_platform.services.hardware_audit_service` | `defer` |
| `GetHealth` | expliziter Surface-Call noch nicht ausgearbeitet | `Surface` | noch kein einzelner produktiver Vertrag | `promote to surface later` |
| `GetCapabilities` | expliziter Surface-Call noch nicht ausgearbeitet | `Surface` | capability-nahe Logik im bestehenden Repo, noch kein enger Vertrag | `promote to surface later` |

Wichtige Lesart:
- Die Tabelle beschreibt nicht nur, was es heute gibt.
- Sie fuehrt auch, was in v0.1 bewusst direkt Surface ist, was nur Adapterform ist und was nicht zur primaeren Surface erhoben werden soll.

Spezifische Klarstellung zu `IntervalCaptureStatus`:
- Das Modell ist heute vorhandenes, valides Rohmaterial im bestehenden Statusbestand.
- Es gehoert aber noch nicht verbindlich zum pollbaren Minimalzustand der `Camera Integration Surface v0.1`.
- Fuer v0.1 bleibt es deshalb bewusst als vorhandene Surface-nahe Struktur sichtbar, aber noch nicht als Pflichtbestandteil der engeren Minimalsurface festgezogen.

---

## Surface-Bedeutung vs. Payload- oder Result-Form

Im bestehenden Repo liegen fachliche Surface-Bedeutung und konkrete Payload- oder Result-Form noch teilweise uebereinander.

Fuer v0.1 gilt deshalb:

- `surface-facing result meaning` ist das fachliche Ergebnis, das die Camera Surface nach aussen traegt
- eine Payload-, Envelope- oder JSON-Form ist nur eine konkrete Adapter- oder Transportform dieses Ergebnisses

Beispiele:
- `SaveSnapshot` als Surface-Bedeutung meint: Snapshot wurde angefordert, gespeichert oder ist fehlgeschlagen, mit artefaktnahem Rueckgabekontext
- das aktuelle CLI-Envelope, API-Payload oder Companion-Resultfile ist nicht selbst die Surface, sondern nur ihre momentane Form
- `GetStatus` als Surface-Bedeutung meint: pollbarer Minimalzustand des Kamera-Subsystems
- `ApiSubsystemStatusPayload` ist dafuer eine API-nahe Adapterform, nicht die eigentliche Surface-Definition

Wichtige Regel:

Die Surface v0.1 wird nicht ueber aktuelle Envelope-Formen definiert, sondern ueber die fachliche Bedeutung der Commands, des States, der Artifacts und spaeter von Health/Events.

---

## Boundary-Block fuer WP93

### Surface

`Surface` bezeichnet die kleine, stabile Integrationsoberflaeche des Camera-Subsystems:
- Commands mit host-neutraler fachlicher Bedeutung
- pollbarer Minimal-State
- artefaktnahe Rueckgabebedeutung
- spaeter explizit: `GetHealth`, `GetCapabilities`

### Adapter

`Adapter` bezeichnet Formen, die ueber der Surface liegen:
- API-Payloads
- CLI-Envelopes
- shell-unabhaengige Companion-Resultbuilder
- traceability- oder auditnahe Ausgabespuren

Sie koennen stabil und wertvoll sein, sind aber nicht automatisch selbst die primaere Surface.

Wichtige Klarstellung:

`vision_platform.services.companion_contract_service` ist nicht die primaere `Camera Integration Surface`.
Er bleibt aber ein wichtiger shell-unabhaengiger Vertragsbaustein fuer den aktuellen `Hybrid Companion`-Pfad.

### Companion-only

`Companion-only` bezeichnet legitime lokale Consumer-, UI- oder Reflection-Sichten:
- shell-published status subsets
- shell-facing reflection blocks
- Stage-2-LabVIEW-nahe Leseschichten ueber dem aktuellen Companion-Pfad

Diese Dinge sind nicht "falsch" oder bloss Altlast.
Sie sind gueltige lokale Consumersichten fuer die aktuelle Hybrid-Companion-Phase.

### Transition-only

`Transition-only` bezeichnet pragmatische Zwischenformen, die heute nuetzlich sind, aber nicht stillschweigend zum Zielzustand werden sollen:
- file-basierte Live-Sync-Resultpfade
- shell-session-spezifische Resultablagen als technische Bruecke

Wichtige Regel:

Nicht alles Shellnahe ist `Transition-only`.
`Companion-only` und `Transition-only` muessen bewusst getrennt gelesen werden.

## Commands

### Heute vorhanden und direkt surface-faehig

- `ApplyConfiguration`
  Repo-Bezug:
  `CommandController.apply_configuration()`
- `SetSaveDirectory`
  Repo-Bezug:
  `CommandController.set_save_directory()`
- `SaveSnapshot`
  Repo-Bezug:
  `CommandController.save_snapshot()`
- `StartRecording`
  Repo-Bezug:
  `CommandController.start_recording()`
- `StopRecording`
  Repo-Bezug:
  `CommandController.stop_recording()`
- `GetStatus`
  Repo-Bezug:
  `CommandController.get_status()`

### Kurzfristig in v0.1 explizit zu praezisieren

- `GetHealth`
- `GetCapabilities`

### Spaeter ausbaubar

- `Prepare`
- `Arm`
- `Abort`
- `Recover`

Wichtige Regel:

V0.1 trennt bereits zwischen:
- kamera-lokalen Capture-Commands
- spaeterer Modul-Lifecycle-Sprache

ohne die spaetere Endform schon festzuschreiben.

---

## State

Die Surface v0.1 braucht einen pollbaren, host-lesbaren Minimalzustand.

### Heute vorhanden

- Kameraidentitaet und Quellart
- Initialisierung und Verfuegbarkeit
- aktuelle Konfigurationssicht
- Recording-Zustand
- Interval-Capture-Zustand
- Save-Basis

Repo-Bezug:
- `CameraStatus`
- `SubsystemStatus`
- `RecordingStatus`
- `IntervalCaptureStatus`
- statusnahe Payload-Mappings

### Kurzfristig zu praezisieren

- `availability`
- `readiness`
- `is_initialized`
- `is_acquiring`
- `configuration`
- `save_directory`
- `recording_state`
- `active_run_id`, falls vorhanden
- `last_fault_summary`, falls vorhanden

### Bewusst noch offen

- vollstaendiger Lifecycle-State
- vollstaendiger Session-/Run-State
- Restriction-/Lock-State
- shellspezifische Reflection-States als primaere State-Lesart

Wichtige Regel:

State v0.1 ist nicht:
- Shell-Reflection
- Event-Historie
- Artefaktindex

---

## Events

Runtime-Events sind in v0.1 noch nicht voll ausgebaut, muessen aber als eigene Integrationskategorie festgehalten werden.

### Heute vorhanden

Es gibt bereits eventartigen Charakter in:
- `saved_artifact_traceability.csv`
- `recording_log.csv`
- `hardware_audit.jsonl`
- Shell-Result-Dateien und Status-Snapshots

### Kurzfristig zu praezisieren

Diese Dinge sind kein Runtime-Event-Modell.
V0.1 benennt deshalb nur die minimale Eventfamilie.

### Minimale Eventfamilie

- `CameraConfigurationApplied`
- `CameraSnapshotSaved`
- `CameraRecordingStarted`
- `CameraRecordingStopped`
- `CameraFaulted`
- `CameraHealthChanged`

### Bewusst noch offen

- Event-Transport
- Event-Bus
- Delivery-Garantien
- Subscription-Modell

---

## Artifacts

Artifacts sind in v0.1 eine eigene Integrationssicht.

### Heute vorhanden

- Snapshot-Dateien
- Recording-Frames oder Serienartefakte
- `recording_log.csv`
- `saved_artifact_traceability.csv`
- artefaktnahe Metadaten in Command-Resulten und Traceability-Zeilen

### Kurzfristig zu praezisieren

Jede relevante Artefaktausgabe sollte mindestens lesbar machen:
- `artifact_path`
- `artifact_kind`
- `save_directory`
- `file_name` oder aequivalenter Dateibezeichner
- `run_id`, falls vorhanden
- `frame_id`, falls vorhanden
- `camera_id`, falls vorhanden
- Zeitkontext

### Harte Grenze

Artefakte und Artefaktmetadaten sind nicht dasselbe wie systemweites Logging.

Die Camera Surface v0.1 liefert:
- Artefaktreferenzen
- lokale Traceability
- artefaktnahe Metadaten

Sie uebernimmt nicht:
- moduluebergreifende Korrelation
- zentrale Audit-Chronik
- Gesamtlogging-Hoheit

Explizite Klarstellung:

`saved_artifact_traceability.csv` und `recording_log.csv` sind surface-relevante Hilfs- oder Adapterformen fuer Artefaktbezug und lokale Traceability.
Sie sind nicht die zentrale Logging-Wahrheit des Gesamtsystems.

---

## Health

Health ist in v0.1 explizit eigene Integrationskategorie.

### Heute vorhanden

- `last_error`
- capability-bezogene Warnungen
- `can_*`-Faehigkeiten
- auditnahe Warn- und Incident-Signale

### Minimales Health-Bild fuer v0.1

- `availability`
- `readiness`
- `degraded`
- `faulted`
- `last_error`
- `capabilities_available`
- `capability_probe_warning`
- `recording_failed`, falls ableitbar

### Bewusst noch offen

- globale Safety-Bewertung
- komplexe Fault-Taxonomie
- komplette Supervisor-Logik

Health v0.1 soll nur sicherstellen, dass spaetere Gesamtintegration nicht wieder auf rohe Fehlertexte zurueckfaellt.

---

## WP94 Surface-Vertrag: GetHealth

`GetHealth` ist in `WP94` ein expliziter Surface-Call.

Seine Aufgabe ist:
- einen kompakten, aktuellen, lesbaren Gesundheitszustand des Camera-Subsystems zu liefern
- nicht nur rohe Statusfragmente oder Fehlertexte weiterzureichen
- nicht spaetere Supervisor- oder Logging-Hoheit vorwegzunehmen

Minimale Regel:

`GetHealth` liefert keinen Incident-Feed.
Es liefert keinen Audit-Stream.
Es liefert keine Failure-Reflection-Historie.
Es liefert einen kompakten aktuellen lesbaren Gesundheitszustand.

### Stable-now Bedeutung

`GetHealth` soll v0.1-seitig mindestens folgende Surface-Bedeutung tragen:
- `availability`
- `readiness`
- `degraded`
- `faulted`
- `last_error`
- `capabilities_available`
- `capability_probe_warning`, falls vorhanden
- `recording_failed`, falls aus dem aktuellen Zustand ableitbar

### Repo-nahe Ableitungsbasis

Diese Surface-Bedeutung darf sich auf vorhandene Signale stuetzen aus:
- `CameraStatus`
- `SubsystemStatus`
- `RecordingStatus`
- capability-bezogenen Warnungen
- `vision_platform.services.hardware_audit_service` nur als moegliche Rohsignalquelle

Wichtige Regel:

Audit-, Warning- und Failure-Reflection-Quellen koennen Rohmaterial fuer `GetHealth` sein.
Sie sind nicht selbst die Rueckgabeform von `GetHealth`.

### Bewusst noch nicht Teil von WP94

- internes `CameraHealth`-Ableitungsmodell
- feinere Fault-Taxonomie
- Incident-/Warning-Historie
- supervisor-nahe Bewertung

`WP94` ist der Surface-Vertrag.
`WP95` bleibt das interne Ableitungsmodell.

---

## WP95 Internes Modell: CameraHealth

`WP95` ist bewusst nicht noch einmal ein Surface-Vertrag.
`WP95` ist das kleine interne Ableitungsmodell unterhalb von `GetHealth`.

### Stable-now Feldmenge

Die erste Baseline soll bewusst klein bleiben:
- `availability`
- `readiness`
- `degraded`
- `faulted`
- `last_error`
- `capabilities_available`
- optional nur wenn sauber ableitbar: `recording_impaired`

Diese Baseline soll bewusst noch nicht enthalten:
- viele Fault-Unterarten
- mehrere Warning-Kanaele
- historische Incidentlisten
- breite Supervisor- oder Safety-Klassifikation

### Harte Trennung: degraded vs faulted

Diese Trennung ist im internen Modell frueh explizit zu halten:

- `faulted`:
  der aktuelle Zustand verhindert oder bricht eine wesentliche Funktion
- `degraded`:
  die Funktion ist aktuell grundsaetzlich noch da, aber eingeschraenkt, risikobehaftet oder nicht voll vertrauenswuerdig

Die beiden Felder duerfen nicht stillschweigend ineinanderlaufen.

### last_error als Kontextfeld

`last_error` ist Teil des Modells, aber nicht dessen Wahrheitsanker.

Wichtige Regel:

`CameraHealth` ist ein abgeleiteter aktueller Zustand.
`last_error` ist nur ein Kontextfeld dazu.

### Audit nur als Input

Audit- oder incident-nahe Signale duerfen die Health-Ableitung beeinflussen.
Aber:

- `CameraHealth` ist kein Audit-Feed
- `CameraHealth` ist keine Incident-Historie
- `CameraHealth` spiegelt nicht einfach `hardware_audit.jsonl`

Damit bleibt die Grenze sauber zwischen:
- internem aktuellem Health-Modell
- Audit-/Incident-Spuren
- spaeterer Logging- oder Safety-Hoheit

---

## WP94 Surface-Vertrag: GetCapabilities

`GetCapabilities` ist in `WP94` ein expliziter Surface-Call.

Seine Aufgabe ist:
- die fuer Integration relevante Faehigkeitssicht des Camera-Subsystems lesbar zu machen
- ohne Rohdetails interner Probe- oder Profilpfade direkt zur Surface zu erklaeren

### Minimale Lesart in WP94

Bereits in `WP94` muss sprachlich getrennt werden zwischen:
- `supported`
- `currently available`
- `currently enabled`

Diese Begriffe sind nicht dasselbe:

- `supported`:
  was das System oder die Kameralinie grundsaetzlich unterstuetzen kann
- `currently available`:
  was unter aktueller Hardware-, Probe- oder Konfigurationslage derzeit verfuegbar ist
- `currently enabled`:
  was im aktuellen Modus oder in der aktuellen aktiven Konfiguration tatsaechlich eingeschaltet oder nutzbar gemacht ist

### Stable-now Bedeutung

`GetCapabilities` soll v0.1-seitig mindestens eine kleine, lesbare Capabilities-Sicht liefern fuer:
- Konfigurationsfaehigkeiten, soweit heute belastbar lesbar
- Recording-/Capture-nahe Faehigkeiten, soweit heute belastbar lesbar
- capability-bezogene Warnhinweise, falls die Probe nur eingeschraenkt moeglich war

Es soll dabei nicht:
- rohe Probeergebnisse dumpen
- Profil- oder Driver-Interna direkt exportieren
- schon die spaetere Endform eines umfassenden Capability-Modells erzwingen

### Repo-nahe Ableitungsbasis

Diese Surface-Bedeutung darf sich auf vorhandene capability-nahe Logik stuetzen aus:
- aktuelle Status- und Konfigurationspfade
- capability-aware Validierungs- und Prueflogik im bestehenden Repo
- probe- oder auditnahe Warnsignale, wenn sie fuer `currently available` relevant sind

### Bewusst noch nicht Teil von WP94

- umfassende Capability-Profil-Taxonomie
- komplette Unterscheidung aller spaeteren Laufzeitmodi
- finaler API-/Transportvertrag fuer jede Capability-Unterfamilie

Auch hier gilt:

`WP94` ist der Surface-Vertrag.
`WP95` ist nicht Capabilities-Ausbau, sondern das interne Health-Ableitungsmodell.

---

## Explizit noch offen nach WP93

Diese Punkte werden durch `WP93` bewusst noch nicht geschlossen:

- enger Surface-Vertrag fuer `GetHealth`
- enger Surface-Vertrag fuer `GetCapabilities`
- internes `CameraHealth`-Minimalmodell
- minimale Runtime-Eventfamilie mit Producer-Orten und Eventschema

`WP93` macht diese Luecken sichtbar und klein.
Es schliesst sie noch nicht.

---

## Minimales Zeitmodell fuer v0.1

Die Integration Surface v0.1 braucht einen kleinen, aber verbindlichen Zeitkontext.

### Heute vorhanden

- `camera_timestamp`
- `system_timestamp_utc`
- `frame_id`
- interne monotone Zeiten in Recording-/Interval-Logik

### Kurzfristig verbindlich zu praezisieren

Wichtige Kameraereignisse und Artefakte sollen mehr als einen simplen Timestamp tragen koennen, mindestens:
- `device_timestamp`, falls vorhanden
- `host_utc`
- `host_monotonic`, falls verfuegbar oder spaeter nachziehbar
- `frame_id`, falls relevant
- `time_source` oder `time_quality`

### Bewusst noch offen

- grosse Zeitarchitektur
- systemweite Clock-Korrelation als Endmodell

V0.1 verhindert nur, dass `camera_timestamp + utc` stillschweigend zur Endform wird.

---

## WP97 Artefaktreferenz und minimaler Zeitkontext

`WP97` ist bewusst ein schmaler Folge-Slice.
Er soll keine grosse Artefakt- oder Zeitarchitektur bauen, sondern nur die kleinste belastbare Baseline festziehen.

### ArtifactReference bewusst klein halten

Die erste `ArtifactReference`-Baseline soll bewusst klein bleiben:
- `artifact_path`
- `artifact_kind`
- `file_name`
- optional `run_id`
- optional `frame_id`
- optional `camera_id`
- minimaler Zeitkontext

Diese Baseline soll bewusst noch nicht enthalten:
- tiefe Vollstaendigkeitsmodelle
- grosse `Artifact`-DTO-Familien
- Index- oder Storage-Design
- breitere Session- oder Logging-Semantik

### run_id und frame_id nur when present

`run_id` und `frame_id` sind wertvolle Referenzfelder.
Aber:

- sie sind nicht Voraussetzung fuer jede `ArtifactReference`
- ihre Abwesenheit macht eine Referenz nicht automatisch ungueltig
- sie bleiben in `WP97` bewusst `when present`-Felder

### Zeitkontext nur als Minimalbaseline

Der Zeitkontext soll in `WP97` klein bleiben, zum Beispiel:
- `device_timestamp` oder vorhandenes kameraseitiges Zeitfeld
- `host_utc`
- `host_monotonic`, falls im Repo heute sinnvoll ableitbar
- `frame_id`, wenn vorhanden
- `time_source` oder `time_quality` nur, wenn heute schon sauber dokumentierbar

Nicht mehr.
Sonst kippt `WP97` in eine halbe Zeitarchitektur.

### Traceability nicht zur ArtifactReference machen

Traceability-Dateien koennen:
- Quelle sein
- Evidenz sein
- hilfreiche Kontextspur sein

Aber:

- sie sind nicht selbst die Definition der `ArtifactReference`
- `saved_artifact_traceability.csv` ist nicht die Artefaktreferenz selbst
- `recording_log.csv` ist nicht die Artefaktreferenz selbst

Damit bleibt die Grenze sauber zwischen:
- Artefaktreferenz
- lokaler Traceability
- Logging
- spaeterer Storage- oder Indexlogik

---

## Was v0.1 bewusst nicht festlegt

Diese Vorstufe legt bewusst nicht fest:
- finalen Transport
- finalen Event-Bus
- finale Orchestrator-Sprache
- finale Safety-Politik
- komplette historische Entkopplung aller `camera_app`-Reste
- Ersetzung der Shell-Bridge

Sie definiert nur die minimale, belastbare Integrationsoberflaeche, auf die spaetere Ausbaustufen aufsetzen sollen.

---

## Ergebnis

Die `Camera Integration Surface v0.1` ist die kleinste verbindliche Vorstufe, die das bestehende Repo jetzt explizit machen sollte:
- vorhandene Commands sauber rahmen
- pollbaren Minimal-State stabil lesen
- minimale Eventfamilie benennen
- Artefaktreferenzen als eigene Surface behandeln
- Health und Zeitkontext als explizite Integrationskategorien festziehen

Das ist klein genug fuer die aktuelle Phase und stark genug fuer spaetere Gesamtintegration.

---

## Kompakte Normliste fuer v0.1

Diese Liste ist die verdichtete Referenz fuer die minimale `Camera Integration Surface v0.1`.

### Pflicht-Commands

- `ApplyConfiguration`
- `SetSaveDirectory`
- `SaveSnapshot`
- `StartRecording`
- `StopRecording`
- `GetStatus`
- `GetHealth`
- `GetCapabilities`

### Pflicht-State-Felder

- `camera_id`, falls vorhanden
- `source_kind`
- `availability`
- `readiness`
- `is_initialized`
- `is_acquiring`
- `configuration`
- `save_directory`
- `recording_state`
- `active_run_id`, falls vorhanden
- `last_fault_summary`, falls vorhanden

### Minimale Eventfamilie

- `CameraConfigurationApplied`
- `CameraSnapshotSaved`
- `CameraRecordingStarted`
- `CameraRecordingStopped`
- `CameraFaulted`
- `CameraHealthChanged`

### Pflicht-Artefaktfelder

- `artifact_path`
- `artifact_kind`
- `save_directory`
- `file_name` oder aequivalenter Dateibezeichner
- `run_id`, falls vorhanden
- `frame_id`, falls vorhanden
- `camera_id`, falls vorhanden
- Zeitkontext

### Pflicht-Health-Felder

- `availability`
- `readiness`
- `degraded`
- `faulted`
- `last_error`
- `capabilities_available`
- `capability_probe_warning`, falls vorhanden
- `recording_failed`, falls ableitbar
