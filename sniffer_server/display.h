#ifndef DISPLAY_H
#define DISPLAY_H

#include <stdint.h>

// 初始化显示屏
void init_display(unsigned int pio_base_address, unsigned int pio_hw_base_address);

// 清空屏幕
void clear_display(unsigned short color);

// 绘制像素
void draw_pixel(unsigned short color, unsigned int x, unsigned int y);

// 设置绘制窗口
void set_window(unsigned int x, unsigned int y, unsigned int width, unsigned int height);

// 生成测试图案
void test_pattern();

// 绘制字符
void draw_char(unsigned short color, unsigned int x, unsigned int y, char c);

#endif