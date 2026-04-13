# Camera Repo Strategieplanung fuer Gesamtprojekt

## 1. Zweck der Note

Diese Note beschreibt den strategischen Transformationspfad vom heutigen Kamera-Repository zu einem belastbaren `Camera Subsystem` fuer ein groesseres Multi-Modul-System.

Sie beschreibt damit nicht primaer das theoretische Soll-Modul, sondern den **Weg**:
- von der aktuellen repo-nahen Realitaet
- ueber gezielte Architektur- und Integrationsschaerfung
- hin zu einer tragfaehigen Zielrolle im Gesamtprojekt

Die Note ist bewusst eine Planungsnote:
- repo-nah statt abstrakt
- schrittweise statt revolutionaer
- mit Trennung zwischen `heute vorhanden`, `spaeter anzupassen` und `noch fehlend`

---

## 2. Ausgangslage des bestehenden Repos

Das bestehende Repository ist bereits deutlich naeher an einem einbettbaren `Camera Subsystem` als an einer klassischen Kamera-App.

Die aktuelle Realitaet ist:
- ein headless-naher Kamera-Kern ist vorhanden
- host-neutrale Command-Steuerung ist vorhanden
- Snapshot, Recording, Preview und Konfigurationsanwendung sind real implementiert
- die lokale VisionApp / wxShell ist eine Companion-Betriebsform ueber dem Kern
- das Repo ist noch nicht die fertige Integrationsform eines groesseren Orchestrator-/Logging-/Safety-Systems

Heute vorhanden:
- `vision_platform.bootstrap` als Start- und Verdrahtungspunkt
- `CommandController` als host-neutrale Steueroberflaeche
- `CameraService`, `SnapshotService`, `RecordingService` als zentrale fachliche Laufzeitbausteine
- Stream-, CLI-, Status- und Payload-Schichten
- `vision_platform.services.api_service` als transportnahe Status- und Command-Payload-Schicht
- Capability-nahe Services als Vorstufe spaeterer Integrationscalls
- artefaktnahe Traceability, Recording-Logs und Audit-Pfade
- optionale lokale Shell mit Live-Bridge fuer den aktuellen `Hybrid Companion`-Betrieb

Spaeter anzupassen:
- die Lesart `laufende App mit Host-Steuerung`
- die Rolle der Shell als sichtbare, aber nachgeordnete Companion-Schicht
- die heute noch implizite Vermischung von Status, Reflection, IPC und Eventcharakter

Noch fehlend:
- explizite Lifecycle-Sprache fuer Orchestrator-nahe Nutzung
- first-class Runtime-Events
- explizites Health-Modell
- strukturiertes Zeitmodell mit Provenienz
- saubere Trennung von subsystemlokaler Artefaktpersistenz und systemischem Logging
- klar benannte Endarchitektur jenseits der file-basierten Shell-Bridge

---

## 3. Zielrolle des Repos im Gesamtprojekt

Die Zielrolle des Repositories ist nicht `Kamera-App`, sondern:

**reale Ausgangsbasis und schrittweise Haupttraeger eines einbettbaren Camera Subsystems**

Im Gesamtprojekt soll daraus hervorgehen:
- ein wiederverwendbarer Camera Core
- eine stabile Camera Integration Surface
- optionale Zugriffsschichten wie CLI, API, lokale Shell oder spaetere MCP-nahe Adapter

Das Ziel ist nicht:
- die heutige wxShell zur Endarchitektur zu erklaeren
- das bestehende Repo vollstaendig neu zu erfinden
- Logging, Orchestrator und Safety in das Camera-Modul hineinzuziehen

Das Ziel ist:
- das vorhandene starke Kamera-Repo kontrolliert in die Sprache und Integrationslogik des Gesamtprojekts zu ueberfuehren

Die strategische Leitfrage ist daher nicht, ob das Repo verwertbar ist.
Die Leitfrage ist, wie lange die heutige Form noch ausreicht, bevor fehlende Lifecycle-, Event-, Health- und Zeitmodelle zum Integrationshemmnis werden.

---

## 4. Was bereits stark und wiederverwendbar ist

Das Repository bringt bereits mehrere starke Bausteine mit, die nicht ersetzt, sondern gezielt weiterentwickelt werden sollten.

### Kern und Verdrahtung

Heute vorhanden:
- `vision_platform.bootstrap` als wiederverwendbarer Startpunkt
- `CommandController` als host-neutrale Application Surface
- `CameraService` fuer kameraorientierte Laufzeitsteuerung
- `SnapshotService` fuer Snapshot-Flows
- `RecordingService` fuer bounded Recording-Flows
- Stream-Services fuer laufende Akquisition und Preview-nahe Nutzung
- Capability-nahe Services fuer live oder profilbezogene Kameragrenzen

Strategischer Wert:
- diese Bausteine sind bereits naeher an einem Camera Subsystem als an App-spezifischer Logik
- sie bilden den realen Kern fuer die spaetere Integration Surface

### Adapter und konsumierbare Oberflaechen

Heute vorhanden:
- CLI ueber `vision_platform.apps.camera_cli`
- status- und payloadnahe Schichten ueber `vision_platform.services.api_service`
- shellseitige Control- und Reflection-Pfade

Strategischer Wert:
- hier existiert bereits eine erste Adapterfamilie
- das Repo hat also nicht nur Kernlogik, sondern auch erste konsumierbare Integrationsformen

### Persistenz, Traceability und Audit

Heute vorhanden:
- Snapshot- und Recording-Artefakte
- `recording_log.csv`
- `saved_artifact_traceability.csv`
- `hardware_audit.jsonl`

Strategischer Wert:
- subsystemlokale Nachvollziehbarkeit ist bereits deutlich ausgebildet
- diese Pfade sind gute Ausgangsbasis fuer spaetere explizite Artefakt- und Logging-Grenzen

### Frontend-Abgrenzung

Heute vorhanden:
- lokale wxShell als Companion-Schicht
- OpenCV-/Frontend-Vorarbeit getrennt vom Kern

Spaeter anzupassen:
- app-lokale UI-agnostische Hilfsschichten, sofern sie subsystemisch wiederverwendbar werden sollen
- verbleibende Direktkopplungen von `vision_platform` auf `camera_app`

Strategischer Wert:
- die eigentliche Kamera-Fachlogik liegt bereits nicht in der Shell
- das erleichtert die schrittweise Herausarbeitung eines echten Camera Subsystems

---

## 5. Wichtigste Luecken / Gaps

Die groessten Luecken liegen heute nicht primaer in den Aufnahmefunktionen, sondern an den Systemgrenzen.

### 1. Lifecycle-Sprache

Heute vorhanden:
- `apply_configuration`
- `set_save_directory`
- `save_snapshot`
- `start_recording`
- `stop_recording`
- `get_status`

Spaeter anzupassen:
- die heutige hostnahe Command-Sprache muss sauber gegen orchestratornahe Lifecycle-Semantik abgegrenzt werden

Noch fehlend:
- explizites Modell fuer `Prepare`, `Arm`, `Abort`, `Recover`
- explizite Trennung zwischen kamera-lokalen Capture-Commands und Modul-Lifecycle-Commands

### 2. Runtime-Events

Heute vorhanden:
- eventartige Artefakte in Traceability, Audit und Shell-Ergebnissen

Spaeter anzupassen:
- diese Spuren duerfen nicht mit einem echten Runtime-Event-Modell verwechselt werden

Noch fehlend:
- first-class Events fuer Snapshot, Recording, Fault, Health, Konfiguration und relevante Zustandsaenderungen

### 3. Health-Modell

Heute vorhanden:
- `last_error`
- Capability-Warnungen
- `can_*`-Flags
- Audit-Klassifikation

Spaeter anzupassen:
- die heutige Fehlertext- und Statusflag-Sprache muss in ein explizites Health-Bild ueberfuehrt werden

Noch fehlend:
- `CameraHealth` mit `availability`, `readiness`, `degraded`, `faulted` und sauberer Ursachenlage
- klare kameraseitige Exportsignale wie `heartbeat_missing`, `trigger_unavailable`, `recording_failed`, falls fachlich benoetigt

### 4. Zeit-Provenienz

Heute vorhanden:
- `camera_timestamp`
- `system_timestamp_utc`
- interne monotone Schedulingzeiten
- `frame_id`

Spaeter anzupassen:
- exportierte Zeitdaten muessen als strukturierter Zeitkontext lesbar werden

Noch fehlend:
- explizite Clock-Domain-Sicht
- Zeitqualitaet
- host-monotone Sicht in der exportierten Integrationsoberflaeche

### 5. Persistenz vs. Logging

Heute vorhanden:
- subsystemlokale Artefaktpersistenz
- Traceability und Audit

Spaeter anzupassen:
- `recording_log` und `traceability` muessen klar als subsystemlokale Artefaktperspektive beschrieben werden

Noch fehlend:
- harte konzeptionelle Trennung zwischen Camera-Artefaktlogik und systemweitem Logging
- explizite Artefaktreferenzen als konsumierbare Integrationsobjekte

### 6. Shell-Bridge

Heute vorhanden:
- file-basierte Live-Sync-Bridge fuer die laufende wxShell

Spaeter anzupassen:
- diese Bridge darf nicht zur Endarchitektur einfrieren

Noch fehlend:
- eine klar benannte dauerhafte Integrationslogik jenseits der aktuellen Shell-IPC
- eine Lesart, in der shellnahe Reflection-Pfade nicht mehr stillschweigend den Modulzustand definieren

---

## 6. Transformationsprinzipien

Die Weiterentwicklung des Repositories sollte folgenden Prinzipien folgen.

### 1. Nicht neu erfinden, sondern freilegen

Das Repo hat bereits einen starken Kern.
Die Strategie ist daher nicht `Neustart`, sondern `Herausarbeiten und Schaerfen`.

### 2. Vom App-Bild zum Subsystem-Bild umdeuten

Die dominante Lesart muss sich verschieben:
- weg von `Kamera-App mit Host-Steuerung`
- hin zu `Camera Core plus Integration Surface plus optionale Companion-Schicht`

### 3. Endarchitektur nicht vorschnell simulieren

Nicht alles, was spaeter gebraucht wird, muss sofort technisch final gebaut werden.
Wichtig ist zuerst die saubere begriffliche und architektonische Trennung.

Gleichzeitig darf die Transformation nicht zu lange aufgeschoben werden:
Sobald das Gesamtprojekt verbindlich explizite Lifecycle-Sprache, Runtime-Events, systemweites Logging oder mehrschichtige Zeitkorrelation braucht, wird aus einer sauberen Nachschaerfung eine akute Integrationsnotwendigkeit.

### 4. Integration Surface explizit machen

Die eigentliche Transformationsarbeit liegt in der expliziten Beschreibung und schrittweisen Ausformung von:
- `Commands`
- `State`
- `Events`
- `Artifacts`
- `Health`

### 5. Uebergangsmechanismen bewusst als Uebergang markieren

Alles, was heute fuer den `Hybrid Companion`-Betrieb sinnvoll ist, darf bleiben, muss aber als Zwischenzustand lesbar sein.

### 6. Vorhandene Services als Primaertraeger nutzen

Die Transformation soll sich auf reale vorhandene Strukturen abstuetzen:
- `bootstrap`
- `CommandController`
- `CameraService`
- `SnapshotService`
- `RecordingService`
- CLI-/Status-/Payload-Schichten

### 7. Querschnittsmodule nicht in Camera hineinziehen

Logging, Orchestrator und Safety muessen anschlussfaehig werden, aber nicht in Camera aufgehen.

---

## 7. Phasenplan / Roadmap

Die Transformation sollte in klaren, kleinen Phasen erfolgen.

### Phase 1: Begriffs- und Architekturklarheit

Ziel:
- das Repo explizit als `Camera Subsystem` statt als App-zentrierte Einheit beschreiben

Heute vorhanden:
- realer Kern
- vorhandene Analysen
- beginnende Trennung von Shell und Kern

Arbeit:
- Architektur- und Strategienoten schaerfen
- Kern, Integration Surface und Companion-Schicht sauber benennen
- Shell-Bridge explizit als Uebergang markieren

Ergebnis:
- gemeinsame Lesart fuer weitere Refactorings

### Phase 2: Integration Surface v0.1 explizit machen

Ziel:
- aus dem bestehenden Command- und Statusbestand eine erste explizite `Camera Integration Surface` ableiten

Heute vorhanden:
- `CommandController`
- Status- und Payload-Mapping
- CLI-Adapter

Spaeter anzupassen:
- Shell-spezifische Reflections und hostnahe Ergebnisformen

Noch fehlend:
- explizite Surface-Dokumentation und fachlich stabile DTO-Lesart

Ergebnis:
- erster sauber lesbarer Vertragskern fuer Camera im Gesamtprojekt
- kurzfristig gute gemeinsame Tragfaehigkeit bleibt erhalten, ohne die heutige Form schon zur Endarchitektur zu erklaeren

### Phase 3: Lifecycle und Health nachziehen

Ziel:
- die hostnahe Command-Sprache um eine orchestratorfaehige Lifecycle- und Health-Sicht ergaenzen

Heute vorhanden:
- implizite Initialisierung
- Statusflags und Fehlertexte

Noch fehlend:
- `Prepare`, `Arm`, `Abort`, `Recover`
- `GetHealth`
- `CameraHealth`

Ergebnis:
- Camera wird fuer Orchestrator und Safety-Konsumenten deutlich anschlussfaehiger
- die mittelfristige Kompatibilitaet zwischen Kamera-Repo und Gesamtprojekt wird belastbarer

### Phase 4: Runtime-Events und Zeit-Provenienz

Ziel:
- Runtime-Ereignisse und strukturierte Zeitkontexte als first-class Integrationsbestandteile einfuehren

Heute vorhanden:
- Traceability
- Audit
- Artefaktmetadaten
- vorhandene Zeitfelder

Noch fehlend:
- echte Runtime-Eventfamilien
- strukturierter Zeitkontext in Event-, State- und Artifact-Sicht

Ergebnis:
- bessere Korrelation mit Orchestrator, Logging und spaeteren Systemmodulen
- geringeres Risiko, dass `camera_timestamp + utc` als zu flache Endform stehenbleibt

### Phase 5: Persistenzgrenzen und Logging-Grenzen schaerfen

Ziel:
- subsystemlokale Artefaktlogik klar gegen systemweites Logging abgrenzen

Heute vorhanden:
- starke lokale Persistenzpfade

Spaeter anzupassen:
- Benennung und Lesart von `recording_log`, `traceability`, Shell-Ergebnisdateien

Noch fehlend:
- explizite Artefaktreferenzen
- klare Trennung von Artefaktindex, Artefaktmetadaten und Gesamtlogging

Ergebnis:
- Camera bleibt zustaendig fuer Artefakte, ohne stillschweigend das zentrale Logging zu werden

### Phase 6: Companion-Bridge entkoppeln und Restkopplungen abbauen

Ziel:
- die aktuelle Shell-Bridge als Endarchitektur aufloesen
- direkte Restabhaengigkeiten zwischen `vision_platform` und `camera_app` reduzieren

Heute vorhanden:
- funktionierender Hybrid-Companion-Pfad
- Restkopplungen und app-nahe Reflection-Logik

Ergebnis:
- Camera Core und Integration Surface werden dauerhafter, frontendaermer und systemisch sauberer
- die langfristige Tragfaehigkeit steigt, weil `Companion-App = Modul` nicht einfriert

---

## 8. Konkrete Refactoring-/Arbeitspakete

Die folgenden Pakete sind als realistische naechste Arbeitseinheiten geeignet.

### Paket A: Camera Integration Surface beschreiben und stabilisieren

Betroffene reale Strukturen:
- `vision_platform.control.command_controller`
- `vision_platform.services.api_service`
- Capability-nahe Services
- Statusmodelle und Command-Result-Payloads

Ziel:
- eine explizite Surface-Sicht ueber bestehende Bausteine legen

### Paket B: Lifecycle-Fassade einfuehren

Betroffene reale Strukturen:
- `CameraService`
- `CommandController`
- Statusmodelle

Ziel:
- technische Service-Initialisierung von orchestratornaher Lifecycle-Sprache unterscheiden

### Paket C: `CameraHealth` modellieren

Betroffene reale Strukturen:
- `CameraStatus`
- `SubsystemStatus`
- Recording- und Interval-Status
- Hardware-Audit-Signale

Ziel:
- Fehlertext- und Flaglandschaft in eine explizite Health-Sicht ueberfuehren

### Paket D: Runtime-Eventfamilie einfuehren

Betroffene reale Strukturen:
- Command-Ausfuehrung
- Snapshot- und Recording-Flows
- Audit- und Traceability-Pfade

Ziel:
- echte Runtime-Events von Artefaktlogs und Shell-Dateien trennen

### Paket E: Zeitkontext standardisieren

Betroffene reale Strukturen:
- `CapturedFrame`
- `FrameMetadata`
- Traceability- und Artefaktmetadaten

Ziel:
- strukturierte Zeit-Provenienz in der Integrationsoberflaeche verankern

### Paket F: Artefaktreferenzen explizit machen

Betroffene reale Strukturen:
- Snapshot- und Recording-Ergebnisse
- Traceability
- Payload-Mappings

Ziel:
- subsystemlokale Artefaktlogik sauber vom spaeteren Gesamtlogging absetzen

### Paket G: Shell-Bridge als Uebergang isolieren

Betroffene reale Strukturen:
- `apps/local_shell/live_command_sync.py`
- `captures/wx_shell_sessions`
- companion-spezifische Reflection-Pfade

Ziel:
- Companion-Betrieb erhalten, aber Endarchitekturanspruch entfernen

### Paket H: Restkopplungen zwischen `vision_platform` und `camera_app` abbauen

Betroffene reale Strukturen:
- direkte Imports
- app-nahe Modelle mit subsystemischem Charakter

Ziel:
- `vision_platform` als primaere Integrationsoberflaeche staerken

### Paket I: Companion-nahe Reflection- und Presenter-Logik pruefen

Betroffene reale Strukturen:
- `vision_platform.services.companion_contract_service`
- `apps/local_shell`-nahe Reflection- und Zustandsmodelle
- UI-agnostische, aber app-lokal platzierte Hilfsschichten

Ziel:
- trennen, was wirklich companion-spezifisch bleiben darf, und was als allgemeiner Adapter- oder Integrationsbaustein verschoben werden sollte

---

## 9. Was vorerst bewusst bleiben darf

Nicht alles muss sofort umgebaut werden.

Vorerst bewusst bleiben darf:
- die bestehende Snapshot-, Recording- und Preview-Funktionalitaet
- der `Hybrid Companion`-Betrieb, solange er klar als Zwischenstufe gelesen wird
- CLI als lokaler Adapter fuer Betrieb, Diagnose und Tests
- vorhandene subsystemlokale Traceability- und Audit-Pfade
- bestehende Services und ihr grober Zuschnitt
- die aktuelle hostnahe Command-Oberflaeche als Basis fuer die spaetere Lifecycle-Ausdifferenzierung
- die aktuelle gute Kurzfrist-Kompatibilitaet zwischen Repo und Gesamtprojekt, solange sie nicht mit Endarchitektur verwechselt wird

Diese Dinge sind heute kein Hindernis, solange sie nicht falsch als Endzustand interpretiert werden.

---

## 10. Was explizit nur Uebergangsmechanismus ist

Folgende Teile muessen explizit als Uebergang gelesen werden:

- file-basierte Shell-Live-Sync-Bridge
- `captures/wx_shell_sessions` als IPC- und Reflexionspfad
- shell-spezifische Reflection-Modelle als primaere Lesart von State
- Mischformen, in denen Artefaktlogik, Statusprojektion und Eventcharakter in denselben Dateipfaden auftauchen
- direkte Restabhaengigkeiten von `vision_platform` auf `camera_app`, wo sie nur historisch oder migrationsbedingt bestehen
- app-zentrierte Lesarten, in denen Companion-Betrieb und Subsystem-Rolle nicht sauber getrennt sind

Diese Mechanismen sind fuer den aktuellen Betrieb legitim.
Sie duerfen aber nicht stillschweigend die Endarchitektur definieren.

---

## 11. Risiken

### Hohes Risiko

- Die Shell-Bridge friert zur faktischen Integrationsoberflaeche ein.
- Das Repo bleibt begrifflich `Kamera-App`, obwohl es systemisch als Subsystem gebraucht wird.
- Eventmodell und Health-Modell bleiben zu lange implizit.
- subsystemlokale Persistenz wird mit systemweitem Logging verwechselt.

### Mittleres Risiko

- Zeit-Provenienz bleibt zu flach fuer spaetere Korrelation.
- `vision_platform` und `camera_app` bleiben zu lange strukturell vermischt.
- Orchestrator-nahe Lifecycle-Sprache wird zu spaet von hostnahen Commands getrennt.
- kurzfristig gute Kompatibilitaet wird ueberschaetzt und verschleppt die noetige Mittelfrist-Transformation.

### Niedrigeres Risiko

- konkrete CLI-Envelope-Details
- konkrete API- oder LabVIEW-Zuschnitte
- genaue Platzierung einzelner frontendnaher Hilfsschichten

---

## 12. Priorisierte Empfehlungen

1. Verankere die Lesart `Camera Subsystem statt Kamera-App` in den Architektur- und Strategiedokumenten.
2. Leite aus `bootstrap`, `CommandController`, `CameraService`, `SnapshotService`, `RecordingService` explizit eine `Camera Integration Surface v0.1` ab.
3. Fuehre als naechste eigentliche Architekturerweiterung ein explizites `CameraHealth`-Modell ein.
4. Trenne hostnahe Command-Sprache und orchestratornahe Lifecycle-Sprache begrifflich und spaeter auch technisch.
5. Fuehre eine kleine typed Runtime-Eventfamilie ein, statt Eventcharakter weiter in Traceability- und Shell-Dateien zu verstecken.
6. Standardisiere Zeit-Provenienz in einem strukturierten Zeitkontext.
7. Benenne `recording_log`, `traceability` und verwandte Pfade explizit als subsystemlokale Artefaktperspektive, nicht als zentrales Logging.
8. Markiere die file-basierte Shell-Bridge in Code und Doku als Uebergangs-IPC.
9. Baue direkte `camera_app`-Restkopplungen unter `vision_platform` schrittweise ab.
10. Erhalte den funktionierenden `Hybrid Companion`-Pfad waehrend der Transformation, aber entkopple ihn von der Zielarchitektur.
11. Nutze die aktuell gute Kurzfrist-Kompatibilitaet aktiv, aber behandle sie nicht als Beweis, dass keine weitere Integrationsschicht mehr noetig ist.

---

## 13. Ergebnis / Strategische Leitentscheidung

Die strategische Leitentscheidung lautet:

Das bestehende Kamera-Repository wird **nicht** als wegzuwerfende Vorstufe behandelt und **nicht** unveraendert zur Endarchitektur erklaert.

Es wird als bereits starker, realer Vorlaeufer eines spaeteren `Camera Subsystems` gelesen und schrittweise in diese Zielrolle ueberfuehrt.

Die Strategie dafuer ist:
- vorhandenen Kern bewahren
- Integrationssurface explizit machen
- Lifecycle, Events, Health und Zeit-Provenienz nachziehen
- subsystemlokale Artefaktlogik gegen Gesamtlogging abgrenzen
- die lokale Shell klar als Companion- und Uebergangsschicht behandeln

Damit ist die Richtung klar:

**kein Neustart, keine Verwechslung von Companion-App und Zielmodul, sondern kontrollierte Transformation eines bereits starken Kamera-Repositories in ein belastbares Camera Subsystem fuer das Gesamtprojekt**
