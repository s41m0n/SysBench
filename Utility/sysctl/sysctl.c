#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/sysctl.h>

int my_var = 0;

static struct ctl_table_header *my_header;

static struct ctl_table my_value[] =
{
    {
        .procname       = "my_value",
        .data           = &my_var,
        .maxlen         = sizeof(int),
        .mode           = 0600,
        .proc_handler   = proc_dointvec_minmax,
    },
    {}
};

static struct ctl_table my_directory[] =
{
    {
        .procname    = "example",
        .mode        = 0600,
        .child       = my_value,
    },
    { }
};

static int __init myInit(void)
{
    /* register the above sysctl */
    my_header = register_sysctl_table(my_directory);
    if (!my_header)
        return -EFAULT;
    return 0;
}

static void __exit myExit(void)
{
    unregister_sysctl_table(my_header);
}
MODULE_LICENSE("GPL");
module_init(myInit);
module_exit(myExit);