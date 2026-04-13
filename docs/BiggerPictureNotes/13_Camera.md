# 13_Camera

## Zweck dieser Note

Diese Note beschreibt das **Camera-Modul** als Fachmodul für Bildaufnahme, kamerabezogene Ereignisse und bildnahe Metadaten.

Sie soll langfristig verständlich machen:

- warum die Kamera als eigenes Hauptmodul behandelt wird,
- welche Rolle sie im Gesamtsystem spielt,
- welche Arten von Daten und Ereignissen aus dem Kamera-Modul entstehen,
- wie es sich zu Logging, Orchestrator, Safety und Zugriffsschichten verhält,
- und welche offenen Spannungen das Modul architektonisch prägen.

Diese Note ist eine **Architektur- und Kontextnote**, keine Implementierungsnote.

---

## Warum die Kamera ein eigenes Modul ist

Im Gesamtsystem ist die Kamera nicht nur ein UI-Add-on oder ein externer Hilfsprozess, sondern eine eigenständige technische Quelle für:

- Beobachtung des Prozesses
- Bild- oder framebezogene Dokumentation
- Trigger- oder zustandsgebundene Aufnahmen
- zeitlich relevante Ereignisse
- spätere Korrelation mit DAQ-, Motor- oder Safety-Zuständen

Würde man die Kamera nur als lose Zusatzfunktion behandeln, würde Folgendes schnell unklar werden:

- wann Aufnahmen relativ zu Run, Bewegung oder Safety-Ereignissen stattfanden,
- welche Metadaten zu einem Bild gehören,
- wie Aufnahmezustände in den globalen Ablauf passen,
- wie kamerabezogene Fehler und Ausfälle behandelt werden,
- und wie Bilder oder Frame-Referenzen sauber im Logging-Kontext landen.

Daraus folgt:
**Camera ist ein eigenes Fachmodul und keine bloße UI-Funktion.**

---

## Einordnung im Gesamtsystem

Das Camera-Modul ist das Fachmodul für:

- Snapshot-Aufnahmen
- Recording / Bildfolgen / Frame-Erzeugung
- Trigger- oder Ereignis-basierte Aufnahme
- kamerabezogene Zustände und Fehler
- Frame-Metadaten
- Health-/Heartbeat-Informationen, sofern relevant

Es steht insbesondere in Beziehung zu:

- **Orchestrator**, der kameraseitige Lebenszyklus und Run-Beteiligung koordiniert
- **Logging**, das Frame- und Aufnahmeereignisse dokumentiert
- **UI / API / CLI / MCP**, die Bildzustände und Kamerafunktionen beobachten oder anstoßen können
- ggf. **Safety**, falls Kameraausfall oder Bildtrigger fachlich relevant werden
- mittelbar auch zu **Acquisition** und **Motor**, wenn Bildaufnahme mit Messung oder Bewegung korreliert werden muss

Das Camera-Modul ist jedoch nicht:
- das globale Sessionmodul,
- nicht das zentrale Logging,
- nicht das Safety-Modul,
- und nicht die primäre Messquelle im DAQ-Sinn.

---

## Fachliches Zielbild

Das Camera-Modul soll als **eigenständige Bild- und Ereignisquelle** im Gesamtsystem fungieren.

Das Zielbild ist ausdrücklich nicht:

- eine lose Kamerafunktion in der Oberfläche,
- ein rein manueller Snapshot-Button,
- oder ein unstrukturierter Bildordner ohne Systemkontext.

Stattdessen soll das Modul sauber abbilden:

1. Aufnahmefunktionen  
2. Aufnahmezustände  
3. Frame-/Snapshot-Ereignisse  
4. Bildnahe Metadaten  
5. Trigger- und Run-Bezüge  
6. Fehler- und Health-Zustände  
7. Ausgabe an Logging, Orchestrator und Zugriffsschichten  

---

## Grundverständnis der Kamera im System

Im bisherigen Gespräch wurde die Kamera architektonisch eher als **Beobachtungs- und Dokumentationsquelle** verankert als als primäre Regelinstanz.

Das heißt:

- Die Kamera ist wichtig für Dokumentation und Korrelation.
- Sie kann prozessrelevante Ereignisse erzeugen.
- Sie kann Teil des orchestrierten Ablaufs sein.
- Sie ist aber nicht automatisch der zentrale Takt- oder Steuergeber des Systems.

Diese Einordnung ist wichtig, damit das Camera-Modul nicht fälschlich überladen wird.

---

## Verantwortlichkeiten des Camera-Moduls

### 1. Kamerazugriff und Kamerabereitschaft
Das Modul muss den technischen Zugriff auf die Kamera kapseln und deren grundlegende Betriebsbereitschaft abbilden.

### 2. Snapshot-Funktion
Einzelaufnahmen müssen als klar definierte Aktion unterstützt werden können.

### 3. Recording / fortlaufende Aufzeichnung
Falls relevant, muss das Modul auch fortlaufende Aufnahmen oder Bildfolgen abbilden können.

### 4. Trigger- oder Ereignisbezug
Das Modul muss Aufnahmeereignisse in den fachlichen Systemkontext einordnen können, etwa:
- durch explizite Triggerbefehle,
- durch Run-Phasen,
- oder durch Marker / Aktionen anderer Module.

### 5. Frame- und Bildmetadaten
Das Modul muss Metainformationen zu aufgenommenen Bildern bzw. Frames liefern können.

### 6. Kamerazustände und Fehler
Das Modul ist verantwortlich für:
- Ready / NotReady
- Running / Idle
- Fehlerzustände
- ggf. Heartbeat / Health

### 7. Ausgabe an andere Module
Camera muss Ereignisse, Zustände und Metadaten an andere Module bereitstellen.

---

## Nicht-Verantwortlichkeiten des Camera-Moduls

Diese Abgrenzung ist wichtig.

### Camera ist nicht verantwortlich für:

#### 1. Globale Session- oder Run-Steuerung
Diese Rolle liegt beim Orchestrator.

#### 2. Persistenzlogik des Gesamtsystems
Das Modul liefert kamera-bezogene Daten und Ereignisse, aber Logging organisiert die systemweite Persistenz.

#### 3. Zentrale Safety-Entscheidungen
Die Kamera kann Health-/Fehlerzustände liefern, entscheidet aber nicht selbst die Gesamtgefährdung.

#### 4. DAQ-Messwerterfassung
Bilder sind keine DAQ-Daten, auch wenn sie fachlich mit ihnen korreliert werden.

#### 5. Motorsteuerung
Die Kamera steuert nicht die Bewegung, auch wenn Bildaufnahme und Bewegung gekoppelt sein können.

---

## Die Kamera als Ereignisquelle

Ein wichtiger architektonischer Punkt ist:
Das Camera-Modul erzeugt nicht nur Bilddaten, sondern auch **kamera-bezogene Ereignisse**.

### Typische Ereignisse
- SnapshotRequested
- SnapshotCaptured
- RecordingStarted
- RecordingStopped
- FrameCaptured
- TriggerReceived
- CameraFault
- CameraDisconnected
- CameraRecovered

Diese Ereignisse sind oft fachlich wichtiger als das Bild selbst, weil sie:
- in Logging einfließen,
- in Run-Kontext eingeordnet werden,
- und später bei Rekonstruktion oder Korrelation helfen.

---

## Typische Datenarten des Camera-Moduls

Auch das Camera-Modul sollte datenmodelliert und nicht nur technisch betrachtet werden.

### 1. Snapshot-Ereignis
Eine einzelne Aufnahme mit Kontext und Metadaten.

### 2. Frame-Ereignis
Ein einzelner Frame oder eine Frame-Referenz während laufender Aufnahme.

### 3. Recording-Status
Informationen über laufende oder abgeschlossene Aufnahmephasen.

### 4. Kamera-Status- und Health-Daten
- Ready
- Busy
- Error
- Disconnected
- Fault
- ggf. Heartbeat

### 5. Kamera-Konfigurationskontext
- aktiver Modus
- Triggerbezug
- Aufnahmeparameter
- ggf. Session-/Run-Kontext

---

## Beziehungen zu anderen Modulen

---

## Beziehung zu Orchestrator

### Warum diese Beziehung wichtig ist
Die Kamera soll nicht isoliert arbeiten, sondern in den globalen Ablauf eingebettet sein.

### Was der Orchestrator typischerweise vom Camera-Modul braucht
- Ready / NotReady
- Prepared
- RecordingStarted
- RecordingStopped
- SnapshotDone
- Fault / Error
- AbortHandled

### Typische Befehle vom Orchestrator an die Kamera
- Configure
- Prepare
- Arm
- Start
- Stop
- Abort
- CaptureSnapshot

### Abgrenzung
Der Orchestrator koordiniert die Kamera, aber besitzt nicht deren Aufnahme- oder SDK-Fachlogik.

---

## Beziehung zu Logging

### Warum diese Beziehung wichtig ist
Die Kamera ist eine eigenständige Quelle für:
- Ereignisse
- Frame-/Snapshot-Referenzen
- Metadaten
- Fehlzustände
- Marker

### Was Logging vom Camera-Modul bekommen soll
- Snapshot-Ereignisse
- Frame-/Recording-Ereignisse
- Bild- oder Dateireferenzen
- Aufnahmekontext
- kamerabezogene Fehler
- Health-/Statusinformationen
- Konfigurations-Snapshots

### Wichtiger Punkt
Logging muss nicht das Bild selbst in derselben Struktur wie andere Streams speichern, aber es muss die Kameraereignisse und Referenzen sauber im Session-/Run-Kontext verankern.

---

## Beziehung zu Safety

### Aktueller Stand im Gespräch
Es ist noch nicht vollständig entschieden, ob die Kamera in jeder Betriebsart safety-relevant ist.

### Trotzdem architektonisch wichtig
Das Camera-Modul kann mindestens folgende Safety-relevante Zustände liefern:
- Heartbeat fehlt
- Kamera fällt aus
- Trigger funktioniert nicht
- Aufnahme startet nicht
- Modul meldet NOK

### Wichtige Abgrenzung
Nicht jeder Kamerafehler ist automatisch ein Safety-Trip.  
Ob die Kamera in einem bestimmten Systemzustand sicherheitskritisch ist, hängt vom späteren Einsatzfall ab.

### Architekturkonsequenz
Das Modul sollte Health-/Fault-Zustände sauber nach außen geben können, auch wenn die genaue Safety-Bewertung außerhalb des Moduls liegt.

---

## Beziehung zu UI / API / CLI / MCP

### Was diese Zugriffsschichten vom Camera-Modul brauchen
- Kamerabereitschaft
- aktueller Aufnahmestatus
- Snapshot-/Recording-Aktionen
- Fehleranzeigen
- ggf. Bildvorschau oder Frame-Referenzen
- Konfigurationszustand

### Wichtige Abgrenzung
Die Zugriffsschichten sollen die Kamera bedienen und beobachten können, aber die Kamera-Logik nicht selbst besitzen.

---

## Beziehung zu Acquisition und Motor

### Warum diese Beziehungen indirekt wichtig sind
Auch wenn die Kamera ein eigenes Fachmodul ist, kann sie fachlich eng gekoppelt sein an:
- Messphasen
- Bewegungszustände
- definierte Triggerpunkte
- Sessionmarker
- Safety-Ereignisse

### Beispiele
- Snapshot bei bestimmtem Bewegungszustand
- Frame-Dokumentation während aktiver Messung
- Aufnahmebeginn synchron zu Run-Marker
- Bildereignis nahe Safety-Trip

### Wichtig
Diese Kopplung soll über Orchestrator, Marker und Eventmodell abgebildet werden, nicht durch verdeckte Fachlogikvermischung.

---

## Was das Camera-Modul nach außen ausgibt

Das ist für die Architektur besonders wichtig.

---

## A. Ausgaben an Orchestrator

Der Orchestrator braucht vor allem lebenszyklus- und zustandsbezogene Informationen.

### Typische Ausgaben
- CurrentState
- IsReady
- RecordingStarted
- RecordingStopped
- SnapshotCaptured
- TriggerHandled
- Fault
- NotReadyReason
- ModuleHealth

---

## B. Ausgaben an Logging

Logging braucht ereignis- und metadatenreiche Kameraausgaben.

### Typische Ausgaben
- `CameraSnapshotEvent`
- `CameraFrameEvent`
- `CameraRecordingEvent`
- `CameraFaultEvent`
- `CameraHealthEvent`
- `CameraConfigSnapshot`
- Bild-/Dateireferenzen
- Trigger-/Run-Bezug

---

## C. Ausgaben an Safety

Sofern relevant, braucht Safety vor allem Zustands- und Health-Informationen.

### Typische Ausgaben
- Heartbeat
- OK / NOK
- Fault
- TriggerFailure
- RecordingFailure
- CameraUnavailable

---

## D. Ausgaben an UI / API / CLI / MCP

### Typische Ausgaben
- Live-Status
- Aufnahme aktiv / inaktiv
- Fehlerzustand
- Snapshot erfolgreich / fehlgeschlagen
- ggf. Frame-/Bildreferenz
- Kamerakonfiguration / Modus

---

## Zeitmodell des Camera-Moduls

Die Kamera ist aus Zeitsicht ein eigenes Themenfeld.

### Warum
Kameraereignisse können mehrere Zeitbezüge haben:

- Aufnahmezeit aus Kamerasicht
- Triggerzeit
- Host-Empfangszeit
- Session-Zeit
- ggf. Framezähler oder device-spezifische Zeitbasis

### Architekturkonsequenz
Das Camera-Modul darf Zeit nicht auf ein einziges Feld reduzieren.

Gerade für spätere Korrelation mit:
- DAQ-Daten
- Motor-Telemetrie
- Safety-Ereignissen
ist es wichtig, dass die Kameraereignisse sauber zeitlich verortbar bleiben.

### Wichtiger Punkt
Noch nicht abschließend geklärt ist, welche Zeitrepräsentation im ersten System verbindlich wird.  
Das Modul muss aber architektonisch bereit sein für:
- native Kamerazeit
- Host-Zeit
- Session-Zeit
- Zeitqualitätsinformation

---

## Kamera und Triggerbezug

Ein besonders wichtiger offener Architekturpunkt ist die Frage nach der **primären Kamerarolle**.

### Mögliche Rollen
- reine Beobachtungsquelle
- Snapshot-Dokumentation
- aufnahmebezogene Begleitquelle zum Run
- triggernahe Ereignisquelle
- in Einzelfällen sicherheitsrelevante Zusatzquelle

### Warum dieser Punkt wichtig ist
Davon hängen später ab:
- Zustandsmodell
- Loggingdetailtiefe
- Triggersemantik
- Zeitmodell
- Run-Integration
- Fehlerbehandlung

Diese Rolle ist noch nicht vollständig festgelegt, muss aber in späteren Notes bewusst entschieden werden.

---

## Interne Strukturidee des Moduls

Diese Note definiert noch keine endgültige Klassenstruktur, aber einige funktionale Teilbereiche sind bereits klar.

### Sinnvolle innere Teilbereiche

#### 1. CameraControl
- Prepare / Arm / Start / Stop / Abort
- Snapshot anstoßen
- Recording steuern

#### 2. CameraEvent / Frame Publication
- Snapshot-Ereignisse
- Frame-Ereignisse
- Trigger-Ereignisse
- Statusänderungen

#### 3. CameraState / Health
- Ready / Busy / Fault
- Verbindungszustand
- Heartbeat / Health

#### 4. Configuration Layer
- Kameramodus
- Aufnahmekontext
- Triggerparameter
- ggf. Session-/Run-bezogene Einstellungen

#### 5. Integration Layer
- Anbindung an Logging
- Integration in Orchestrator-Lebenszyklus
- Bereitstellung für Zugriffsschichten

Diese Strukturidee ist vor allem deshalb wichtig, weil sie das Modul klar von UI oder Ad-hoc-Aufnahmelogik trennt.

---

## Design-Rationale

### Warum Camera nicht als bloße UI-Funktion behandelt wird
Weil Bildaufnahme und Frame-Ereignisse Teil des Systemkontexts und späterer Rekonstruktion sind.

### Warum Camera ein eigenes Modul und kein Logging-Unterordner ist
Weil Aufnahme- und Zustandslogik vor Persistenz kommen und fachlich getrennt werden müssen.

### Warum Camera trotz offener Detailfragen jetzt schon als Hauptmodul sinnvoll ist
Weil ihre systemische Rolle bereits klar genug ist:
- eigenständige Daten- und Ereignisquelle,
- orchestrierbar,
- loggbar,
- potenziell health-/safety-relevant.

---

## Was in späteren Notes noch vertieft werden muss

Diese Note setzt den Rahmen, beantwortet aber nicht alle Details.

Später noch zu klären sind insbesondere:

- primäre Kamerarolle im Zielsystem
- Triggermodell
- genaue Frame-/Snapshot-Datentypen
- Metadaten-Mindestumfang
- Zeitrepräsentation
- ob und wann Kamera safety-relevant ist
- wie Bilddaten und Bildreferenzen konkret persistiert werden

---

## Ergebnis dieser Note

Das Camera-Modul ist ein eigenständiges Fachmodul für **Bildaufnahme, kamera-bezogene Ereignisse und Bildmetadaten**.

Es ist geprägt durch folgende Spannungen:

- Beobachtungsquelle vs. prozessnahes Modul
- Snapshot vs. Recording
- Ereignisbezug vs. Bildinhalt
- Kameraeigene Zeit vs. Systemzeit
- UI-Nähe vs. headless Integration
- optionale vs. kritische Rolle im Ablauf

Gerade diese Spannungen machen es sinnvoll, die Kamera früh als eigenes Modul zu modellieren, statt sie nur als technische Zusatzfunktion zu behandeln.