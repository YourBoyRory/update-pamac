#!/bin/bash

sudo cp ./update-pamac.py /usr/local/bin/update-pamac
sudo chmod 755 /usr/local/bin/update-pamac

sudo mkdir -p /etc/install-pamac-options/
sudo cp ./pamac-options.json /etc/install-pamac-options/
sudo chmod 644 /etc/install-pamac-options/pamac-options.json
