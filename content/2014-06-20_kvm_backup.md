Title: Einfaches Backups von QCOW2 basierten KVM Maschinen
Date: 2014-05-17
Tags: ubuntu, trusty, linux, kvm, libvirt, snapshot, qemu, debian, backup, qcow2, vm, howto
Category: tech
Author: janssen

Dieser Blogeintrag erweitert grundsätzlich den Blogeintrag [Backups mit (externen) Snapshots mittels KVM unter Ubuntu 14.04](http://aurka.com/backups-mit-externen-snapshots-mittels-kvm-unter-ubuntu-1404.html) um ein in der Praxis einfach zu verwendendes Script, um KVM Maschinen bequem zu sichern.

# Umgebung
Sämtliche Informationen gelten für folgende Testumgebung:

* Ubuntu 14.04 64bit Server
* Single Host
* Disk format: qcow2
* Um die Snapshots sinnvoll zu speichern wird ein externer Speicher benötigt. Am einfachsten ein NAS, welches via NFS o.Ä. auf dem Host gemountet wird.

Das Script wurde schlussendlich nur mit Ubuntu 14.04 getestet, sollte jedoch auf sämtlichen KVM/libvirt betriebenen Systemen laufen.


# Backup erstellen
Das Script [bkvm](http://soliton74.blogspot.ch/2013/08/about-kvm-qcow2-live-backup.html) von Luca Lazzeroni, habe ich ein wenig erweitert, damit dieses nun das Sichern von KVM-Maschinen unterstützt, welche sich nicht im Status 'running' befinden. Normalerweise verwendet das Script die `virsh` Funktion `blockcopy`. Weil sich dieser jedoch weigerte, ein offline Image zu kopieren, übernimmt dies nun halt das gute alte `rsync`.

Das Backup wird durch den Aufruf des Scripts gestartet:

	/bin/bash bkvm.sh <VMName>

Es erstellt am angegeben Speicherort folgende Ordnerhierarchie:

	Backupdir
	├── example
	│   ├── backup-0
	│   │   ├── example-memory
	│   │   ├── example.qcow2-backup.qcow2
	│   │   └── example.xml
	│   ├── backup-1
	│   │   ├── example-memory
	│   │   ├── example.qcow2-backup.qcow2
	│   │   └── example.xml

Sofern eine Mailadresse angegeben ist, wird eine Mailbenachrichtigung versendet; inklusive Information im `Subject`, ob das Backup funktioniert hat.

Meine `bkvm_extended`-Version gibt es auf [meinem Github-Account](https://gist.github.com/janaurka/326fbf6fcf8671ea395d). Verbesserungen, etc. werden selbstverständlich gerne angenommen.

Wie auch Luca in seinem Blog betont, gilt natürlich, dass ich in keinster Weise garantiere, dass dieses Script einwandfrei funktioniert.

# Alle Maschinen sichern
Damit das Script nicht einzeln angestossen werden muss, hier noch ein kleines Zusatzscript, welches für [Backupninja](https://labs.riseup.net/code/projects/backupninja/) konzipiert wurde, jedoch ohne weiteres auch als standalone verwendet werden kann (eine Shebang wäre dann natürlich keine schlechte Idee). Das Script sichert sämtliche definierten Maschinen (`virsh list --all`), welche nicht in der `Exclude`-Liste auftauchen:

	# Backupninja SH-Handler to snapshot kvm machines

	#Initials
	BKVM=`/usr/local/scripts/bkvm.sh`

	# List with all kvm machines which are defined on this host
	VMLIST=`virsh list | awk '{print $2}' | sed '/^$/d' | grep -v Name`

	# Array with kvm machines to exclude from backup
	EXCLUDE=(neptun-test4 ubuntutest1 ubuntutest2 ubuntutest3)

	echo "Start Backup KVM Machines"
	# Functions

	function arraycontains() {
	    local vm=$1
	    local in=1
	    for element in $EXCLUDE; do
	        if [[ $element == $vm ]]; then
	            in=0
	            break
	        fi
	    done
	    return $in
	}

	# Run the script
	# Run default bkvm.sh for all vms
	for vm in $VMLIST
	do
		echo $vm
		arraycontains $vm
		if [ $? -eq 1 ];
		then
			echo "$vm is getting backuped"
			/bin/bash /usr/local/scripts/bkvm.sh $vm
		else
			echo "$vm is on the exclude list"
		fi
	done

# Restore
Dies wurde von mir noch nicht getestet, jedoch sollte laut Luca folgender Befehl funktionieren:

	virsh restore <file>

Also die VM definieren, schauen dass das Backup-Image am korrekten Ort liegt und dann als File das RAM-Abbild angeben. Mit der Option `--running` müsste KVM die Maschine dann gleich als running betiteln.

# Weitere Artikel zum Thema KVM unter Ubuntu 14.04
* [Erstellen virtueller Maschinen mit KVM unter Ubuntu 14.04](http://aurka.com/erstellen-virtueller-maschinen-mit-kvm-unter-ubuntu-1404.html)
* [Erstellen virtueller Windows-VMs mit KVM unter Ubuntu 14.04](http://aurka.com/erstellen-virtueller-windows-vms-mit-kvm-unter-ubuntu-1404.html)
* [Open vSwitch mit KVM unter Ubuntu 14.04](http://aurka.com/open-vswitch-mit-kvm-unter-ubuntu-1404.html)
* [Konvertierung von ESXi-VMs zu KVM unter Ubuntu 14.04](konvertierung-von-esxi-vms-zu-kvm-unter-ubuntu-1404.html)
* [Backups mit (externen) Snapshots mittels KVM unter Ubuntu 14.04](http://aurka.com/backups-mit-externen-snapshots-mittels-kvm-unter-ubuntu-1404.html)

Anmerkungen und Korrekturen bitte via [Kontakt](http://aurka.com/pages/about.html)
