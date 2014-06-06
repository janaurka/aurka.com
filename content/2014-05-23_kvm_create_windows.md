Title: Erstellen virtueller Windows-VMs mit KVM unter Ubuntu 14.04
Date: 2014-05-23
Tags: ubuntu, trusty, linux, kvm, libvirt, qemu, debian, virt-install, tech, howto, windows, win7
Category: tech
Author: janssen

Dieser Blogpost erläutert kurz das Vorgehen bei der Erstellung von virtuellen Windows-VMs mit KVM unter 14.04. Dies unterscheidet sich an gewissen Orten von dem Vorgang von Linux/UNIX VMs. Der Artikel basiert auf [Erstellen virtueller Maschinen mit KVM unter Ubuntu 14.04](http://aurka.com/erstellen-virtueller-maschinen-mit-kvm-unter-ubuntu-1404.html).

# Requirements
Speziell für Windows-VMs wird folgendes zusätzlich benötigt:

* Windows <Version> ISO (und eine gültige Lizenz)
* Virtio-Treiber für Windows ([gibt es bei Fedora](https://alt.fedoraproject.org/pub/alt/virtio-win/latest/images/))

# Erstellen der VM
Die Vorbereitungen für das Erstellen von Windows-VMs sind genau die gleichen, wie wenn mit Linux/UNIX Gästen gearbeitet wird. Ein QCOW-Image muss erstellt werden und ein Installations-ISO muss zur Verfügung stehen.

## VM generieren
Mit der Hilfe von `virt-install` kann nun sehr schmerzfrei eine VM erstellt werden. Für Windows (beispiel ist auf ein Windows 7 zugeschnitten, müsste aber für alle Windows Versionen (Client und Server) seit Windows 7 / Server 2008 gelten). Als Beispiel wir die VM `win7test` erstellt:

	virt-install --connect qemu:///system --name win7test --ram=4096 --vcpus=2 \
	--disk path=/var/vm/win7test/win7test.qcow2,size=50,format=qcow2 \
	--cdrom=/var/vm/ISO/windows7.iso --vnc --os-type=windows --nonetworks

Nun ist die VM bereits erstellt und läuft auch. Das `--nonetworks` bezieht sich auf den im Artikel [Open vSwitch mit KVM unter Ubuntu 14.04](http://aurka.com/open-vswitch-mit-kvm-unter-ubuntu-1404.html) näher beschriebene Verwendung eines Open vSwitches. Sollten normale Linux-Bridges verwendet werden, kann das Netzwerk natürlich gleich mit `virt-install` zugewiesen werden.

## Installation VM
Speziell hier ist, dass der `virt-install` Befehl weiterläuft. Dieser kann nun in den Hintergrund geschickt werden, oder es muss von einem anderen Terminal aus weitergearbeitet werden.
Nun muss die VM noch installiert werden. Hierfür kann mit dem Werkzeug `virt-viewer` via VNC auf die VM zugegriffen werden. Weil dieses X benötigt, greife ich von einem Client via `virt-viewer` auf die VM zu. Dies funktioniert folgendermassen:

	virt-viewer -c qemu+ssh://<user>@<kvm-host>/system win7test

Für einen lokalen Zugriff muss nicht auf SSH zurückgegriffen werden:

	virt-viewer -c qemu+ssh://system/system win7test

Nun kann Windows wie gewohnt über den Installer installiert werden. Die Aktivierung der Lizenz kann aufgrund der fehlenden Netzwerkverbindung noch nicht vorgenommen werden. Windows lässt sich ohne Probleme ohne Netzwerktreiber installieren. Nach der Installation das Windows sauber herunterfahren. Nun ist der `virt-install` Prozess fertig mit der Erstellung der VM.

Nach der Installation muss der VM mitgeteilt werden, dass Sie an einem Open vSwitch hängt. Dies geschieht mit:

	virsh edit win7test

Dies öffnet den default Editor mit dem win7test-XML File. Direkt vor `</devices>` muss folgendes hinzgefügt werden:

	<interface type='bridge'>
	 <source bridge='<bridgename>'/>
	 <virtualport type='openvswitch' />
	 <model type='virtio'/>
	</interface>

(Das detaillierte Vorgehen ist im Artikel [Open vSwitch mit KVM unter Ubuntu 14.04](http://aurka.com/open-vswitch-mit-kvm-unter-ubuntu-1404.html) beschrieben).

Weiter muss in der Datei angegeben werden, dass die Windows VirtIO-Treiber-CD gemountet werden soll. Dies geschieht folgendermassen:

	 <disk type='file' device='cdrom'>
	   <driver name='qemu' type='raw'/>
	   <source file='/var/vm/ISO/virtio-win-0.1-74.iso'/>
	   <target dev='hdc' bus='ide'/>
	   <readonly/>
	</disk>

(Der Eintrag `<disk>` (...) `</disk>` besteht bereits. Dort eingetragen ist das Windows-ISO. Der Pfad zum Windows-ISO kann einfach durch den Pfad zur Treiber-CD geändert werden.)

Jetzt muss die VM wieder gestartet werden:

	virsh start win7test

Nun als Administrator in Windows anmelden und den Gerätemanager öffnen. Dort wurde der Ethernet-Treiber nicht gefunden.

* Rechts-Klick auf den Ethernet-Adapter ohne Treiben
* nach Treibern suchen
* lokal nach Treibern suchen
* auf die gemountete Treiber CD zeigen und die gewählte Windowsversion (hier Win7) auswählen
* Windows nach Treibern suchen lassen
* Die gefundenen Treiben allesamt installierten.

Nun ist Windows voll funktionsfähig und einsetzbar. Das Windows7 läuft hier mit 4GB RAM und 2 vCPUs auf einem SATA RAID5 äusserst flüssig und schnell.


# Weitere Artikel zum Thema KVM unter Ubuntu 14.04

* [Erstellen virtueller Maschinen mit KVM unter Ubuntu 14.04](http://aurka.com/erstellen-virtueller-maschinen-mit-kvm-unter-ubuntu-1404.html)
* [Backups mit (externen) Snapshots mittels KVM unter Ubuntu 14.04](http://aurka.com/backups-mit-externen-snapshots-mittels-kvm-unter-ubuntu-1404.html)
* [Open vSwitch mit KVM unter Ubuntu 14.04](http://aurka.com/open-vswitch-mit-kvm-unter-ubuntu-1404.html)
* [Konvertierung von ESXi-VMs zu KVM unter Ubuntu 14.04](2014-06-6_kvm_convert_from_esxi.html)

Anmerkungen und Korrekturen bitte via [Kontakt](http://aurka.com/pages/about.html)
