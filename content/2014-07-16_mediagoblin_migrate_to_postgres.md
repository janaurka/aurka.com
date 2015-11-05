Title: Mediagoblin von SQLite zu Postres migrieren
Date: 2014-07-16
Tags: mediagoblin, gnu, goblin, media, hosting, share, photo, film, media, migrate, sqlite, postgres, psql
Category: tech
Picture: mediagoblinuse_header.jpg
Author: janssen

Mediagoblin (mehr Infos darüber auf der [offiziellen Homepage](http://mediagoblin.org/) und in [diversen Blogeinträgen auf diesem Blog](https://blog.aurka.com/tag/mediagoblin.html)) bietet leider aktuell keine einfache Migration der Datenbank von SQLite zu Postgres. Eine Migration ist jedoch mit relativ wenigen Schritten möglich. Hier eine kurze Anleitung:

__Solltet ihr Mediagoblin wie im Artikel [Mediagoblin auf einem Uberspace](https://blog.aurka.com/mediagoblin-auf-uberspace.html) beschrieben Mediagoblin innerhalb eines Uberspaces betreiben, dann müsst ihr Postgres zuerst wie im Artikel aufgezeigt initialisieren/installieren__

Nach der Bereitstellung von Postgres muss nun die Postgres Datenbank erstellt werden. Voraussetzung hierfür ist eine laufende und funktionierende Postgres Instanz.

Zu Beginn wird die Datenbank, welche Mediagoblin verwenden soll erstellt:

	postgres createdb -E UNICODE -O mediagoblin mediagoblin

Mediagoblin wird nun beendet (egal wie) und in der `mediagoblin.ini` respektive `mediagoblin_local.ini` (ist normalerweise nur ein symlink) die Datenbank verändert werden. Dort wird folgende Zeile benötigt:

	sql_engine = postgresql://<psql-user>:<socket-pw>@localhost/<dbname>?host=<pfad-zu-socket-falls-nicht-/tmp>

__Erläuterung:__ Das `?host=/home/keks/tmp` zeigt auf den Socket von Postgres. Ohne diesen Parameter sucht Posgres diesen im /tmp-Verzeichnis. Anschliessend werden einfach sämtliche Tabellen, welche das `sqlite` Script von eben zurückgegeben hat.

Jetzt mit dem `gmg` Befehl die Datenbank initialisieren:

	.bin/gmg dbupdate

Mediagoblin erstellt hiermit die benötigte Datenbankstruktur.

Nun in das Verzeichnis wechseln, wo die SQLite Datenbank liegt und folgenden Befehl absetzen:

	sqlite3 mediagoblin.db .dump | \
	grep '^CREATE TABLE' | \
	cut -d' ' -f3 | \
	sed 's,",,g' | \
	tr '\n' ' '

Dieser gibt sämtliche Tabellen der Datenbank zurück. Bei mir sieht dies folgendermassen au
	
	core__migrations core__file_keynames core__clients core__nonce_timestamps core__tags core__request_tokens core__notifications core__collections core__collection_items core__comment_subscriptions core__access_tokens core__media_comments core__mediafiles core__processing_metadata core__attachment_files core__processing_notifications core__media_tags core__comment_notifications image__mediadata core__reports core__reports_on_comments core__reports_on_media core__user_bans core__privileges core__privileges_users core__users core__media_entries

Nun wird [dieses Script](http://www.tylerlesmann.com/2009/apr/27/copying-databases-across-platforms-sqlalchemy/) verwendet, um die Daten von SQLite nach Postgres zu kopieren. Dafür das Script folgendermassen ausführen:

	<path-to-(virtualenv)-python> pull.py -f sqlite:///mediagoblin.db -t postgresql://<psql-user>:<socket-pw>@localhost/<dbname>?host=<pfad-zu-socket-falls-nicht-/tmp> core__migrations core__file_keynames core__clients core__nonce_timestamps core__tags core__request_tokens core__notifications core__collections core__collection_items core__comment_subscriptions core__access_tokens core__media_comments core__mediafiles core__processing_metadata core__attachment_files core__processing_notifications core__media_tags core__comment_notifications image__mediadata core__reports core__reports_on_comments core__reports_on_media core__user_bans core__privileges core__privileges_users core__users core__media_entries

Das Script meldet bei den ersten paar Durchführungen (bei mir waren es zwei an der Zahl) Fehler zurück, welche auf eine spezifische Tabelle zeigen. Um das Problem zu lösen einfach das Script noch einmal auslösen aber nur mit der 'Problemtabelle' an der Stelle von sämtlichen Tabellen. Anschliessend wieder das Script mit allen Tabellen als Attribute starten, bis kein Fehler mehr auftritt.

Mediagoblin kann nun wieder gestartet werden und sollte sämtliche Einträge aus der SQLite Datenbank übernommen haben. Nun gibt es jedoch noch ein Problem: Die Uploads funktionieren nicht. Grund: Psostgres kennt die ID-Schlüssel nicht und erstellt dann Duplikate, welche nicht zulässig sind => Datenbankfehler [Hier genauer bechrieben](https://wiki.postgresql.org/wiki/Fixing_Sequences). 

Um dieses Problem zu lösen kann einfach das von Postgres zur verfügung gestellte Script [Updating sequence values from table](https://wiki.postgresql.org/wiki/Fixing_Sequences) verwendet werden. Also:

	psql -Atq -f reset.sql -o temp
	psql -f temp
	rm temp

Sollte dieses Script diesen Fehler ausspucken:

	psql:temp:9: ERROR:  function max(integer, integer) does not exist 
	LINE 1: ...VAL('public.core__notifications_id_seq',
	COALESCE(MAX(id, 1)... 
	         ^ 
	HINT:  No function matches the given name
	and argument types. You might need to add explicit type casts.

Dann kann auf folgendes Script zurückgegriffen werden:

	SELECT  'SELECT SETVAL(' ||quote_literal(quote_ident(S.relname))|| ', MAX(' ||quote_ident(C.attname)|| ') ) FROM ' ||quote_ident(T.relname)|| ';'
	FROM pg_class AS S, pg_depend AS D, pg_class AS T, pg_attribute AS C
	WHERE S.relkind = 'S'
	    AND S.oid = D.objid
	    AND D.refobjid = T.oid
	    AND D.refobjid = C.attrelid
	    AND D.refobjsubid = C.attnum
	ORDER BY S.relname;

(Quelle: [PostgreSQL – Updating Tables Sequence](http://akangirul.wordpress.com/2013/06/29/postgresql-updating-tables-sequence/)

Das Vorgehen ist gleich wie beim Script vom Postgres-Wiki.

Nun ist auch die ID bei Postgres korrekt und Mediagoblin wurde erfolgreich von SQLite nach Postgres migriert.

Anmerkungen und Korrekturen bitte via [Kontakt](https://blog.aurka.com/pages/about.html)


Quellen:

* [Mediagoblin Mailingliste](http://lists.mediagoblin.org/pipermail/devel/2014-June/000886.html), danke an Kushal Kumaran.
* [Postgres Wiki](https://wiki.postgresql.org/wiki/Fixing_Sequences)
* [Updating Table Sequences, akangirul.wordrpess.com](http://akangirul.wordpress.com/2013/06/29/postgresql-updating-tables-sequence/)
