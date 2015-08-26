Title: Mediagoblin auf einem Uberspace
Date: 2013-11-19
Tags: mediagoblin, uberspace, install, deploy, howto, tech, python, pypi, pip, easy_install, photo, pictures
Category: tech
Slug: mediagoblin-auf-uberspace
Picture: mediagoblin_header.png
Author: janssen

(Zuletzt aktualisiert am 11. Juli 2014; kleinere Ergänzungen zur Verwendung von PostgresSQL)

Bei den [Ubernauten](https://uberspace.de "Uberspace.de") lässt sich [Mediagoblin](http://www.mediagoblin.org/ "Mediagoblin.org") installieren - auch wenn es doch ziemlich viel gebastel ist. Ich hoffe ich kann jemandem mit dieser Anleitung ein paar Minuten/Stunden Arbeit ersparen.

# Über Mediagoblin
Mediagoblin ist ein in Python geschrieben und ein unter AGPL stehendes Replacement für Fotoplattformen wie flickr oder 500px und/oder für Musikplattforen wie Soundcloud. Es kann gar 3D-Dokument darstellen oder Filme abspielen. Kurz: Ein kleines Mediacenter.

# Installation

## Vorbereitungen

Diese Anleitung verwendet Postgres als Datenbank für Mediagoblin. Defaultmässig wird auf Sqlite zurückgegriffen - wenn ihr ohne Postgres auskommen wollt, dann vergesst diesen Punkt.

Wir müssen also zuerst postgres für den Uberspace konfigurieren. Hierfür muss nur ein Script angekickt werden:
	uberspace-setup-postgresql

Nun sollte man sich laut uberspace-doku einmal neu einloggen.

User erstellen:

	createuser mediagoblin

Datenbank erstellen (mit dem Owner des soeben erstellen Users ’mediagoblin’:

	createdb -E UNICODE -O mediagoblin mediagoblin

Nun müsst ihr euch überlegen, wie ihr auf euer Mediagoblin zugreiffen wollt. Ich mache dies via Subdomain mediagoblin.aurka.com.
Also muss unter `/var/www/virtual/<Uberspace Account>/` ein Directory mit dem Namen `mediagoblin.aurka.com` erstellt werden.
Da Mediagoblin wie `git` gepullt wird, lasse ich gerade `git` den Ordner erstellen:

	cd /var/www/virtual/<Uberspace Account>
	git clone git://gitorious.org/mediagoblin/mediagoblin.git mediagoblin.aurka.com
	cd mediagoblin.aurka.com
	git submodule init && git submodule update

Das `git`-Repository ist momentan auf dem master-branch. Mit diesem habe ich nie eine laufende Version hingekriegt. Allgemein macht es Sinn, auf den aktuellesten Tag zu wechseln - mit diesem dürfte Mediagoblin am stabilsten laufen. In meinem Falle ist dies Tag v0.5.1.

	git checkout v0.5.1


Nun wird mit `virtualenv` eine virtuelle Python Umgebung erstellt:

	virtualenv -p python2.7 --system-site-packages .

Diese virtuelle Umgebung muss nun aktiviert werden:

	source bin/activate

Jetzt verfügen wir über eine eigene virtuelle Python-Umgebung, fügen wir nun also die benötigten Pys hinzu. Ich verwende hierzu `pip`, natürlich kann auch `easy_install` verwendet werden:

	./bin/pip install lxml
	./bin/pip install psycopg2
	./bin/pip install paste
	./bin/pip install flup
	./bin/pip install sqlalchemy

Mediagoblin benötigt zusätzlich die Python Image Library (PIL). Dort gibt es jedoch etwas handarbeit, deshalb wird es nicht via Paketmanager installiert:
Aktuellste PIL Version von der [PIL-Homepage](http://www.pythonware.com/products/pil/ "PIL Homepage") herunterladen.
(Sollten Probleme mit PIL aufkommen: Die Ubernauten stellen eine eigene Dokumententation zur Installation von PIL zu verfügung. Diese ist [hier](https://wiki.uberspace.de/development:python#pil) zu finden.)

	mkdir PIL
	wget http://effbot.org/downloads/Imaging-1.1.7.tar.gz
	tar xvfz Imaging-1.1.7.tar.gz
	cd Imaging-1.1.7

PIL sollte die JPG, TIFF, etc. Libraries eigentlich automatisch finden - tut es aber nicht. In der setup.py können wir dies nun aber ändern:
`vim setup.py` -> Die Nummern sind die Zeilennummern, damit ihr nicht lange suchen müsst ;-)

	36 TCL_ROOT = "/usr/lib64"
	37 JPEG_ROOT = "/usr/lib64"
	38 ZLIB_ROOT = "/usr/lib64"
	39 TIFF_ROOT = "/usr/lib64"
	40 FREETYPE_ROOT = "/usr/lib64"
	41 LCMS_ROOT = "/usr/lib64"

(Der Vollständigkeitshalber wieder ins virtualevn-root wechseln `cd ../..`)

Nun kann PIL installiert werden:

	../../bin/python setup.py install

Jetzt sind alle Pys, welche Mediagoblin nicht automatisch mitinstalliert (wieso auch immer) auf dem System. Nun kann der ganze Rest automatisch gezogen werden:

	./bin/python setup.py develop

Dies sollte ohne Fehler ablaufen. Ansonsten müsst ihr evt. noch weiter Pys installieren.

mediagoblin.ini muss nun noch angepasst werden. Die Verwendung von Postgres ist bereits vorbereitet - es muss jedoch korrekt auf den Unix-Socket zugegriffen werden:

	sql_engine = postgresql://<uberspace-username>:<passwort>@localhost/mediagoblin?host=/home/<uberspace-name>/tmp

(Kurze Erklärung: Mediagoblin versucht standardmässig auf einen Unix-Socket unter /tmp zuzugreiffen. Bei den Ubernauten liegt der Socket jedoch [defaultmässig] unter ~/tmp/ [/home/<uberspace-name>/tmp]. Dies wird mit dem `?host=/home/<uberspace-name>/tmp`-String am Ende angegeben. Den Namen und das Passwort kriegt ihr aus der Datei `~/.pgpass` und müsste sehr wahrscheinlich überhaupt nicht mit angegeben werden [dafür gibt es die .pgpass Datei überhaupt].)

Nun kann die Datenbank initialisiert werden:

	./bin/gmg dbupdate

Mediagoblin kann nun über den von den Ubernauten für euch freigegeben Port erreichbar gemacht werden. Zuerst muss der Port jedoch noch in der Datei `paste.ini` editiert werden:

	[server:broadcast]
	use = egg:Paste#http
	host = 0.0.0.0
	port = <insert-your-port-here>

Mediagoblin deployen:

	./lazyserver.sh --server-name=broadcast

Ihr könnt nun euer Mediagoblin unter http://<dein-uberspace>:<dein-port> ansteuern und verwenden.


## FastCGI deployment

Soweit so gut, wir wollen aber via Port 80 und/oder Port 443 auf Mediagoblin zugreiffen. Also muss ein FastCGI deployment her.

Erstellt under `mediagoblin` die Datei `mg.fcgi` (Achtung: Die Pfäde zu Python und paste.ini korrigieren!):

	#!</path/to/mediagoblin/bin/python>

	# Written in 2011 by Christopher Allan Webber
	#
	# To the extent possible under law, the author(s) have dedicated all
	# copyright and related and neighboring rights to this software to the
	# public domain worldwide. This software is distributed without any
	# warranty.
	#
	# You should have received a copy of the CC0 Public Domain Dedication along
	# with this software. If not, see
	# <http://creativecommons.org/publicdomain/zero/1.0/>.

	from paste.deploy import loadapp
	from flup.server.fcgi import WSGIServer

	CONFIG_PATH = \'</path/to/mediagoblin/paste.ini>\'

	import os
	os.environ[\'CELERY_ALWAYS_EAGER\'] = \'true\'

	def launch_fcgi():
	    ccengine_wsgi_app = loadapp(\'config:\' + CONFIG_PATH)
	    WSGIServer(ccengine_wsgi_app).run()


	if __name__ == \'__main__\':
	    launch_fcgi()

Das Script nun ausführbar machen:

	chmod +x mediagoblin/mg.fcgi


Und eine `.htaccess`-Datei erstellen:

	RewriteEngine On
	RewriteBase /
	RewriteCond %{REQUEST_FILENAME} !-f
	RewriteRule ^(.*)$ $1 [QSA,L]

	Options +ExecCGI
	AddHandler fcgid-script .fcgi


Das FastCGI-Depoyment ist nun bereits fertig!

## Service erstellen

Wie üblich bei den Ubernauten wird nun noch ein Service erstellt.

Die Postgresinstallation hat `~/service` bereits erstellt - dies ist also bereits gemacht.

Bei mir sieht dann `~/etc/run-mediagoblin/run` folgendermassen aus:

	#!/bin/bash
	cd /var/www/virtual/keks/mediagoblin.aurka.com/
	source bin/activate
	./lazyserver.sh --server-name=fcgi fcgi_host=127.0.0.1 fcgi_port=<Uberspace-Port-von-mir>


Nun muss einzig noch nach `~/service` gelinkt werden:

	ln -s ~/etc/run-mediagoblin/ ~/service/mediagoblin

Mediagoblin läuft nun als Service. Viel Spaß beim verwenden!

Wenn ihr zuerst ein Mediagoblin anschauen wollt. Hier ist mein [Mediagoblin](http://mediagoblin.aurka.com "mediagoblin.aurka.com"). Ich habe vor einiger Zeit auch einen [Bericht](http://blog.aurka.com/mediagoblin-in-use-ein-bericht.html) darüber geschrieben, wie ich zu Mediagoblin nach einem Jahr in Verwendung stehe.

Korrekturen, Bugfixes, etc. bitte an mich herantragen, damit ich die Doku verbessern/korrigieren kann.

# Useful links

[Linux Magazin mit einer Mediagoblin Installations-Anleitung](http://www.linux-magazine.com/Online/Features/MediaGoblin "Linux Magazin")

[Offizielles Mediagoblin Wiki](http://mediagoblin.readthedocs.org/en/v0.5.1/siteadmin/deploying.html "Mediagoblin Wiki")

# Dankeschön

* Christopher von der Ubernauten fürs weiterhelfen beim FastCGI deployment!

* Gizu für einige Anpassungen, welche ich nun endlich eingepflegt habe
