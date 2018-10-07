#ifndef __TEST__
#define __TEST__

#define MAX_CYCLE 10000
#define MIN_CYCLE 1

#define MODULE_NAME "testModule"
#define OUTPUT_DIR "output"
#define BUFF_SIZE 1024

#define init_module(module_image, len, param_values) syscall(__NR_init_module, module_image, len, param_values)
#define delete_module(name, flags) syscall(__NR_delete_module, name, flags)

int runTest(int n_cycle, int max_proc, bool active, char *file);

#endif
