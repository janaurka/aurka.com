Title: Backups mit (externen) Snapshots mittels KVM unter Ubuntu 14.04
Date: 2014-05-17
Tags: ubuntu, trusty, linux, kvm, libvirt, snapshot, qemu, debian, external, tech, tahr, howto
Category: tech
Author: janssen

Dies ist der zweite Post zum Thema Ubuntu 14.04 und KVM. Dieser behandelt das Thema 'Snapshots', wobei ich hauptsächlich auf sogenannt 'external' Snapshots eingehen werde. Der erste Artikel bezüglich der Erestellung von VMs gibt es hier: [Erstellen virtueller Maschinen mit KVM unter Ubuntu 14.04](http://blog.aurka.com/erstellen-virtueller-maschinen-mit-kvm-unter-ubuntu-1404.html).

# Umgebung
Sämtliche Informationen gelten für folgende Testumgebung:

* Ubuntu 14.04 64bit Server
* Single Host
* Disk format: qcow2
* VMs basieren ebenfalls auf Ubuntu 14.04 64bit Server
* Um die Snapshots sinnvoll zu speichern wird ein externer Speicher benötigt. Am einfachsten ein NAS, welches via NFS auf dem Host gemountet wird.

# Requirements
Um KVM einzusetzen, wie später beschrieben, werden folgende Pakete benötigt:

* libvirt0
* libvirt-bin
* virtinst
* (virt-viewer -> kann auch auf einem externen Host sein)
* virt-goodies
* qemu-kvm
* rsync oder andere Tools, um Daten zu kopieren/sichern. Mein Favorit hierbei ist [Backupninja](https://labs.riseup.net/code/projects/backupninja); eine Sammlung rund um rsync und Konsorten, welche den Backupvorgang sehr bequem gestalten.

Um Snapshots zu erstellen wird natürlich mindestens eine VM benötigt. Ich beschreibe hier das Snapshoten von der im Post bezüglich dem Erstellen einer VM `example1`. Der Vorgang funktioniert nur, wenn das Image von `example1` im Format qcow2 vorliegt.

# Snapshots unter KVM - Eine kurze Einführung
KVM und seine Werkzeuge können von bestimmten Image Formaten Snapshots erstellen. Oft verwendet werden LVMs (die können auch ohne KVM snapshotten) und qcow2. Letzters wird in diesem HowTo behandelt.
Grundsätzlich gibt es zwei sich unterscheidende Arten von Snapshots. Es gibt:

* __interne Snapshots__: Interne Snapshots werden innerhalb eines qcow2 Images erstellt. Von ausserhalb ist nicht sofort ersichtlich, ob und wenn ja, wie viele Snapshots das Imagefile besitzt. Sämtliche Änderungen bleiben also in einem File kompakt zusammen. Dies hat den Vorteil, dass man sich nur um eine Datei kümmern muss. Dies lohnt sich jedoch offensichtlich nur, um Tests zu fahren, welche im Notfall rückgängig gemacht werden können. Die Image-Datei kann ziemlich überfallartig anwachsen. Besonders, wenn der aktuelle Stand der VM mitgesichert werden soll, da der Inhalt des RAMs ebenfalls im Image landet. Interne Snapshots können mit dem Argument `--live` von einem Live-System erstellt werden.
* __externe Snapshots__: Externe Snapshots eignen sich dafür gut, um ein Bare-Metal Backup einer VM zu erstellen. Diese externen Snapshots funktionieren in etwa so, wie von ESXi bekannt. Ein Snapshot erstellt eine neue Image-Datei, welch Änderungen speichert. Die 'alte' Image-Datei ist somit konsistent (sofern die VM zum Stand des Snapshots konsistent war) und kann einfach wegkopiert werden.

Obwohl Snapshots auf den ersten Blick ein Segen sind, sollte sehr vorsichtig mit ihnen umgegangen werden. Man sollte immer darauf bedacht sein, möglichst wenige (am besten gar keine) Snapshots auf einem System zu haben, weil diese das System verlangsamen und sehr gerne Quota/FS/HD Grenzen sprengen, weil es sich um eine neue, teilweise extrem schnell wachsende Datei handelt. Wer also Snapshots für Backups verwendet, sollte darauf bedacht sein, die Snapshots so bald wie möglich wieder los zu werden.

Gedanken sollte man sich auch zum Thema 'wann erstelle ich den Snapshot' machen. `virsh` erstellt ohne Probleme Snapshots von laufenden Systemen. Bei externen Snapshots wird die `--live` Option jedoch (noch) nicht unterstützt. Deshalb ist es wohl sinnvoll, wenn nicht äusserst empfehlenswert, die Snapshots von einem heruntergefahrenem System zu machen. Da Uptime bei mir nicht kritisch ist, kann ich ohne Problem mit ein paar Sekunden/Minuten Downtime auskommen. Wenn ein Snapshot einer laufenden VM erstellt wird, wechselt die VM in den Stataus 'paused'. Der Snapshot ist also grundsätzlich konsistent. Die Frage ist mehr, ob die Daten genau zu dem Zeitpunkt es auch waren. Es ist beispielsweise gut möglich, dass die Datenbank gerade Transaktionen am laufen hat (oder ähnliches) und dies dann zu Problemen führt. Grundsätzlich gilt: Wenn man es sich leisten kann Offline-Snapshots zu erstellen, dann ist man sicherlich auf der sicheren Seite.


Weiter wird mit dem Backup von einem konsistenten Snapshot des Systems ein Bare Metal Backup erstellt. Daten können nicht sofort aus dem Snapshot extrahiert werden. Ein zusätzliches Datenbackup, zumindest von `/home/`, `/etc`, und `/var`, ist wärmstens zu empfehlen. Hier sei noch einmal auf das Tool [Backupninja](https://labs.riseup.net/code/projects/backupninja) verwiesen. Ein Szenario, welches sämtliche Daten konsistent sammelt (DB Dumps, etc) und dann via `rsync over ssh` auf das Backup schreibt (um nur ein Mount zu benötigen kann dies auf dem Host oder auf einer dedizierten VM gemountet sein, oder direkt via `rsync over ssh` auf das Backupsystem). Fertig ist ein äusserst effektives, schnelles und leicht zu debuggendes Datenbackup ;-)

# Externe Snapshots erstellen
Dieses HowTo beschreib die Erstellung von Snapshots mit dem Tool `virsh`, weil ich sehr gerne mit wenigen Tools auskomme und beinahe das alles bezüglich QEMU/Libvirt mittels `virsh` gemacht werden kann.

Der Befehl um Snapshots zu erstellen lautet `snapshot-create-as`. Aufgerufen:

	virsh snapshot-create-as <vm-name> <snapshot-name> "<snapshot-description>" --diskspec vda,file=<path-to-new-snapshot-file.qcow2> --disk-only --atomic
oder als Beispiel mit example1:

	virsh snapshot-create-as example1 snapshot1_example1 "first snapshot of example1" --diskspec vda,file=/var/vm/example1/snapshot1_example1.qcow2 --disk-only --atomic

Die Parameter bedeuten:

* snapshot-create-as: Erstellt einen Snapshot von Disk und RAM.
* diskspec: Gibt die Diskattribute an.
* disk-only: Gibt an, dass nur die Disk und nicht auch noch der VM-Stand gesnapshotted werden soll
* atomic: Führt den Snapshot nur aus, wenn dieser konsistent erstellt werden kann. Ansontest failt der Snapshot.

Interne Snapshots werden beinahe gleich erstellt. Das Argument `disk-only` bestimmt jedoch, dass es sich um einen externen Snapshot handelt.

Nach dem Erstellen wird der Vorgang kontrolliert:

	virsh snapshot-list neptun-test4

Liefert die Snapshot Daten:

	 Name                 Creation Time             State
	------------------------------------------------------------
	 snapshot1_example1  2014-05-17 03:35:41 +0200 disk-snapshot

Der Snapshot wurde also erstellt. Auf der Filesystem-Ebene wurde die Snapshot-Datei ebenfalls erstellt:

	-rw------- 1 libvirt-qemu kvm  232K May 17 03:35 snapshot1_example1.qcow2

Änderungen werden ab der Erstellung kosequent in diese Datei geschrieben. Die alte Image-Datei kann nun ohne Bedenken bezüglich Konsistenz, etc. wegkopiert werden. Beispielsweise mit:

	rsync -avv /var/vm/example1/example1.qcow2 /media/backup/vms/example1/$(date +"%y-%m-%d")-example1.qcow2

Nun ist es an der Zeit den Snapshot wieder los zu werden. Hier ist KVM/QEMU/libvirt jedoch noch nicht soweit, wie man sich dies wünschen könnte.
Der einfachste Versuch den Snapshot zu löschen (einen Snapshot löschen bedeutet, dass sämtliche Änderungen aus dem Snapshot in die Image-Datei einfliessen. Um zum Stand des Snapshots zu springen ist der Befehl `virsh backup-revert <vm-name> <snapshotname> zu verwenden) failt:

	virsh snapshot-delete example1 snapshot1_example1

Ausgabe:

	error: Failed to delete snapshot snapshot1_example1
	error: unsupported configuration: deletion of 1 external disk snapshots not supported yet

Wenn der Snapshot schon nicht gelöscht werden kann, dann muss der Inhalt des alten Images halt in den Snapshot eingepflegt werden. Dies geschieht folgendermassen:

	virsh blockpull --domain example1 --path /var/vm/example1/snapshot1_example1.qcow2 --verbose --wait

__Achtung__: Dies funktioniert nur, wenn nur ein Snapshot existiert.

Dieser Vorgang dauert dann seine Zeit, da das alte Image in den Snapshot eingepflegt werden muss. Liefert dann aber bei Erfolg zurück:
	Block Pull: [100 %]
	Pull complete

Nun enthält der Snapshot sämtliche Informationen, um die VM zu betreiben. Das Snapshot-Image ist dementsprechend auch gewachsen:

	-rw------- 1 libvirt-qemu kvm  3.1G May 17 03:48 snapshot1_example1.qcow2

Nun kann die alte Image Datei gelöscht werden.

Vom System wurde auf diese Art und Weise ein sauberes Bare Metal Backup erstellt, welches im Notfall schnell zum Einsatz gebracht werden kann.


# Weitere Artikel zum Thema KVM unter Ubuntu 14.04
* [Erstellen virtueller Maschinen mit KVM unter Ubuntu 14.04](http://blog.aurka.com/erstellen-virtueller-maschinen-mit-kvm-unter-ubuntu-1404.html)
* [Erstellen virtueller Windows-VMs mit KVM unter Ubuntu 14.04](http://blog.aurka.com/erstellen-virtueller-windows-vms-mit-kvm-unter-ubuntu-1404.html)
* [Open vSwitch mit KVM unter Ubuntu 14.04](http://blog.aurka.com/open-vswitch-mit-kvm-unter-ubuntu-1404.html)
* [Konvertierung von ESXi-VMs zu KVM unter Ubuntu 14.04](konvertierung-von-esxi-vms-zu-kvm-unter-ubuntu-1404.html)

Anmerkungen und Korrekturen bitte via [Kontakt](http://blog.aurka.com/pages/about.html)
