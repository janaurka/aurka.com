Title: Konvertierung von ESXi-VMs zu KVM unter Ubuntu 14.04
Date: 2014-06-06
Tags: ubuntu, trusty, linux, kvm, libvirt, qemu, debian, tech, howto, convert, esx, vmware, esxi
Category: tech
Author: janssen

Dies ist der vierte Post zum Thema Ubuntu 14.04 und KVM. Dieser behandelt die Konvertierung von [VMWare ESXi](http://www.vmware.com/products/vsphere-hypervisor) VMs zu KVM.

# Umgebung
Sämtliche Informationen gelten für folgende Testumgebung:

* Ursprung: VMWare ESXi 4.x oder 5.x (vmx Konfigurationsdatei und vmdk Images)
* KVM: Ubuntu 14.04 64bit Server (xml Konfigurationsdatei und qcow2 Images)

# Requirements
Für die Konvertierung folgendes benötigt:

* Paket `virtinst`
* VMX und VMDK Dateien der zu konvertierenden VM

Zusätzlich werden selbstverständlich die Pakete für KVM (und Open vSwitch) benötigt.


# VMs konvertieren
Um eine VM von ESXi zu KVM zu konvertieren, müssen zuerst die VMX und die VMDK Dateien der gewünschten VM auf den KVM Wirth übertragen werden. Sollten die VMDK-Images aus mehreren Teilen bestehen, können diese mit `cat` zusammgeführt werden -> `cat part1.vmdk part2.vmdk > disk.vmdk`. Die Konvertierung kann nun gestartet werden:

	virt-convert -D qcow2 example.vmx

Der Befehl erstellt einen neuen Ordner mit dem Namen der soeben konvertierten VM. Dieser beinhaltet eine grundlegene XML-Datei (welche nicht benötigt wird) und ein qcow2-Image. Grundsätzlich könnte das erstellte XML-File verwendet werden, um die Maschine gleich in `libvirt` zu definieren, der Weg über `virt-install` ist jedoch bedeutend einfacher. Mit der Hilfe von `virt-install` wird die Maschine nun definiert:

	virt-install --connect qemu:///system --name example --ram=2048 --vcpus=2 --disk path=/var/vm/example/example.qcow2,size=30,format=qcow2 --vnc --os-variant=ubuntuprecise --nonetworks --import

An der Stelle der Angabe einer ISO-Datei für die Installation wird das Argument `--import` verwendet.

Die Maschine ist nun definiert und kann ganz normal via `virsh` gestartet werden:

	virsh start example

Und bereits läuft die ehemalige ESXi VM unter KVM. Natürlich sollten/können nun in der VM gewisse Dinge umgestellt werden. Beispielsweise können die VMware-Tools deinstalliert werden. Weiter empfielt sich die verwendung von `linux-virtual` als Kernel (aber das empfiehlt sich bereits unter ESXi).

# Weitere Artikel zum Thema KVM unter Ubuntu 14.04

* [Erstellen virtueller Maschinen mit KVM unter Ubuntu 14.04](http://aurka.com/erstellen-virtueller-maschinen-mit-kvm-unter-ubuntu-1404.html)
* [Erstellen virtueller Windows-VMs mit KVM unter Ubuntu 14.04](http://aurka.com/erstellen-virtueller-windows-vms-mit-kvm-unter-ubuntu-1404.html)
* [Backups mit (externen) Snapshots mittels KVM unter Ubuntu 14.04](http://aurka.com/backups-mit-externen-snapshots-mittels-kvm-unter-ubuntu-1404.html)
* [Open vSwitch mit KVM unter Ubuntu 14.04](http://aurka.com/open-vswitch-mit-kvm-unter-ubuntu-1404.html)

Anmerkungen und Korrekturen bitte via [Kontakt](http://aurka.com/pages/about.html)
