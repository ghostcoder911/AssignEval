# ATmega328P reference (AssignEval AVR track)

Official documentation used for register-level assignment checks:

- [ATmega328P datasheet (Microchip)](https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega328P-DS-DS40002061A.pdf)
- [ATmega328P product page](https://www.microchip.com/en-us/product/ATmega328p)

`register_reference.json` lists GPIO ports, timer/ADC/UART/TWI registers, and special pins (OC0A on PD6, INT0 on PD2, etc.) aligned with the datasheet.

AVR submissions are evaluated by:

1. Cross-compile with `avr-gcc -mmcu=atmega328p` (syntax and MCU-specific rules)
2. Static analysis of register usage, ISRs, and module requirements (no hardware required)
