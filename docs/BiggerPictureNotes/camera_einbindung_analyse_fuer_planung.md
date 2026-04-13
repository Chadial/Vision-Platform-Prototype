# Kamera-Einbindung-Analyse fuer Gesamtprojektplanung

## Zweck

Diese Note ist eine strukturierte Analyse fuer eine planende LLM.
Sie bewertet, wie das aktuelle Repository in ein groesseres System eingebunden werden kann, welche Anpassungen an der heutigen Kamera-App wahrscheinlich noetig sind und wie die vorlaeufigen Anforderungen aus `docs/13_Camera.md` geschaerft werden sollten.

## Eingabekontext

### Primaere temporaere Kontextquellen
- `docs/00_Systemkontext_und_Zielbild.md`
- `docs/13_Camera.md`

### Relevanter bestehender Repository-Kontext
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `docs/ROADMAP.md`
- `docs/GlobalRoadmap.md`
- `docs/HOST_CONTRACT_BASELINE.md`
- `apps/local_shell/README.md`
- `apps/local_shell/STATUS.md`

## Kurzfazit

Das Vorhaben ist grundsaetzlich gut anschlussfaehig, aber nicht ohne begriffliche und architektonische Klaerung.

Die gute Nachricht:
- Das Repository verfolgt bereits wesentliche Zielprinzipien des groesseren Systems: headless-orientierte Kernlogik, getrennte Services, host-neutraler Command-Layer, klare Trennung von UI und Kameralogik, vorbereitete spaetere Portierung nach C#/.NET.
- Die heutige Kamera-App ist nicht nur eine GUI, sondern bereits ein Hybrid-Companion ueber einem wiederverwendbaren Kern.
- Snapshot, Preview, Recording, Konfiguration, Save-Path-Steuerung und hostseitige Kommandierung sind bereits vorhanden.

Die kritische Einschraenkung:
- Das aktuelle Repository ist fachlich noch als Kamera-Subsystem mit Host-Anbindung modelliert, nicht als voll integriertes Modul in einem uebergeordneten Orchestrierungs-, Logging-, Safety- und Multi-Modul-System.
- `13_Camera.md` beschreibt die Kamera bereits sinnvoll als eigenes Fachmodul, bleibt aber an mehreren wichtigen Stellen zu offen, damit daraus spaeter eindeutige Modulgrenzen und Integrationsvertraege abgeleitet werden koennen.

Die zentrale Bewertung lautet daher:
- Die aktuelle Kamera-App sollte nicht als spaeterer Gesamtsystemkern betrachtet werden.
- Sie ist aber eine gute Ausgangsbasis fuer ein einbettbares `Camera Subsystem`, wenn ihre Rolle explizit von `laufender App` zu `host-/orchestrator-faehigem Modul mit optionalen Frontends` umgedeutet und technisch weiter entkoppelt wird.

## Einschatzung des Vorhabens

### Gesamturteil
- `machbar`: ja
- `anschlussfaehig zur aktuellen Codebasis`: ja
- `ohne Architekturkorrektur sinnvoll einbettbar`: nur teilweise
- `groesstes Risiko`: Begriffs- und Verantwortungsunschärfe zwischen Kamera-App, Kamera-Kern, Orchestrator, Logging und Safety

### Warum das Vorhaben gut passt
- Das Zielbild des groesseren Systems ist `headless first`.
- Das Repository verfolgt bereits eine Architektur mit getrennten Schichten fuer Driver, Services und UI.
- Der aktuelle Host-Control-Ansatz passt gut zu einer spaeteren Einbettung in Orchestrator, LabVIEW oder andere Host-Systeme.
- Die bestehende Trennung zwischen `vision_platform` und `camera_app` ist ein guter Uebergang fuer spaetere Extraktion eines stabilen Kamera-Kerns.

### Warum das Vorhaben noch nicht fertig passt
- Die aktuelle Laufzeitform ist noch stark auf `Hybrid Companion` optimiert: sichtbare wx-Shell plus externer Host.
- Die heutige Live-Steuerung der Shell verwendet einen lokalen file-basierten Session-Bridge-Mechanismus. Das ist fuer den aktuellen Stand brauchbar, aber kein plausibles Langzeitmodell fuer ein groesseres Kernsystem.
- Logging ist heute im Repository stark auf kamera- und artefaktnahe Traceability fokussiert, noch nicht auf moduluebergreifende Systemereignisse.
- Orchestrator-Semantik in deinem Zielbild ist groesser als die aktuelle `CommandController`-Semantik.
- Safety ist im Zielbild ein priorisiertes Supervisor-Modul; im aktuellen Kamera-Repo ist Safety eher indirekt vorbereitet als explizit integriert.

## Wichtigste Architektur-Differenz

### Zielbild des groesseren Systems
- mehrere Hauptmodule
- zentraler Orchestrator fuer Lebenszyklus
- moduluebergreifendes Logging
- moegliche Safety-Eskalation
- mehrere Clock-Domains
- spaetere mehrere Zugriffsschichten

### Heutiger Schwerpunkt des Repositories
- ein leistungsfaehiges Kamera-Subsystem
- host-neutrale Kamera-Kommandierung
- optional sichtbare lokale Shell
- fokus auf Preview, Snapshot, Recording, ROI, Focus und hostgesteuerte Bedienung

### Konsequenz
Die Kamera-App sollte kuenftig nicht als das eigentliche Produktzentrum behandelt werden, sondern als Kombination aus:
- `Camera Core / Camera Subsystem`
- `Camera Host Adapter`
- `Optional Local Shell`

## Empfohlene Ziel-Rollen im Gesamtsystem

### 1. Camera Subsystem Core
Verantwortlich fuer:
- Kamerazugriff
- Konfiguration
- Snapshot
- Recording
- Preview-Frame-Bereitstellung
- kameraeigene Status- und Fehlerzustaende
- kamerabezogene Ereignisse und Metadaten

Nicht verantwortlich fuer:
- globale Sessionsteuerung
- moduluebergreifendes Logging
- globale Safety-Entscheidungen
- fachliche Ablaufregeln ausserhalb der Kamera

### 2. Camera Integration Surface
Verantwortlich fuer:
- orchestratorfaehige Kommandos
- status- und eventfaehige Ausgabe
- stabile Integrationsvertraege
- spaetere Transportabbildungen fuer LabVIEW, API oder C#

### 3. Optional Camera UI Shell
Verantwortlich fuer:
- lokales Preview
- lokale Bedienung
- Diagnose
- Setup, Fokus, ROI und manuelle Tests

Wichtig:
- Die Shell sollte ein optionaler Consumer des Kamera-Kerns sein, nicht dessen Besitzschicht.

## Konkrete Anpassungen an der Kamera-App

### A. Begrifflich-architektonische Anpassung
Die wichtigste Anpassung ist nicht zuerst technisch, sondern begrifflich:

Die heutige `KameraApp` sollte in der Planung nicht mehr als primaere Einheit verstanden werden.
Stattdessen sollte die Planungslogik unterscheiden zwischen:
- `Camera Module` oder `Camera Subsystem`
- `Camera Shell` oder `Camera Frontend`
- `Camera Integration Contract`

Empfohlene Planungsregel:
- Alles, was fuer Orchestrator, Logging, Safety und andere Module wiederverwendbar sein muss, darf nicht in einer app-zentrierten Begriffswelt eingefroren werden.

### B. Host-Control zu Orchestrator-Control erweitern
Heute vorhanden:
- host-neutrale Command-Oberflaeche
- Statusabfragen
- Snapshot- und Recording-Befehle
- Konfigurationsanwendung

Fuer das groessere System fehlt zusaetzlich eine klarere Einordnung in:
- `Prepare`
- `Arm`
- `Start`
- `Stop`
- `Abort`
- `Recover`
- `GetHealth`
- `GetCapabilities`

Empfehlung:
- die bestehende Command-Oberflaeche nicht ersetzen, sondern in eine explizite Modul-Lifecycle-Schicht einordnen
- Kamera-Kommandos von Orchestrator-Lifecycle-Kommandos begrifflich trennen

### C. Event-Modell schaerfen
Heute ist der Fokus stark auf Result-Payloads und Status-Snapshots.
Fuer das groessere System wird zusaetzlich ein expliziteres Event-Modell noetig.

Noetig sind mindestens unterscheidbare Klassen von Ereignissen:
- Lifecycle Events
- Capture Events
- Recording Events
- Fault Events
- Health Events
- Configuration Events
- Trigger Events

Empfehlung:
- nicht nur command/result denken
- sondern `commands`, `state`, `events` und `artifacts` als getrennte Integrationsarten modellieren

### D. Logging-Anbindung neu rahmen
Im grossen System darf `Logging` nicht mit `Dateiablage der Kamera` verwechselt werden.

Die Kamera sollte liefern:
- Ereignisse
- Artefakt-Referenzen
- Konfigurations-Snapshots
- Zeitstempel mit Herkunft
- Fehler- und Health-Meldungen

Das uebergeordnete Logging-System sollte verantworten:
- Session-/Run-Zuordnung
- moduluebergreifende Korrelation
- persistente Gesamtsicht
- Auditierbarkeit ueber mehrere Quellen

Empfehlung:
- die Kamera-Persistenz als lokales Artefaktmanagement ansehen
- das System-Logging als getrennten Consumer/Owner modellieren

### E. Zeitmodell explizit erweitern
`13_Camera.md` erkennt das Problem korrekt, ist aber noch zu offen.

Fuer spaetere Planbarkeit sollte die Kamera mindestens auf folgende Zeitfelder vorbereitet werden:
- `device_timestamp` oder kameraeigene Zeit, falls vorhanden
- `host_received_at`
- `host_monotonic_at`
- `session_time` oder `run_time`, falls vom Gesamtsystem vergeben
- `time_quality` oder `time_source`

Empfehlung:
- Zeit nicht als einzelnes Feld in Event- oder Metadatentypen modellieren
- sondern als kleinen strukturierten Zeitkontext

### F. Health und Safety trennen
Aktuell ist die Kamera in deinem Note-Entwurf sinnvollerweise nicht selbst das Safety-Modul.
Das sollte beibehalten werden.

Aber:
- Die Kamera braucht ein expliziteres Health-Modell.
- Safety braucht klar getrennt davon nur konsumierbare Signale.

Empfehlung fuer die Planung:
- `CameraHealth` als kamerainterne bzw. kamerabezogene Bewertung
- `SafetyImpact` nicht in der Kamera entscheiden
- nur eindeutig exportierbare Signale wie `degraded`, `faulted`, `heartbeat_missing`, `trigger_unavailable`, `recording_failed`

### G. File-basierte Shell-Steuerung als Zwischenloesung markieren
Der aktuelle file-basierte Live-Sync der wx-Shell ist fuer den momentanen Companion-Zustand plausibel.
Fuer das groessere System sollte er aber explizit als Uebergangsmechanismus markiert bleiben.

Empfehlung:
- nicht als Endarchitektur in die Gesamtplanung uebernehmen
- spaeter ersetzen durch einen host-neutralen In-Process-Service-Seam oder einen expliziten Adapter

## Bewertung von `13_Camera.md`

### Was an der Note bereits gut ist
- Sie behandelt die Kamera korrekt als eigenes Fachmodul.
- Sie grenzt Kamera sauber gegen UI, Logging, Safety und Orchestrator ab.
- Sie erkennt die Relevanz von Ereignissen, nicht nur von Bilddaten.
- Sie benennt die Spannungen Snapshot vs. Recording, Beobachtung vs. prozessnahe Rolle, Kamerazeit vs. Systemzeit.
- Sie ist als Kontextnote gut geeignet.

### Was der Note noch fehlt, damit sie planungsstark wird
- klarere Unterscheidung zwischen `Kamera als Modul`, `Kamera-App`, `Frontend` und `Integrationsadapter`
- explizite Trennung von `Commands`, `State`, `Events`, `Artifacts`
- klarerer Lifecycle-Bezug zum uebergeordneten Orchestrator
- explizite Health-Schnittstelle statt nur losem Fault-/Heartbeat-Bezug
- deutlicherer Unterschied zwischen kameraeigener Persistenz und systemweitem Logging
- eine erste Minimalmenge wirklich benoetigter Metadaten
- ein expliziter Integrationshinweis, dass Preview ein Consumer-Fall ist, aber nicht die Kernrolle des Moduls

## Empfohlene inhaltliche Nachschaerfung fuer `13_Camera.md`

Die folgende Umdeutung wuerde die Note deutlich belastbarer machen.

### 1. Rolle explizit festlegen
Empfohlene Formulierung:
- Das Camera-Modul ist ein `einbettbares Subsystem fuer Bildaufnahme und kamera-bezogene Ereignisse`.
- Eine lokale Kamera-App oder Shell ist nur eine moegliche Zugriffsschicht auf dieses Subsystem.

### 2. Integrationsarten explizit machen
Ergaenze einen Abschnitt wie:

- `Commands`:
  - ConfigureCamera
  - Prepare
  - Arm
  - StartRecording
  - StopRecording
  - Abort
  - CaptureSnapshot
  - QueryStatus
  - QueryHealth
- `State`:
  - readiness
  - acquisition_state
  - recording_state
  - configuration_state
  - last_fault
  - current_health
- `Events`:
  - snapshot_captured
  - recording_started
  - recording_stopped
  - frame_available
  - camera_faulted
  - camera_recovered
  - trigger_received
  - configuration_applied
- `Artifacts`:
  - saved_image_reference
  - recording_segment_reference
  - metadata_reference
  - run_context_reference

### 3. Logging-Beziehung praezisieren
Empfohlene Regel:
- Das Camera-Modul darf Bilddaten und kameraeigene Artefaktmetadaten erzeugen.
- Das Gesamtsystem-Logging ist jedoch fuer die moduluebergreifende Einordnung und Persistenzverknuepfung verantwortlich.

### 4. Health-Modell ergaenzen
Empfohlene Minimalfelder:
- availability
- readiness
- degraded_reason
- fault_reason
- heartbeat_state
- last_successful_capture_at
- last_successful_configuration_at

### 5. Zeitmodell greifbarer machen
Empfohlene Minimalregel:
- Jedes wichtige Kameraereignis sollte mehr als eine Zeitreferenz tragen koennen.
- Zeitinformationen sollten als strukturierter Kontext statt als einzelner Timestamp modelliert werden.

### 6. Preview abgrenzen
Empfohlene Klarstellung:
- Preview ist eine wichtige Nutzungsform der Kamera, aber nicht die definierende Kernverantwortung des Moduls.
- Preview-Rendering und UI-Interaktion gehoeren in Zugriffsschichten bzw. Frontends.

## Vorlaeufige Anforderungs-Schaerfung fuer die Gesamtplanung

### Mindestfaehigkeiten des Camera-Moduls im Zielsystem
- Kamera technisch initialisieren und freigeben koennen
- Konfiguration kontrolliert anwenden koennen
- Snapshot ausloesen koennen
- Recording starten und stoppen koennen
- einen klaren Modulstatus bereitstellen
- ein klares Health-Signal bereitstellen
- kamera-bezogene Ereignisse publizieren koennen
- Bild-/Artefakt-Referenzen samt Mindestmetadaten ausgeben koennen
- vom Orchestrator steuerbar sein
- ohne GUI betreibbar sein

### Mindestfaehigkeiten der optionalen Camera-App oder Shell
- Live-Preview anzeigen
- Kamerastatus sichtbar machen
- lokale Setup-Aktionen anbieten
- Snapshot und Recording manuell anstossen koennen
- ROI/Fokus/Setup fuer Bediener abbilden koennen
- externe Steuerung sichtbar reflektieren koennen

### Explizit noch nicht festzurren
- finales Transportsystem
- endgueltiges Event-Bus-Design
- finale Persistenzform fuer Bilddaten
- endgueltige Safety-Politik
- genaue Trigger-Topologie
- vollstaendige C#-Vertragsfamilie

## Risiken und offene Entscheidungen

### Risiko 1: App und Modul werden vermischt
Wenn `KameraApp` weiterhin die dominante Denkeinheit bleibt, drohen spaetere Verkopplungen zwischen UI, Workflowlogik und Integrationsschnittstellen.

### Risiko 2: Logging wird zu kameralokal gedacht
Wenn Logging nur als Bildspeicherung verstanden wird, fehlt spaeter die moduluebergreifende Rekonstruktion.

### Risiko 3: Orchestrator wird nur als umbenannter Host gelesen
Das groessere Zielbild braucht mehr als eine command-getriebene Kamerasteuerung. Es braucht Modul-Lifecycle und systemische Koordination.

### Risiko 4: Safety-Semantik wird zu frueh oder zu spaet festgelegt
Wenn die Kamera zu frueh als safety-kritisch modelliert wird, entsteht Uebermodellierung. Wenn das Thema ignoriert wird, fehlen spaeter exportierbare Signale.

### Risiko 5: Zeitmodell bleibt zu abstrakt
Ohne fruehen Minimalstandard fuer Zeitkontexte wird spaetere Korrelation unnoetig teuer.

## Empfohlene Planungsentscheidung fuer die naechsten Schritte

### Kurzfristig
- `13_Camera.md` in Richtung `einbettbares Camera Subsystem` nachschaerfen
- den Unterschied zwischen Kern, Integrationssurface und optionaler Shell explizit machen
- ein minimales Kamera-Integrationsmodell fuer `commands/state/events/artifacts/health` festhalten

### Mittelfristig
- den bestehenden Command-Layer des Repositories auf Orchestrator-Kompatibilitaet abbilden
- die file-basierte Shell-Steuerung als Uebergangsadapter dokumentieren
- kamerabezogene Zeit- und Metadaten auf einen kleinen strukturierten Kern standardisieren

### Nicht vorschnell tun
- keine Endarchitektur fuer Transport oder Event-Bus festschreiben
- nicht die wx-Shell zur primaeren Integrationsoberflaeche erklaeren
- nicht versuchen, Logging, Safety und Orchestrator schon in der Kamera selbst aufzugehen zu lassen

## Nutzbare Gesamtbewertung fuer eine planende LLM

Wenn das groessere System geplant wird, sollte die Kamera nicht als isolierte `App` betrachtet werden, sondern als frueh bereits gut entwickeltes, aber noch umzuinterpretierendes `Subsystem`.

Die vorhandene Codebasis ist dafuer wertvoll, weil sie bereits bietet:
- headless-nahe Service-Trennung
- wiederverwendbare host-neutrale Kommandierung
- klare UI-Abgrenzung im Zielmodell
- nachweisbare Snapshot-/Recording-/Preview-Pfade
- vorbereitete Portierbarkeit

Die Hauptaufgabe ist daher nicht primaer eine technische Neuerfindung, sondern eine kontrollierte Re-Rahmung:
- von `kameraorientierter Companion-App mit Host-Steuerung`
- zu `einbettbarem Kamera-Subsystem mit optionaler lokaler Shell und spaeteren Integrationsadaptern`

## Konkrete Empfehlung

Fuer die Gesamtplanung sollte `13_Camera.md` nicht verworfen, sondern um drei Kernaussagen ergaenzt werden:
- `Camera ist ein einbettbares Subsystem, nicht nur eine App-Funktion.`
- `Die Shell ist nur eine Zugriffsschicht, nicht die Besitzschicht des Kamera-Verhaltens.`
- `Die Integrationssicht des Kamera-Moduls muss explizit in commands, state, events, artifacts und health beschrieben werden.`
