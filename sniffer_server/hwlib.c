#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include "hwlib.h"
#include "socal/socal.h"
#include "socal/hps.h"
#include "socal/alt_gpio.h"

#define HW_REGS_BASE (ALT_STM_OFST)
#define HW_REGS_SPAN (0x04000000)
#define HW_REGS_MASK (HW_REGS_SPAN - 1)

#define USER_IO_DIR   (0x01000000)
#define BIT_LED       (0x01000000)
#define BUTTON_MASK   (0x02000000)

static void *virtual_base;
static int fd;

void init_hw() {
    // 映射寄存器地址空间
    fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd == -1) {
        printf("ERROR: could not open \"/dev/mem\"...\n");
        return;
    }

    virtual_base = mmap(NULL, HW_REGS_SPAN, PROT_READ | PROT_WRITE, MAP_SHARED, fd, HW_REGS_BASE);
    if (virtual_base == MAP_FAILED) {
        printf("ERROR: mmap() failed...\n");
        close(fd);
        return;
    }

    // 初始化GPIO控制器
    alt_setbits_word((virtual_base + ((uint32_t)(ALT_GPIO1_SWPORTA_DDR_ADDR) & (uint32_t)(HW_REGS_MASK))), USER_IO_DIR);
}

void deinit_hw() {
    // 取消映射并关闭文件描述符
    munmap(virtual_base, HW_REGS_SPAN);
    close(fd);
}

void set_led(uint32_t value) {
    if (value) {
        alt_setbits_word((virtual_base + ((uint32_t)(ALT_GPIO1_SWPORTA_DR_ADDR) & (uint32_t)(HW_REGS_MASK))), BIT_LED);
    } else {
        alt_clrbits_word((virtual_base + ((uint32_t)(ALT_GPIO1_SWPORTA_DR_ADDR) & (uint32_t)(HW_REGS_MASK))), BIT_LED);
    }
}

uint32_t get_button_state() {
    return alt_read_word((virtual_base + ((uint32_t)(ALT_GPIO1_EXT_PORTA_ADDR) & (uint32_t)(HW_REGS_MASK))));
}