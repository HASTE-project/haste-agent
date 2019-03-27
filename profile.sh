#!/usr/bin/env bash

python3 -m haste.desktop_agent.simulator /Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/ &

sleep 5

python3 -m cProfile -o profile_759.dat haste/desktop_agent/__main__.py --include .png --tag trash --host haste-gateway.benblamey.com:80 --username haste --password mr_frumbles_bad_day /Users/benblamey/projects/haste/haste-desktop-agent-images/target/ --x-preprocessing-cores 1