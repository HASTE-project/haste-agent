#!/usr/bin/env bash

rm test-tmp/*

python3 -m haste.desktop-agent test-tmp &

sleep 1
touch test-tmp/foo1.txt
sleep 1
touch test-tmp/foo2.txt
sleep 1
touch test-tmp/foo3.txt
sleep 1
mv test-tmp/foo3.txt test-tmp/foo4.txt
sleep 1

# (terminate the most recently started background task)
kill $!