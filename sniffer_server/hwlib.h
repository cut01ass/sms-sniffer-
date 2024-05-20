#ifndef HWLIB_H
#define HWLIB_H

#include <stdint.h>

void init_hw();
void deinit_hw();
void set_led(uint32_t value);
uint32_t get_button_state();

#endif