#!/usr/bin/env bash

for file in $(find flip -name *.py)
do 
    echo 
    echo \# $file
    cat $file
    echo
done