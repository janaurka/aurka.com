Title: Erstellen virtueller Maschinen mit KVM unter Ubuntu 14.04 
Date: 2014-05-16
Tags: ubuntu, trusty, linux, kvm, libvirt, virt-install, qemu, debian, virt-install, tech, tahr, howto 
Category: tech 
Author: janssen

Infolge vom Wechsel von VMWare ESXi 5.x zu KVM wird es an dieser Stelle einige Artikel zum Thema KVM (Kernel based Virtual Machine) geben. Diese Artikel sind auf Ubuntu 14.04 Trusty Tahr abgestimmt - nicht weil ich Ubuntu extrem mag, aber weil Ubuntu 14.04 für dieses Projekt eingesetzt wird.

### Bemerkung zu Ubuntu 14.04
Ubuntu 14.04 ist vor gut einem Monat erschienen (also dieser Artikel geschrieben wurde). Auch wenn es als LTS Version gekennzeichnet ist, sind Ubuntu Releases zu Beginn leider oft ziemlich buggy. Ubuntu 12.04 war hier leider ein ziemlich gutes Beispiel. Dieses war erst in etwa ab 12.04.1 wirklich produktiv einsetzbar. Also vorsicht bezüglich produktiv einsetzen und meldet Bugs!


# Umgebung
Sämtliche Informationen gelten für folgende Testumgebung:

* Ubuntu 14.04 64bit Server
* Single Host
* Disk format: qcow2
* VMs basieren ebenfalls auf Ubuntu 14.04 64bit Server

# Requirements
Um KVM einzusetzen, wie später beschrieben, werden folgende Pakete benötigt:

* libvirt0
* libvirt-bin
* virtinst
* (virt-viewer -> kann auch auf einem externen Host sein)
* virt-goodies
* qemu-kvm

Diese können wie gewohnt bequem via `apt` installiert werden:

	apt-get install libvirt0 libvirt-bin virtinst virt-goodies qemu-kvm

__Info:__ Natürlich muss die Netzwerkkonfiguration angepasst werden. Hierfür gibt es diverse Varianten. Seit Kernel 3.3 ist grundsätzlich der Open vSwitch für das Networking zuständig. Bis dahin wurde oftmals mit normalen Linux Bridges gearbeitet. Hierzu wird noch ein Artikel folgen.

Weiter wird natürlich ein Verzeichnis benötigt, in welchem die Image-Dateien der VMs liegen sollen. Ich habe mich hierbei für `/var/vm/` entschieden. Unter diesem Verzeichnis wird dann pro VM ein neuer Ordner mit dem jeweiligen VM-Namen erstellt. Zum Beispiel: `/var/vm/example1`


# Erstellen der VM
Beschrieben wird die Installation einen Linux/UNIX-VM. Wie eine Windows-VM erstellt wird, wird unter [Erstellen virtueller Windows-VMs mit KVM unter Ubuntu 14.04](http://aurka.com/erstellen-virtueller-windows-vms-mit-kvm-unter-ubuntu-1404.html) beschrieben.

## Imagedatei erstellen
Als erstes muss für die VM ein Image erstellt werden. Dies übernimmt das Tool `qemu-img`. Hier der Befehl:

	qemu-img create -f qcow2 /var/vm/example1/example.qcow2 1.5T

Dieser Befehl erstellt ein Image File im qcow2 Format, welches 1.5TB groß ist. Effektiv ist das File nur wenige KB groß; es wächst dann mit dem Image dynamisch.

## ISO herunterladen
Das ISO für die Installation von Ubuntu wird benötigt und kann von einem x-beliebigen Mirror heruntergeladen werden. Beispielsweise mit:

	wget http://mirror.switch.ch/ftp/ubuntu-cdimage/14.04/ubuntu-14.04-server-amd64.iso

__Wichtig:__ Überprüft nach dem Download die Checksummen des ISOs. Die korrekten Checksums sind [hier](http://mirror.switch.ch/ftp/ubuntu-cdimage/14.04/SHA256SUMS) zu finden. Unter Debian/Ubuntu kann die Checksumme des heruntergeladenen ISOs so erstellt werden:

	sha256sum <ISO-File>

## VM generieren
Mit der Hilfe von `virt-install` kann nun sehr schmerzfrei eine VM erstellt werden:

	virt-install --connect qemu:///system --name example1 --ram=24109 --vcpus=4 \
	--disk path=/var/vm/example1/example1.qcow2,size=2500,format=qcow2 \
	--cdrom=/var/vm/ISO/ubuntu-14.04-server-amd64.iso --vnc \ 
	--os-variant=ubuntutrusty --network=bridge:br0,model=virtio

Dieser Befehl erstellt die VM mit:

* Name: example1
* auf dem Host: localhost (zu sehen am qemu:///system)
* mit 24GB RAM
* 4 vCPUs
* auf das mit `qemu-img create` erstellte Image. Die Größe wird in GB angegeben und muss deklariert werden, auch wenn die Größe bereits beim erstellen des Images angegeben wurde. Weiter muss auch das Format mit qcow2 angegeben werden. Werden die Parameter nicht angegeben, sieht die VM nur wenig KB Speicherplatz und ist im RAW Format, welches keine Snapshots zulässt!
* das ISO soll als CD emuliert werden
* VNC soll laufen
* dass es sich um ein Ubuntu 14.04 Trusty Tahr handelt
* mit einem Bridged Network über br0, mit dem virtio Treiber (dieser ist Paravirtuell und dadurch sehr performant).

Nun ist die VM bereits erstellt und läuft auch.  

## Kontrolle
Die Erstellung der VM kann nun kontrolliert werden. Der Befehl `virsh list` zeigt die soeben erstellte VM an. Die VM kann mit `virsh` jeweils über die ID oder den Namen angesprochen werden.

	 Id    Name                           State
	----------------------------------------------------
	 1     example1                       running

Die Konfigurationsdateien (wie gewohnt im XML Format) sind unter diesem Pfad zu finden:

	/etc/libvirt/qemu/

Dort existiert nun eine example1.xml Datei. Kurze Kontrolle, ob bei der VM angekommen ist, dass es qcow2 als Imageformat verwenden soll:

	<disk type='file' device='disk'>
		<driver name='qemu' type='qcow2'/>
		<source file='/var/vm/example1/example1.qcow2'/>
		<target dev='vda' bus='virtio'/>
		<address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
	</disk>

Solange `<driver name='qemu' type='qcow2' />` in der XML-Datei steht, ist soweit einmal alles gut.


## Installation VM
Nun muss die VM noch installiert werden. Hierfür kann mit dem Werkzeug `virt-viewer` via VNC auf die VM zugegriffen werden. Hierfür wird X benötigt, deshalb greife ich von einem Client vie `virt-viewer` auf die VM zu. Dies funktioniert folgendermassen:

	virt-viewer -c qemu+ssh://<user>@<kvm-host>/system example1 

Für einen lokalen Zugriff muss nicht auf SSH zurückgegriffen werden:

	virt-viewer -c qemu+ssh://system/system example1

Nun kann Ubuntu 14.04 wie gewohnt über den Installer installiert werden.

# Weitere Artikel zum Thema KVM unter Ubuntu 14.04

* [Erstellen virtueller Windows-VMs mit KVM unter Ubuntu 14.04](http://aurka.com/erstellen-virtueller-windows-vms-mit-kvm-unter-ubuntu-1404.html)
* [Backups mit (externen) Snapshots mittels KVM unter Ubuntu 14.04](http://aurka.com/backups-mit-externen-snapshots-mittels-kvm-unter-ubuntu-1404.html)
* [Open vSwitch mit KVM unter Ubuntu 14.04](http://aurka.com/open-vswitch-mit-kvm-unter-ubuntu-1404.html)

Anmerkungen und Korrekturen bitte via [Kontakt](http://aurka.com/pages/about.html)
