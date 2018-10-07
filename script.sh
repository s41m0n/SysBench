#!/bin/bash

re='^[0-9]+$'
file="result"
lkrg_name='p_lkrg'
ntimes=$1
ncycle=$2
path_lkrg=$3

if [[ "$EUID" != 0 ]]; then 
	echo "Error: need root privileges"
  	exit 1
fi

if ! [[ $1 =~ $re ]] ; then
   echo "Error: not a number"
   exit 1
fi

if ! [[ $2 =~ $re ]] ; then
   echo "Error: not a number"
   exit 1
fi

if ! lsmod | grep "$lkrg_name" &> /dev/null ; then
	insmod $path_lkrg > /dev/null
fi


for i in $(seq 1 $ntimes);
do
	echo "N. esecuzione: $i"
	./sysbench $ncycle $file$i".txt" > /dev/null
	rmmod $lkrg_name > /dev/null
	./sysbench $ncycle $file$i".txt" > /dev/null
	insmod $path_lkrg > /dev/null
done
