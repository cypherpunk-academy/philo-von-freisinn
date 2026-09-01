# Open Source Kultur und die Dreigliederung des sozialen Organismus
<!-- version: 26. August 2026 | autor: Claude Opus -->

*Gegenstück zu „Open Source beweist die Dreigliederung". Dort geht es um die Freiheit im Geistesleben — hier um die Stelle, an der Open Source im Wirtschaftsleben unvollständig bleibt.*

## Ist Open Source überhaupt Wirtschaftsleben?

Ja — und zwar nicht am Rande, sondern im Kern.

Die wirtschaftliche Grundgeste ist vollständig da, in einer Reinheit, die sonst kaum irgendwo erreicht wird: Menschen arbeiten nicht für den eigenen Ertrag, sondern für einen Bedarf, den andere haben. Sie geben etwas in die Welt, das sie selbst nicht verkaufen. Der Nutzen entsteht bei jemand anderem. Das ist keine Gesinnung, das ist die tägliche Arbeitspraxis von Millionen Menschen.

Wer Open Source nur der Kultursphäre zurechnet, weil dort programmiert und nicht gehandelt wird, übersieht das. Es wird dort gewirtschaftet. Nur eben halb.

## Was fehlt?

Das soziale Hauptgesetz besteht aus zwei Aussagen, die nur zusammen einen Kreislauf ergeben.

Die erste: Der Einzelne soll die Erträgnisse seiner Arbeit nicht für sich selbst beanspruchen, sondern sie der Gesamtheit zukommen lassen.

Die zweite: Die Gesamtheit muss dafür die Bedürfnisse des Arbeitenden decken — durch die Arbeit der anderen.

Entscheidend ist der Zusatz, den Steiner macht: Das muss eine *Einrichtung* sein. Kein Appell, keine Gesinnungsfrage, keine Frage der Güte einzelner Menschen. Eine Struktur, die auch dann trägt, wenn niemand besonders gut ist und gerade nichts brennt.

Genau daran fehlt es. Nicht am Geld.

## Aber es fließt doch Geld — stimmt das Argument dann noch?

Es fließt tatsächlich, und zwar seit über einem Jahrzehnt und in erheblichem Umfang. Der Einwand muss ernst genommen werden, sonst führt man ein Gespenst vor.

**Die Core Infrastructure Initiative.** Angekündigt am 24. April 2014, siebzehn Tage nach der Offenlegung von Heartbleed. Amazon, Cisco, Dell, Facebook, Fujitsu, Google, IBM, Intel, Microsoft, NetApp, Rackspace, Qualcomm und VMware sagten je 100.000 Dollar pro Jahr über drei Jahre zu. Der Kontrast, der das erst verständlich macht: OpenSSL hatte bis dahin etwa 2.000 Dollar Spenden im Jahr erhalten. Als Heartbleed bekannt wurde, kamen knapp 9.000 Dollar herein. Finanziert wurden dann zwei Vollzeitentwickler. Die CII ist inzwischen in der OpenSSF aufgegangen.

**Die Meldung beim Build.** „139 packages are looking for funding" — das kommt von npm, seit Version 6.13, gespeist aus einem `funding`-Feld in der `package.json`.

**GitHub Sponsors.** Seit 2019. Inzwischen über 100 Millionen Dollar insgesamt, mehr als 70.000 Maintainer und Organisationen, über 280.000 Sponsoren. Die ersten zehn Millionen dauerten fast zwei Jahre, die letzten zehn Millionen fünf Monate.

**Die Sovereign Tech Agency.** Berlin, seit September 2022, hervorgegangen aus SPRIND. Über 24 Millionen Euro in Projekte wie systemd, PHP, FFmpeg, curl und GNOME.

**Die Open Source Pledge.** Von Sentry 2024 gestartet: mindestens 2.000 Dollar pro Entwickler und Jahr direkt an Maintainer. Sentry selbst zahlte 5.813 Dollar pro Entwickler, insgesamt 750.000.

Und nun die Zahl, um die es geht.

Tidelift befragt seit Jahren Maintainer. Im Erhebungsjahr 2024 — zehn Jahre nach der CII, fünf Jahre nach GitHub Sponsors, zwei Jahre nach dem Sovereign Tech Fund — werden 60 Prozent der Maintainer nicht bezahlt. Exakt derselbe Wert wie im Jahr davor. Nur 3 Prozent bekommen Geld von Open-Source-Stiftungen, und dieser Wert ist über alle drei Erhebungen stabil geblieben. Nur 1 Prozent erhält Zahlungen von Regierungen oder öffentlichen Stellen. 61 Prozent der unbezahlten Maintainer arbeiten allein. 60 Prozent haben aufgehört oder daran gedacht, 44 Prozent nennen Erschöpfung als Grund.

Das Geld fließt also — und die Kennzahl bewegt sich nicht.

Damit ist der Einwand beantwortet, aber die Antwort ist unbequemer als die ursprüngliche Behauptung. Es fehlt nicht an Mitteln. Es fehlt an der Form, in der die Mittel ankommen. Was existiert, ist eine Summe von Einzelentscheidungen, die dorthin fließen, wo etwas sichtbar geworden ist: nach Heartbleed zu OpenSSL, nach Log4j breiter, nach xz erneut. Der Rückstrom reagiert auf Katastrophen, nicht auf Bedarf.

Und dass es nicht am Geld an sich liegt, zeigt dieselbe Erhebung: Bezahlte Maintainer setzen wichtige Sicherheitspraktiken mit 55 Prozent höherer Wahrscheinlichkeit um als unbezahlte. Es wirkt, wo es ankommt. Es kommt nur bei den Falschen an — bei den Sichtbaren statt bei den Bedürftigen.

## Woran erkennt man die fehlende Form?

An drei Erscheinungen, die wie drei verschiedene Probleme aussehen und eines sind.

**Die Erschöpfung.** Der Maintainer als Verschleißteil. Jahrelange unbezahlte Pflege kritischer Infrastruktur, bis die Kraft nicht mehr reicht — und dann die Übergabe an den Erstbesten, der Hilfe anbietet. Der xz-utils-Vorfall ist der Modellfall: ein erschöpfter Maintainer, ein geduldiger Angreifer, der sich über Jahre als hilfsbereiter Nachfolger aufbaut, und am Ende eine Hintertür in einem Stück Software, das auf einem großen Teil der Serverinfrastruktur der Welt läuft. Das war kein Sicherheitsproblem, das sich sozial auswirkte. Das war ein Sozialproblem, das sich als Sicherheitsproblem zeigte. Erschöpfung ist die Angriffsfläche.

**Die Bedarfsblindheit.** Es wird produziert, was die Entwickler interessiert — nicht notwendig, was gebraucht wird. Neue Rahmenwerke im Überfluss, Dokumentation im Mangel. Barrierefreiheit, Wartung, unspektakuläre Bibliotheken: chronisch unterversorgt. Der Grund ist nicht charakterlich, sondern strukturell: Der Verwender hat keine verhandelnde Stimme. Er kann bitten, er kann selbst machen — aber er sitzt an keinem Tisch, an dem gemeinsam ermittelt wird, was in welcher Menge zu produzieren ist.

**Die Übernahme durch das Kapital.** Wo der Verwender doch Stimme hat, hat er sie über Geld — und dann zu laut. Ein Konzern bezahlt fünf Vollzeitstellen an einem Projekt und bestimmt damit die Richtung, ohne je Verantwortung übernommen zu haben. Das ist keine Assoziation. Das ist Einkauf von Einfluss in eine Struktur, die sich dagegen nicht wehren kann, weil sie für Verhältnismäßigkeit keine Rechtsform hat.

## Was ist das Bild für den halben Kreis?

Die npm-Meldung.

„139 packages are looking for funding" steht bei jedem Build da. Das Bedürfnis ist perfekt sichtbar gemacht — gezählt, verlinkt, automatisch aus dem Abhängigkeitsbaum erhoben — und bleibt folgenlos, weil Sichtbarkeit keine Verbindlichkeit erzeugt. Der Entwickler scrollt vorbei.

Man kann die Meldung übrigens abschalten. `--no-fund`, oder dauerhaft in der `.npmrc`.

Die erste Hälfte des sozialen Hauptgesetzes ist in dieser Kultur automatisiert. Die zweite ist ein Appell mit Ausschaltknopf.

## Löst Copyleft das nicht?

Copyleft ist ein Griff, der die Kraft des Gegners benutzt: Es wendet das Urheberrecht gegen dessen eigene Absicht. Wirksam — aber es baut auf dem alten Fundament auf. Es ist eine Umkehrung im Rechtsleben, kein neuer Grund.

Und es regelt ausschließlich die Weitergabe. Es sagt nichts darüber, wovon der lebt, der weitergibt. Die GPL schützt den Quelltext vor Einschließung. Sie schützt den Menschen nicht vor Verschleiß.

## Was folgt daraus?

Nicht, dass die These vom Anfang falsch wäre. In Open Source hat sich ein Stück Geistesleben selbst befreit — aus eigenem Impuls, ohne Erlaubnis und ohne Auftrag. Und die wirtschaftliche Geste ist dabei wirklich getroffen. Aber was sich da befreit hat, ruht auf einem Wirtschaftsleben, das es sich nicht selbst gegeben hat und das nach dem alten Prinzip läuft — und deshalb bleibt es auf die Dauer angreifbar an genau der Stelle, an der es am stärksten aussieht.

Zwei Dinge müssten hinzukommen.

Erstens der Verwender als verhandelnde Instanz — nicht als Bittsteller und nicht als Geldgeber, sondern als jemand, der am selben Tisch sitzt und mitträgt, was und wieviel realistisch entstehen kann. Das ist die Erzeuger-Verwender-Gemeinschaft. Sie ersetzt die Sichtbarkeit durch Verhandlung: Nicht wer am lautesten sichtbar wird, bekommt etwas, sondern wer im gemeinsamen Ermitteln als notwendig erkannt wurde.

Zweitens ein Rückstrom, der eine Form hat. Nicht Bezahlung — Bezahlung wäre die Rückkehr des alten Prinzips durch die Hintertür, denn dann wäre der Maintainer Dienstleister und der Verwender Kunde, und die ganze Geste wäre verloren. Sondern Deckung des Bedarfs. Der Maintainer arbeitet weiterhin nicht für Ertrag. Er arbeitet für den Bedarf der anderen. Nur muss er dabei nicht mehr verbrennen.

## Offene Fragen

**Der Wortlaut.** Das soziale Hauptgesetz steht in GA 34 („Geisteswissenschaft und soziale Frage"). Der Band ist bisher nicht im Korpus — er wäre für diesen Gedankengang und für das Korn-Konzeptpapier eine sinnvolle Ergänzung.

**Die Skalierung.** Bei zwanzig Menschen funktioniert Verhandlung am Tisch. Bei einer Bibliothek mit zehntausend Verwendern nicht. Elinor Ostroms achtes Gestaltungsprinzip — verschachtelte Einheiten — gibt darauf eine empirische Antwort, die sich mit Stafford Beers Rekursionsprinzip deckt. Siehe „Gesellschaftsinitiativen".

**Der Staat.** Der wirksamste der genannten Mechanismen, die Sovereign Tech Agency, ist staatlich. Die naheliegende Frage — Übergriff oder legitime Infrastrukturpflicht? — ist falsch gestellt. Der Staat als *Verwender* ist unproblematisch: Die Bundesverwaltung benutzt curl und systemd tatsächlich, hat also realen Bedarf und dürfte an jedem Tisch sitzen wie jeder andere Verwender auch. Der Übergriff beginnt nicht beim Geld, sondern bei der Bedarfsermittlung. Eine Vergabestelle entscheidet nach eigenen Kriterien, was förderwürdig ist — und nimmt damit genau die Funktion wahr, die der Assoziation zusteht: das gemeinsame Ermitteln des Notwendigen. Nicht der Zufluss ist die Pathologie, sondern das Urteil darüber, was gebraucht wird. Dass dieses Urteil derzeit in Berlin gefällt wird, ist ein Symptom dafür, dass es den Tisch nicht gibt. Ein sauberer Fall für die Off-Diagonale Recht → Wirtschaft.

## Zu den Zahlen

Die Maintainer-Daten stammen aus dem *State of the Open Source Maintainer Report* von Tidelift, Erhebung Mitte 2024, 437 Befragte. Zwei Einschränkungen: Tidelift verkauft Maintainer-Bezahlung als Produkt, hat also ein Interesse an der Aussage. Und es handelt sich um eine Selbstauswahl, nicht um eine Zufallsstichprobe. Die Größenordnung halte ich für belastbar, die Nachkommastellen nicht.

Die übrigen Angaben stammen aus den Ankündigungen der Linux Foundation (2014), dem GitHub-Blog (2026), der Sovereign Tech Agency und dem Sentry-Blog zur Open Source Pledge.