#!/usr/bin/env bash

rm -rf test-tmp/**

# -u for unbuffered STDOUT -- some issues with flushing with async code?!
python3 -u --include txt --tag ben-mac-laptop --username ben --password password test-tmp &

sleep 1
touch test-tmp/foo1.txt
sleep 1
touch test-tmp/foo2.txt
sleep 1
touch test-tmp/foo3.txt
sleep 1
mv test-tmp/foo3.txt test-tmp/foo4.txt
sleep 1


sleep 1
echo 'foo' > test-tmp/foo5.txt
sleep 1
echo 'foo' > test-tmp/foo6.txt
sleep 1
echo 'foo' > test-tmp/foo7.txt
sleep 1

mkdir test-tmp/inner


sleep 1
echo 'foo' > test-tmp/inner/foo5.txt
sleep 1
echo 'foo' > test-tmp/inner/foo6.txt
sleep 1
echo 'foo' > test-tmp/inner/foo7.txt
sleep 1


# (terminate the most recently started background task)
kill $!