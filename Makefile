list = python3-tk python3-pil python3-pil.imagetk

install-deb:
	sudo pip3 install numpy matplotlib pyserial scipy PyQt5
	sudo apt-get install $(list)

install-fedora:
	sudo pip3 install numpy matplotlib pyserial scipy PyQt5
	sudo dmf install $(list)

update:
	git pull
