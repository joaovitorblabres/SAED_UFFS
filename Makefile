list = numpy matplotlib pyserial scipy PyQt5

install-deb:
	sudo pip3 install $(list)
	sudo apt-get install python3-tk python3-pil python3-pil.imagetk

install-fedora:
	sudo pip3 install $(list)
	sudo pip3 install Pillow --upgrade
	sudo dnf install python3-tkinter

update:
	git pull
