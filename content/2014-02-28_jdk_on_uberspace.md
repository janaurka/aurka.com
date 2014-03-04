Title: JDK und Java Play Framework bei den Übernauten 
Date: 2014-02-28
Tags: jdk, java, play, framework, uberspace
Category: Tech
Author: janssen

Für ein Projekt habe ich mir auf einem Uberspace das Oracle JDK installiert und das Java Play Framework installiert.

Hint:
Solltet ihr etwas mit der JDK oder gleich mit dem Play Framework machen wollen; bitte beachtet, dass es sich um Shared-Hosting handelt. Ich verwende die Instanz nur als Testumgebung, da ich in einem kleinen Team eine Play Applikation entwickeln soll/muss und wir ein kleine Testumgebung benötigen. Solange eure Applikation jedoch nicht allzuviel CPU und RAM (hier ist, meine ich einmal gelesen zu haben, 512MB pro Prozess das Maximum!) fressen, sollte einem produktiven Einsatz nichts im Wege stehen. Aber bei Java Applikationen ist dieser Hinweis sicher nicht fehl am Platz. ;-) 


Hier ein kurzes Installations-HowTo:

## JDK Installation
(Bezüglich der Installation habe ich mich am [Blog von Markus Heberling](http://markus.heberling.net/2013/04/11/java-auf-dem-uberspace/) orientiert).

Heruntergeladen kann man das JDK bei [Oracle](http://www.oracle.com/technetwork/java/javase/downloads/jdk7-downloads-1880260.html)

Weil Oracle seine JDK Downloads x-mal umleitet und `wget` daran keine Freude hatte (und `toast` verwendet ja auch `wget`), habe ich mir die JDK bei mir lokal heruntergeladen und dann wie `scp` auf den Uberspace geladen. Auf jeden Fall benötigt ihr ein 64bit JDK als .tar.gz auf dem Uberspace-Account.


Dann wird getoastet:

	toast add <path-to-jdk/jdk-7u<build>-linux-x64.tar.gz>
	toast build jdk
	toast arm jdk

Das wars dann auch bereits.

## Ein Java Play Projekt starten
Java Play herunterladen:

	wget http://downloads.typesafe.com/play/2.2.1/play-2.2.1.zip #http://www.playframework.com/download

entpacken

	unzip play-2.2.1.zip -d <Pfad wohin entpackt werden soll>

zu $PATH hinzufügen:

	export PATH=$PATH:<Pfad-zu-Java-Play>

und ausführbar machen:

	chmod +x -R <Pfad-zu-Java-Play>

Java Play kann nun beliebig verwendet werden. Um ein neues Projekt zu erstellen ist folgendes zu tun:

	cd /var/www/virtual/<dein-user>/<auf-welche-domain-du-java-play-auch-immer-lauffen-lassen-willst; oder halt html>
	play new <projektname> #erstellt das Projekt, es folgend Angaben zum Namen und ob mit Scala oder Java

Um mit dem Projekt nun zu arbeiten muss zuerst in das Verzeichnis gewechselt werden und dann kann der Spaß beginnen:

	cd <path-zum-Projekt>
	play #öffnet die Play Console

Um das Projekt auszuliefern muss zuerst ein freier Port beantragt werden. In etwa [so](https://twitter.com/ubernauten/status/439479931144531970). Anschliessend einfach laufen lassen:

	run <port-nummer>

Dann ist das Projekt wie Browser zugreiffbar.


 
