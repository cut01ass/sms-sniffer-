import ctypes

# 加载硬件库
hwlib = ctypes.CDLL('./hwlib.so')

# 加载显示库
display = ctypes.CDLL('./display.so')

def init_hw():
    hwlib.init_hw()
    display.init_display(0xFF200060, 0xFF200080)

def deinit_hw():
    hwlib.deinit_hw()

def get_button1_state():
    return hwlib.get_button1_state()

def get_button2_state():
    return hwlib.get_button2_state()

def get_button3_state():
    return hwlib.get_button3_state()

def get_button4_state():
    return hwlib.get_button4_state()

def display_message(message):
    display.clear_display(0x0000)
    display.draw_string(0xFFFF, 0x0000, 10, 100, message.encode())