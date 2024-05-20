#include "display.h"
#include "DE1SoC_LT24.h"

// 字符的位图数据结构,使用5x7点阵字体
typedef struct {
    unsigned char data[5];
} FontBitmap;

// 所有字符的位图数据
static const FontBitmap font[] = {
    // 'A'
    {0x7C, 0x44, 0x7C, 0x44, 0x38},
    // 'B'
    {0xFC, 0x44, 0x7C, 0x44, 0xFC},
    // 'C'
    {0x3C, 0x40, 0x40, 0x40, 0x3C},
    // 'D'
    {0xFC, 0x44, 0x44, 0x44, 0xFC},
    // 'E'
    {0xFC, 0x40, 0x7C, 0x40, 0xFC},
    // 'F'
    {0xFC, 0x40, 0x7C, 0x40, 0x40},
    // 'G'
    {0x3C, 0x40, 0x4C, 0x44, 0x3C},
    // 'H'
    {0x44, 0x44, 0xFC, 0x44, 0x44},
    // 'I'
    {0x7C, 0x10, 0x10, 0x10, 0x7C},
    // 'J'
    {0x1C, 0x08, 0x08, 0x48, 0x7C},
    // 'K'
    {0x44, 0x48, 0x70, 0x48, 0x44},
    // 'L'
    {0x40, 0x40, 0x40, 0x40, 0xFC},
    // 'M'
    {0x44, 0x6C, 0x54, 0x44, 0x44},
    // 'N'
    {0x44, 0x64, 0x54, 0x4C, 0x44},
    // 'O'
    {0x3C, 0x44, 0x44, 0x44, 0x3C},
    // 'P'
    {0xFC, 0x44, 0x7C, 0x40, 0x40},
    // 'Q'
    {0x3C, 0x44, 0x44, 0x64, 0x3C},
    // 'R'
    {0xFC, 0x44, 0x7C, 0x48, 0x44},
    // 'S'
    {0x7C, 0x40, 0x3C, 0x04, 0xFC},
    // 'T'
    {0x7C, 0x10, 0x10, 0x10, 0x10},
    // 'U'
    {0x44, 0x44, 0x44, 0x44, 0x3C},
    // 'V'
    {0x44, 0x44, 0x28, 0x28, 0x10},
    // 'W'
    {0x44, 0x54, 0x54, 0x54, 0x38},
    // 'X'
    {0x44, 0x28, 0x10, 0x28, 0x44},
    // 'Y'
    {0x44, 0x28, 0x10, 0x10, 0x10},
    // 'Z'
    {0x7C, 0x04, 0x38, 0x40, 0x7C}
};

// 初始化显示屏
void init_display(unsigned int pio_base_address, unsigned int pio_hw_base_address) {
    LT24_initialise(pio_base_address, pio_hw_base_address);
}

// 清空屏幕
void clear_display(unsigned short color) {
    LT24_clearDisplay(color);
}

// 绘制像素
void draw_pixel(unsigned short color, unsigned int x, unsigned int y) {
    LT24_drawPixel(color, x, y);
}

// 设置绘制窗口
void set_window(unsigned int x, unsigned int y, unsigned int width, unsigned int height) {
    LT24_setWindow(x, y, width, height);
}

// 生成测试图案
void test_pattern() {
    LT24_testPattern();
}

// 绘制字符
void draw_char(unsigned short color, unsigned int x, unsigned int y, char c) {
    unsigned char bitmap;
    int row, col;

    // 确保字符在A-Z范围内
    if (c < 'A' || c > 'Z') {
        return;
    }

    // 获取字符的位图数据
    const FontBitmap *font_bitmap = &font[c - 'A'];

    // 遍历位图数据,绘制像素
    for (row = 0; row < 7; row++) {
        bitmap = font_bitmap->data[row / 7];
        for (col = 0; col < 5; col++) {
            if (bitmap & (1 << (4 - col))) {
                draw_pixel(color, x + col, y + row);
            }
        }
    }
}