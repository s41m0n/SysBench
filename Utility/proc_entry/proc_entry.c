#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/sched.h>
#include <linux/uaccess.h>
#include <linux/slab.h>
#define MSG_SIZE (512)

static char *msg;
static int len,tmp;

ssize_t write_proc(struct file *filp, const char *buf, size_t count, loff_t *offp)
{
    unsigned long actual_len = count < MSG_SIZE - 1 ? count : MSG_SIZE - 1;
    copy_from_user(msg, buf, actual_len);
    len = count;
    tmp = len;
    return len;
}

ssize_t read_proc(struct file *filp, char *buf, size_t count, loff_t *offp)
{
    if(count > tmp) 
        count = tmp;
    tmp = tmp - count;
    copy_to_user(buf, msg, count);
    if(count == 0)
        tmp = len;
    return count;
}

struct file_operations proc_fops =
{
write:
    write_proc,
read:
    read_proc
};

static int __init proc_init(void)
{
    if ((msg = kmalloc(MSG_SIZE, GFP_KERNEL)) == NULL)
        return -ENOMEM;
    proc_create("myProc", 0, NULL, &proc_fops);
    return 0;
}

static void __exit proc_exit(void)
{
    remove_proc_entry("myProc", NULL);
    kfree(msg);
}

MODULE_LICENSE("GPL");
module_init(proc_init);
module_exit(proc_exit);