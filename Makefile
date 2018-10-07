obj-m += testModule/testModule.o

all: 	sysbench testModule/testModule.ko

sysbench: sysbench.c test.c
	gcc sysbench.c test.c -ansi -Wpedantic -Wall -D_REENTRANT -o sysbench

testModule/testModule.ko:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
	mv modules.order Module.symvers ./testModule/

.PHONY:	clean

clean:
	rm -f sysbench
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
