#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 3
#endif

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h>
#include <ctype.h>
#include <fcntl.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/resource.h>
#include "test.h"

int main(int argc, char *argv[])
{
#ifndef __linux__
    printf("This software cannot be run into a different OS than Linux\n");
    return 1;
#endif
    int ncycle, nproc, i, offset;
    char buf[16];
    struct winsize w;
    struct rlimit rl;
    FILE *fd = popen("lsmod | grep p_lkrg", "r");
    bool active = fread (buf, 1, sizeof (buf), fd);

    if(argc != 3)
    {
        printf("Error: need exactly 2 arguments (ncycle, filename)\n");
        exit(1);
    }

    if (sscanf (argv[1], "%i", &ncycle) != 1) {
        printf("Error: ncycle is not an integer.\n");
        exit(1);
    }

    if (ncycle < MIN_CYCLE || ncycle > MAX_CYCLE)
    {
        printf("Error: ncycle too big, range value [%d,%d].\n", MIN_CYCLE, MAX_CYCLE);
        exit(1);
    }

    if (strchr(argv[2], '/') != NULL)
    {
        printf("Error: the file name must not contain -> / .\n");
        exit(1);
    }

    if(strstr(argv[2], ".txt") == NULL)
    {
        printf("Error: must insert a .txt file\n");
        exit(1);
    }

    if(strlen(argv[2]) + strlen(OUTPUT_DIR) > BUFF_SIZE)
    {
        printf("Error: file name too long\n");
        exit(1);
    }

    getrlimit(RLIMIT_NPROC, &rl);
    fclose(fd);
    nproc = ncycle > rl.rlim_cur / 2 ? rl.rlim_cur / 2 : ncycle;

    /*To get the terminal width*/
    ioctl(STDOUT_FILENO, TIOCGWINSZ, &w);
    offset  = w.ws_col / 2 - 4;

    /*To clear the screen*/
    printf("\033[H\033[J");

    /*Welcome part*/
    for(i = 0; i < w.ws_col; i++) putchar('*');
    for(i = 0; i < offset; i++) putchar(' ');
    printf("SysBench");
    if(w.ws_col % 2) putchar(' ');
    for(i = 0; i < offset; i++) putchar(' ');
    for(i = 0; i < w.ws_col; i++) putchar('*');
    printf("Welcome to SysBench, a program to measure time execution of many system calls\n\n"
           "Instructions:\n"
           "-> (INPUT)ncycle = number of system call executed [%d, %d];\n"
           "-> results will be stored in `%s/%s`\n"
           "-> waiting time depends on ncycle (if >= 10000 could take long time to finish) especially `insert_module()` and `delete_module()`. :D\n\n"
           "NB: root privileges needed to test `insert_module()` and `delete_module()`\n"
           "NBB: to be safe, max process created is half the number read in /proc/self/limits\n\n",
           MIN_CYCLE, MAX_CYCLE, OUTPUT_DIR, argv[2]);

    if(runTest(ncycle, nproc, active, argv[2]) != 0) {
        printf("Failed to save, try again.\n\n");
        return 1;
    }
    printf("Successfully stored results.\n");
    return 0;
}
