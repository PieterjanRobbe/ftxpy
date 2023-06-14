#!/bin/bash

num=$1
for n in {1..64}
do
    a=$(((n - 1)*32 + 1))
    b=$((32*n))
    batch=${a}_${b}
    python examples/gsa_${num}_perlmutter.py define $batch
    python examples/gsa_${num}_perlmutter.py start $batch
    echo $batch
done