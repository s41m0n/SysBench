#define _GNU_SOURCE

#include <time.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/fsuid.h>
#include <sys/time.h>
#include <sys/syscall.h>
#include "test.h"

typedef struct myStruct
{
    char *name;
    int (*function) ();
    double time;
} Syscall;

static int testSetuid(Syscall *self);
static int testSetgid(Syscall *self);
static int testSetresuid(Syscall *self);
static int testSetresgid(Syscall *self);
static int testSetreuid(Syscall *self);
static int testSetregid(Syscall *self);
static int testSetfsuid(Syscall *self);
static int testSetfsgid(Syscall *self);
static int testOpen(Syscall *self);
static int testFork(Syscall *self);
static int testExecve(Syscall *self);
static int testModule(Syscall *self, Syscall *other);
static int saveResults();
static Syscall* findSyscall(char *name);

static Syscall Array[] =
{
    { "`setuid()`", testSetuid, -1}, { "`setgid()`", testSetgid, -1},
    { "`setresuid()`", testSetresuid, -1}, { "`setresgid()`", testSetresgid, -1},
    { "`setreuid()`", testSetreuid, -1}, { "`setregid()`", testSetregid, -1},
    { "`setfsuid()`", testSetfsuid, -1}, { "`setfsgid()`", testSetfsgid, -1},
    { "`open()`",   testOpen, -1}, { "`fork()`",   testFork, -1},
    { "`execve()`", testExecve, -1}, { "`insert_module()`", testModule, -1},
    { "`delete_module()`", testModule, -1}
};
static int ncycle = 0;
static unsigned long nproc = 0;
static bool loaded;

int runTest(int n_cycle, int n_proc, bool active, char *file)
{
    int i, ret, size = sizeof(Array) / sizeof(Syscall);
    bool done = false, is_insert = false;
    Syscall *other = NULL;
    
    ncycle = n_cycle;
    nproc = n_cycle <= n_proc ? n_cycle : n_proc;
    loaded = active;

    if(loaded) printf ("Running the test (LKRG LOADED)\n");
    else printf ("Running the test (LKRG UNLOADED)\n");
    
    for (i = 0; i < size; i++)
    {
        if((is_insert = (strcmp(Array[i].name, "`insert_module()`") == 0)) || strcmp(Array[i].name, "`delete_module()`") == 0)
        {
            if (done) continue;
            else done = true;
            other = is_insert ? findSyscall("`delete_module()`") : findSyscall("`insert_module()`");
            printf("\t-> Testing %-16s + %-16s ... ", Array[i].name, (*other).name);
            fflush(stdout);
            ret = is_insert ? Array[i].function(&Array[i], other) : Array[i].function(other, &Array[i]);
        } else
        {
            printf("\t-> Testing %-37s ... ", Array[i].name);
            fflush(stdout);
            ret = Array[i].function(&Array[i]);
        }
        if (ret == 0) printf("done\n");
        else printf("failed\n");
    }
    return saveResults(file);
}

static int testSetuid(Syscall *self)
{
    int uid = getuid(), i;
    struct timeval start, end;

    gettimeofday(&start, NULL);
    for (i = 0; i < ncycle; i++)
        if(setuid(uid) != 0) return 1;
    gettimeofday(&end, NULL);
    self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    return 0;
}

static int testSetgid(Syscall *self)
{
    int gid = getgid(), i;
    struct timeval start, end;

    gettimeofday(&start, NULL);
    for (i = 0; i < ncycle; i++)
        if(setgid(gid) != 0) return 1;
    gettimeofday(&end, NULL);
    self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    return 0;
}

static int testSetresuid(Syscall *self)
{
    uid_t ruid, euid, suid;
    int i;
    struct timeval start, end;

    if(getresuid(&ruid, &euid, &suid) != 0) return 1;

    gettimeofday(&start, NULL);
    for (i = 0; i < ncycle; i++)
        if(setresuid(ruid, euid, suid) != 0) return 1;
    gettimeofday(&end, NULL);
    self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    return 0;
}

static int testSetresgid(Syscall *self)
{
    gid_t rgid, egid, sgid;
    int i;
    struct timeval start, end;

    if(getresgid(&rgid, &egid, &sgid) != 0) return 1;

    gettimeofday(&start, NULL);
    for (i = 0; i < ncycle; i++)
        if(setresgid(rgid, egid, sgid) != 0) return 1;
    gettimeofday(&end, NULL);
    self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    return 0;
}

static int testSetreuid(Syscall *self)
{
    uid_t ruid, euid;
    int i;
    struct timeval start, end;

    ruid = getuid();
    euid = geteuid();

    gettimeofday(&start, NULL);
    for (i = 0; i < ncycle; i++)
        if(setreuid(ruid, euid) != 0) return 1;
    gettimeofday(&end, NULL);
    self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    return 0;
}

static int testSetregid(Syscall *self)
{
    uid_t rgid, egid;
    int i;
    struct timeval start, end;

    rgid = getgid();
    egid = getegid();

    gettimeofday(&start, NULL);
    for (i = 0; i < ncycle; i++)
        if(setregid(rgid, egid) != 0) return 1;
    gettimeofday(&end, NULL);
    self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    return 0;
}

static int testSetfsuid(Syscall *self)
{
    uid_t uid;
    int i;
    struct timeval start, end;

    uid = getuid();
    gettimeofday(&start, NULL);
    for (i = 0; i < ncycle; i++)
        setfsuid(uid);
    gettimeofday(&end, NULL);
    self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    return 0;
}

static int testSetfsgid(Syscall *self)
{
    gid_t gid;
    int i;
    struct timeval start, end;

    gid = getgid();
    gettimeofday(&start, NULL);
    for (i = 0; i < ncycle; i++)
        setfsgid(gid);
    gettimeofday(&end, NULL);
    self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    return 0;
}

static int testOpen(Syscall *self)
{
    int i, fd;
    struct timeval start, end;

    gettimeofday(&start, NULL);
    for(i = 0; i < ncycle; i++)
    {
        fd = open("/etc/passwd", O_RDONLY);
        if (fd == -1) return 1;
        close(fd);
    }
    gettimeofday(&end, NULL);
    self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    return 0;
}

static int testFork(Syscall *self)
{
    pid_t pid;
    struct timeval start, end;
    int i, ret = 0;

    gettimeofday(&start, NULL);
    for(i = 0; i < nproc; i++)
    {
        if((pid = fork()) < 0) {
            ret = 1;
            break;
        } else if(pid == 0)
        {
            exit(0);
        }
    }
    while ((pid = waitpid(-1, NULL, 0)))
        if (errno == ECHILD) break;
    if(ret == 0)
    {
        gettimeofday(&end, NULL);
        self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    }
    return ret;
}

static int testExecve(Syscall *self)
{
    pid_t pid, saved_stdout;
    struct timeval start, end;
    int i, ret = 0;
    char *const parameters[] = {"/bin/ls", "-l", NULL};
    int fd = open("/dev/null", O_WRONLY);
    /*This way output is temporarly redirected to /dev/null*/
    saved_stdout = dup(1);
    dup2(fd, 1);
    dup2(fd, 2);
    close(fd);
    
    gettimeofday(&start, NULL);
    for (i = 0; i < nproc; i++)
    {
        pid = fork();
        if (pid == -1){
            ret = 1;
            break;
        }
        else if (pid == 0)
        {
            printf("ok\n");
            execve("/bin/ls", parameters, NULL);
            exit(1);
        }
    }
    while (waitpid(-1,NULL,WNOHANG)!=-1);
    gettimeofday(&end, NULL);
    /*Restoring output*/
    dup2(saved_stdout, 1);
    close(saved_stdout);
    if(ret == 0)
        self->time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    return ret;
}

static int testModule(Syscall *self, Syscall *other)
{
    struct stat st;
    size_t image_size;
    void *image;
    struct timeval start, end;
    double sum_insmod = 0, sum_rmmod = 0;
    char name[] = MODULE_NAME "/" MODULE_NAME ".ko";
    int i, fd = open(name, O_RDONLY);

    if(getuid() != 0) return 1;

    fstat(fd, &st);
    image_size = st.st_size;
    image = malloc(image_size);
    read(fd, image, image_size);
    for(i = 0; i < ncycle; i++)
    {
        gettimeofday(&start, NULL);
        if(init_module(image, image_size, "") != 0) return 1;
        gettimeofday(&end, NULL);
        sum_insmod += (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
        gettimeofday(&start, NULL);
        if (delete_module(MODULE_NAME, O_NONBLOCK) != 0) return 1;
        gettimeofday(&end, NULL);
        sum_rmmod += (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    }
    free(image);
    close(fd);
    self->time = sum_insmod;
    other->time = sum_rmmod;
    return 0;
}

static int saveResults(char *file)
{
    int i, fd, dir, size = sizeof(Array) / sizeof(Syscall);
    time_t timer;
    char to_save[BUFF_SIZE] = OUTPUT_DIR "/", buff[BUFF_SIZE] = "";

    dir = mkdir(OUTPUT_DIR, S_IRUSR | S_IWUSR | S_IXUSR);
    if(dir == -1 && errno != EEXIST) return 1;

    strcat(to_save, file);
    fd = open(to_save, O_WRONLY | O_APPEND | O_CREAT, 0777);
    if(fd == -1) return 1;
    
    time(&timer);

    strftime(buff, 36, "SysBench %Y-%m-%d %H:%M:%S ", localtime(&timer));
    if(loaded) sprintf(buff + strlen(buff), "(lkrg ON, ncycle=%d, nproc=%lu)\n", ncycle, nproc);
    else sprintf(buff + strlen(buff), "(lkrg OFF, ncycle=%d, nproc=%lu)\n", ncycle, nproc);
    sprintf(buff + strlen(buff), "\tFunction%*cTot%*cMean\n", 13, ' ', 16, ' ');
    if(write(fd, buff, strlen(buff)) == -1) return 1;

    for (i = 0; i < size; i++)
    {
        if(Array[i].time == -1)
            sprintf(buff, "\t%-18s-> \t/\t/\n", Array[i].name);
        else
            if(strcmp(Array[i].name, "`fork()`") == 0 || strcmp(Array[i].name, "`execve()`") == 0)
                sprintf(buff, "\t%-18s-> %e\t%e\n", Array[i].name, Array[i].time, Array[i].time / nproc);
            else
                sprintf(buff, "\t%-18s-> %e\t%e\n", Array[i].name, Array[i].time, Array[i].time / ncycle);
        if(write(fd, buff, strlen(buff)) == -1) return 1;
    }
    close(fd);
    return 0;
}

static Syscall* findSyscall(char *name)
{
    int i, size = sizeof(Array) / sizeof(Syscall);
    for(i = 0; i < size; i++)
        if(strcmp(Array[i].name, name) == 0)
            return &Array[i];
    return NULL;
}