Title: Open vSwitch mit KVM unter Ubuntu 14.04
Date: 2014-05-22
Tags: ubuntu, trusty, linux, kvm, libvirt, qemu, debian, tech, howto, ovs, open, vSwitch, network
Category: tech
Author: janssen

Dies ist der dritte Post zum Thema Ubuntu 14.04 und KVM. Dieser behandelt das Thema 'Networking', wobei ich mit Open vSwitch arbeiten werde. Die ersten beiden Artikel sind [Erstellen virtueller Maschinen mit KVM unter Ubuntu 14.04](http://blog.aurka.com/erstellen-virtueller-maschinen-mit-kvm-unter-ubuntu-1404.html) und [Backups mit (externen) Snapshots mittels KVM unter Ubuntu 14.04](http://blog.aurka.com/backups-mit-externen-snapshots-mittels-kvm-unter-ubuntu-1404.html).

# Umgebung
Sämtliche Informationen gelten für folgende Testumgebung:

* Ubuntu 14.04 64bit Server
* Single Host
* Disk format: qcow2
* VMs basieren ebenfalls auf Ubuntu 14.04 64bit Server
* Ein Server mit multiple NICs

# Requirements
Um KVM einzusetzen, wie später beschrieben, werden folgende Pakete benötigt:

* libvirt0
* libvirt-bin
* virtinst
* (virt-viewer -> kann auch auf einem externen Host sein)
* virt-goodies
* qemu-kvm

Open vSwitch benötigt folgende Pakete:

* openvswitch-switch
* openvswitch-common

Die Installation erfolgt wie gewohnt via `apt`:

	apt-get install openvswitch-switch openvswitch-common


# Networking unter KVM - Eine kurze Einführung
Die bis vor kurzem gängigste Art, KVM Netzwerktechnisch zu betreiben war die Verwendung von normalen Linux-Bridges. Seit Kernel 3.3 ist der [Open vSwitch](http://openvswitch.org/) fix im Kernel und bietet deutlich mehr flexibilität gegenüber den Linux Bridges. Seitdem ist die Verwendung von Open vSwitches für/unter KVM die Regel. Dieses HowTo wird sich demnach auch ausschliesslich um KVM Networking mit Open vSwitch behandeln.

# Open vSwitch erstellen
Als erstes muss ein Open vSwitch erstellt werden. Dies geschieht mit diesem Befehl:

	ovs-vsctl add-br <Bridge-Name>

Beispiele hier mit examplebr0:

	ovs-vsctl add-br examplebr0

Der vSwitch ist nun erstellt, hat jedoch erst einen Port (sozusagen sich selbst) und ist nicht angeschlossen. Nun wird ihm ein Port hinzugefügt, über welchen dann später die Zugriffe erfolgen:

	ovs-vsctl add-port examplebr0 examplebr0p1 -- set interface examplebr0p1 type=internal

(Dieser Schritt könnte soweit ich das sehe grundsätzlich weggelassen werden; grundsätzlich finde ich es jedoch gut, das alles über p1 läuft und nicht über den generischen Namen `examplebr0`.)


Bevor der vSwitch an einem Interface angemacht wird, muss folgendes beachtet werden. Sobald das Interface angehängt ist, kann nicht mehr auf das Interface zugegriffen werden, da dieses vom vSwitch übernommen wird. Eine SSH Session über dieses Interface fault also gleich ab. Deshalb zuerst die Netzwerkkonfiguration vorbereiten und sich einen Zugriff via IMPI oder gleich physich bereithalten.

Der soeben erstellte Port `examplebr0p1` wird nun in `/etc/network/interfaces` konfiguriert:

	auto examplebr0p1
	iface examplebr0p1 inet static
	address <ip; 192.168.1.100>
	gateway <gateway; 192.168.1.1>
	netmask <netmask; 255.255.255.0>

Die physischen Interfaces, welche am vSwitch angeschlossen werden sollen, müssen nun noch so umkonfiguriert werden, dass sie hochkommen (up), wenn der Server startet. Das Beispiel zeigt `eth0`:

	auto eth0
	iface eth0 inet manual
	up ifconfig $IFACE 0.0.0.0 up
	down ifconfig $IFACE down

Nun ist der Moment, an welchem die physischen Interfaces am vSwitch angeschlossen werden. Wie bereits geschrieben: Nach diesem Befehl ist es gut möglich, dass die SSH Verbindung in der Urlaub geht.

	ovs-vsctl add-port examplebr0 eth0

Nun ist das Interface `eth0` am vSwitch angeschlossen. Um die Netzwerkeinstellungen wirksam zumachen, wird der Server am einfachsten neugestartet (`reboot`).

Wenn alles korrekt gemacht wurde, kann nun auf die für `examplebr0p1` konfigurierte IP auf den Server via SSH, etc. zugegriffen werden.

Kontrolliert werden kann das Ganze mit folgendem Befehl:

	ovs-vsctl show

## Open vSwitch mit Bonding (802.3ad)
Der Open vSwitch unterstützt Bonding Techniken wie IEEE 802.3ad. Hierfür kann theoretisch ein Bond-Port dem Switch hinzugefügt werden. Dies geschieht folgendermassen:

	ovs-vsctl add-bond <Switch> <Bondname> <interface> (<interface> ...) lacp=active

Also beispielsweise:

	ovs-vsctl add-bond examplebr0 examplebond0 eth0 eth1 eth2 eth3 lacp=active

`lacp=active` definiert, dass für dieses Bond 802.3ad aktiviert sein soll.

__Wichtig:__ Ich habe diese Konfiguration bis jetzt nicht hingekriegt. Der Switch war von ausserhalb nie ansprechbar. Bis jetzt noch keine Ahnung, wieso dem so ist. Grundsätzlich könnte das Problem umgangen werden, indem auf der Linux Networking-Ebene ein Bond erstellt wird und dieser dann als einzelner Port dem vSwitch hinzugefügt wird.

# Open vSwitch in KVM/libvirt integrieren
Nachdem der vSwitch erstellt wurde, muss nun noch KVM, respektive `libvirt` für den vSwitch konfiguriert werden. Direkt nach dem Aufsetzen von `libvirt` besteht normalerweise ein Netzwerk mit dem Namen `default`. Dieses kann zuerst gelöscht werden:

	virsh net-destroy default

Nun kann das Netzwerk neu konfiguriert werden. Dies geschieht mit folgendem Befehl:

	virsh net-edit default

Dadurch wird der default-Editor mit einer XML-Datei geöffnet. Die Datei muss nach der Veränderung (genau) folgendermassen aussehen:

	<network>
	<name>examplebr0</name>
	<forward mode='bridge'/>
	<bridge name='examplebr0'/>
	<virtualport type='openvswitch'/>
	</network>

Das `default` Netzwerk wurde nun durch das `examplebr0` Netzwerk ersetzt. Um das alte `default` Netzwerk vollständig los zu werden kann folgendes getan werden:

	virsh new-undefine default

Sollte das `default` Netzwerk noch benötigt werden, oder aber es existieren bereits Netzwerkkonfigurationen und man möchte diese einfach ergänzen, dann kann natürlich auch einfach ein neues Netzwerk erstellt werden. Um dies zu tun wird eine XML-Datei an einem beliebigen Ort erstellt. Hier zum Beispiel: `/tmp/examplebr0.xml`. Der Inhalt dieser Datei muss folgendermassen aussehen:

	<network>
	<name>examplebr0</name>
	<forward mode='bridge'/>
	<bridge name='examplebr0'/>
	<virtualport type='openvswitch'/>
	</network>

Diese XML-Datei muss nun noch von `virsh` eingelesen werden:

	virsh define /tmp/examplebr0.xml

Das Netzwerk `examplebr0` wurde nun in `libvirt` konfiguriert.

Damit das Netzwerk bei Systemstart sicher startet, wird für das Netzwerk das `Autostart-Flag` gesetzt:

	virsh net-autostart examplebr0

Der vSwitch wurde nun für den Einsatz mit KVM konfiguriert. Dies kann folgendermassen kontrolliert werden:

	virsh net-list

Liefert folgendes zurück:

	 Name                 State      Autostart     Persistent
	----------------------------------------------------------
	 examplebr0           active     yes           yes

# VMs an den Open vSwitch anbinden
Die Erstellung von VMs ist im Artikel [Erstellen virtueller Maschinen mit KVM unter Ubuntu 14.04](http://blog.aurka.com/erstellen-virtueller-maschinen-mit-kvm-unter-ubuntu-1404.html) erklärt.
Nun beherrscht `virt-install` leider (noch) keine Erstellung von VMs mit Open vSwitch. Deshalb gibt es einen Workaround. Die VM wird mit der Option `--nonetworks` erstellt; also ohne Netzwerkkonfiguration:

	virt-install --connect qemu:///system --name example1 --ram=24109 --vcpus=4 \
	--disk path=/var/vm/example1/example1.qcow2,size=2500,format=qcow2 \
	--cdrom=/var/vm/ISO/ubuntu-14.04-server-amd64.iso --vnc \
	--os-variant=ubuntutrusty --nonetworks

Nun kann die VM installiert werden. Wenn hierfür Netzwerk benötigt wird muss bereits vor der Installation die Konfiguration der VM verändert werden. Ansonsten muss dies einfach gemacht werden, sobald Netzwerk benötigt wird. Die VM muss hierfür ausgeschaltet sein (respektive die Veränderungen werden erst aktiv, wenn die Maschine via `virsh` neu gestartet wird -> das XML File muss neu eingelesen werden):

	virsh edit example1

Direkt bevor das `</devices>` Tag kommt nun folgender XML-Part:

	<interface type='bridge'>
	 <source bridge='examplebr0'/>
	 <virtualport type='openvswitch' />
	 <model type='virtio'/>
	</interface>

Nun ist die VM an den vSwitch angeschlossen. Überpüft werden kann dies wiederum mit der Hilfe von:

	ovs-vsctl show

Dieser liefert folgendes zurück:

	Bridge "examplebr0"
           Port "eth0"
               Interface "eth0"
           Port "examplebr0"
               Interface "examplebr0"
                   type: internal
           Port "examplebr0p1"
               Interface "examplebr0p1"
                   type: internal
           Port "vnet0"
               Interface "vnet0"
	ovs_version: "2.0.1"

Neu ist der Port `vnet0`. Der Open vSwitch wird nun für das Networking unter KVM verwendet.

# Weitere Artikel zum Thema KVM unter Ubuntu 14.04

* [Erstellen virtueller Maschinen mit KVM unter Ubuntu 14.04](http://blog.aurka.com/erstellen-virtueller-maschinen-mit-kvm-unter-ubuntu-1404.html)
* [Erstellen virtueller Windows-VMs mit KVM unter Ubuntu 14.04](http://blog.aurka.com/erstellen-virtueller-windows-vms-mit-kvm-unter-ubuntu-1404.html)
* [Backups mit (externen) Snapshots mittels KVM unter Ubuntu 14.04](http://blog.aurka.com/backups-mit-externen-snapshots-mittels-kvm-unter-ubuntu-1404.html)
* [Konvertierung von ESXi-VMs zu KVM unter Ubuntu 14.04](konvertierung-von-esxi-vms-zu-kvm-unter-ubuntu-1404.html)

Anmerkungen und Korrekturen bitte via [Kontakt](http://blog.aurka.com/pages/about.html)
