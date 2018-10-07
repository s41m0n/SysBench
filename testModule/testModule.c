#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/stat.h>

static int __init myModule_init(void)
{
	return 0;
}

static void __exit myModule_exit(void)
{
	return;
}

module_init(myModule_init);
module_exit(myModule_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Simone Magnani");
MODULE_DESCRIPTION("An empty module");
