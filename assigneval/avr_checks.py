"""Static register-level checks for ATmega328P assignments (no hardware)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class AvrCheck:
    name: str
    weight: float = 1.0


CheckFn = Callable[[str], tuple[bool, str]]


def _norm(code: str) -> str:
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//.*?$", "", code, flags=re.MULTILINE)
    return code


def _search(code: str, pattern: str) -> re.Match[str] | None:
    try:
        return re.search(pattern, code, re.IGNORECASE)
    except re.error as exc:
        raise re.error(f"Invalid AVR check pattern {pattern!r}: {exc}") from exc


def _has(code: str, *patterns: str) -> bool:
    return all(_search(code, p) for p in patterns)


def _has_any(code: str, *patterns: str) -> bool:
    return any(_search(code, p) for p in patterns)


def _user_functions(code: str) -> int:
    return len(re.findall(r"\b(?:void|int|uint8_t|uint16_t)\s+([a-zA-Z_]\w*)\s*\(", code))


def _has_isr(code: str, vector: str | None = None) -> bool:
    if vector:
        return bool(re.search(rf"ISR\s*\(\s*{re.escape(vector)}\s*\)", code, re.I))
    return bool(re.search(r"ISR\s*\(", code, re.I))


def check_portd_pd5_led(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"\bPORTD\b", r"\bDDRD\b"):
        return False, "Should configure PORTD (PORTD/DDRD registers)."
    if not _has_any(c, r"PD5", r"DDB5", r"DDD5", r"PORTD\s*&=\s*~?\s*\(1\s*<<\s*5", r"1\s*<<\s*5", r"0x20"):
        return False, "LED should use PORTD pin 5 (PD5 / bit 5)."
    if not _has_any(c, r"while\s*\(\s*1\s*\)", r"for\s*\(\s*;\s*;\s*\)"):
        return False, "Should loop continuously."
    if not _has_any(c, r"3000", r"_delay_ms\s*\(\s*3000", r"3\s*\*\s*1000"):
        return False, "Should include ~3 second ON timing."
    if not _has_any(c, r"5000", r"_delay_ms\s*\(\s*5000", r"5\s*\*\s*1000"):
        return False, "Should include ~5 second OFF timing."
    return True, "PORTD.5 LED timing pattern present."


def check_two_led_button_toggle(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"\bDDR", r"\bPORT"):
        return False, "GPIO registers (DDR/PORT) required."
    if not _has_any(c, r"button|switch|PIND|PINB|PINC|INT"):
        return False, "Push-button input handling expected."
    if not _has_any(c, r"\^=|toggle|XOR|red|green"):
        return False, "Should toggle between two LED states."
    return True, "Dual-LED toggle logic detected."


def check_train_portb(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"\bPORTB\b", r"\bDDRB\b"):
        return False, "Train LEDs should use PORTB."
    if not _has_any(c, r"<<|>>|shift|train"):
        return False, "Sequential shift / train pattern expected."
    if len(re.findall(r"1\s*<<\s*[0-7]", c)) < 1 and not _has_any(c, r"PORTB\s*=", r"\|="):
        return False, "Bit shifting or PORTB updates for multiple LEDs expected."
    return True, "PORTB shifting LED pattern present."


def check_binary_counter_portb(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"\bPORTB\b"):
        return False, "Four LEDs on PORTB (pins 0–3)."
    if not _has_any(c, r"\bPIND\b|\bPORTD\b") and not _has_any(c, r"INT0|PD2"):
        return False, "Button on PORTD pin 2 (PIND/INT0) expected."
    if not _has_any(c, r"counter|count|\+\s*\+|=\s*0|15|0x0f"):
        return False, "Binary counter 0–15 with wrap expected."
    if _user_functions(c) < 1:
        return False, "Use a dedicated function to update LED states."
    return True, "Binary counter with function detected."


def check_traffic_no_delay(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if _has(c, r"\b_delay\s*\("):
        return False, "Must not use _delay(); use hardware timers per assignment."
    if not _has_any(c, r"\bTCCR", r"\bOCR", r"\bTCNT", r"TIMER"):
        return False, "Timer registers (TCCR/OCR/TCNT) required."
    if not _has_any(c, r"green|orange|red|10|3000|3\s*\*\s*1000"):
        return False, "Traffic light sequence timings (10s/3s) expected."
    return True, "Timer-based traffic light (no _delay) detected."


def check_traffic_int0_flag(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_isr(c) and not _has_any(c, r"INT0|EIFR|EICRA|EIMSK"):
        return False, "External interrupt INT0 setup expected."
    if not _has_any(c, r"flag|volatile"):
        return False, "ISR should set a flag (volatile), not change lights immediately."
    if not _has_any(c, r"green|orange|red"):
        return False, "Three traffic LEDs expected."
    return True, "INT0 ISR flag-based traffic control detected."


def check_dual_timer_isr(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"TCCR1|OCR1|TIMSK1|TIMER1"):
        return False, "Timer1 (TCCR1/OCR1/TIMSK1) required for 2s LED."
    if not _has_any(c, r"TCCR2|OCR2|TIMSK2|TIMER2"):
        return False, "Timer2 (TCCR2/OCR2/TIMSK2) required for 500ms LED."
    if len(re.findall(r"ISR\s*\(", c, re.I)) < 2:
        return False, "Two separate ISR handlers expected."
    if not _has_any(c, r"OCIE1|TIMER1_COMP") or not _has_any(c, r"OCIE2|TIMER2_COMP"):
        return False, "Compare-match interrupts for both timers expected."
    return True, "Timer1 + Timer2 compare-match ISRs detected."


def check_timer0_fast_pwm_oc0a(code: str, require_debounce: bool = False) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"TCCR0", r"OCR0A", r"OC0A", r"COM0A", r"WGM0"):
        return False, "Timer0 Fast PWM: TCCR0A/B, OCR0A, COM0A/WGM bits expected."
    if not _has_any(c, r"PD6|DDD6|PORTD.*6|OC0A"):
        return False, "PWM output on OC0A (PORTD pin 6) expected."
    if not _has_any(c, r"OCR0A"):
        return False, "Duty cycle via OCR0A updates expected."
    if require_debounce and not _has_any(c, r"debounc|DEBOUNCE|stable|previous"):
        return False, "Button debouncing (software or logic) required for Q9."
    return True, "Timer0 Fast PWM on OC0A detected."


def check_lm35_adc_motor(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"ADMUX|ADCSRA|ADC|ADCH"):
        return False, "ADC registers (ADMUX/ADCSRA) expected for LM35."
    if not _has_any(c, r"motor|PWM|OCR|TCCR|PORT"):
        return False, "DC motor control via PWM/GPIO expected."
    if _user_functions(c) < 2:
        return False, "Separate functions for sensor, speed, and motor control expected."
    return True, "ADC + motor control with functions detected."


def check_servo_timer1_phase_pwm(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"ADMUX|ADCSRA|ADC"):
        return False, "ADC read for potentiometer (channel 0) expected."
    if not _has_any(c, r"TCCR1|OCR1A|OC1A|COM1A|WGM1"):
        return False, "Timer1 Phase Correct PWM on OC1A (PB1) for servo."
    if _user_functions(c) < 1:
        return False, "Function to map ADC value to pulse width expected."
    return True, "ADC + Timer1 servo PWM pattern detected."


def check_lcd_counter_button(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"LCD|lcd|4\s*bit|RS|EN"):
        return False, "LCD interface (parallel) expected."
    if not _has_any(c, r"counter|count|000000000|digit"):
        return False, "9-digit counter display expected."
    if not _has_any(c, r"2000|2\s*\*\s*1000|long|hold"):
        return False, "Long-press (2s) reset logic expected."
    if _user_functions(c) < 2:
        return False, "Functions for button timing and LCD update expected."
    return True, "LCD counter with press-duration logic detected."


def check_uart_pwm_led(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"UBRR0|UCSR0|UDR0|uart|USART"):
        return False, "UART (UBRR0/UCSR0/UDR0) at 9600 baud expected."
    if not _has_any(c, r"9600|103"):
        return False, "Baud rate 9600 configuration expected."
    if not _has_any(c, r"ON|OFF|brightness|%"):
        return False, "Commands ON/OFF/brightness handling expected."
    if not _has_any(c, r"TCCR|OCR|PWM|COM"):
        return False, "Hardware PWM for LED brightness expected."
    return True, "UART + PWM command handling detected."


def check_adc_pot_motor_pwm(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"ADMUX|ADCSRA|ADC"):
        return False, "ADC channel 0 read expected."
    if not _has_any(c, r"TCCR0|OCR0A|OC0A|Fast\s*PWM|WGM0"):
        return False, "Timer0 Fast PWM on OC0A for motor expected."
    if _user_functions(c) < 1:
        return False, "Function to scale ADC to OCR0A expected."
    return True, "ADC to Timer0 PWM mapping detected."


def check_i2c_bmp280_oled(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"TWCR|TWDR|TWSR|TWBR|TWI|i2c|I2C"):
        return False, "I2C/TWI registers (TWCR/TWDR/TWSR) expected."
    if not _has_any(c, r"BMP280|bmp|0x76|0x77"):
        return False, "BMP280 sensor communication expected."
    if not _has_any(c, r"OLED|ssd1306|display|128"):
        return False, "OLED display over I2C expected."
    if not _has_any(c, r"2000|2\s*\*\s*1000|delay"):
        return False, "Periodic update (~2 seconds) expected."
    return True, "I2C BMP280 + OLED pattern detected."


def check_avr_headers(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if not _has_any(c, r"avr/io\.h|avr/io"):
        return False, "Include <avr/io.h> for register definitions."
    return True, "AVR headers present."


def check_no_arduino_only(code: str) -> tuple[bool, str]:
    c = _norm(code)
    if _has(c, r"\bdigitalWrite\b|\bpinMode\b|\bSerial\.begin\b"):
        return False, "Use register-level code, not Arduino wiring API."
    return True, "Register-level style (no Arduino API)."


AVR_QUESTION_CHECKS: dict[int, list[tuple[AvrCheck, CheckFn]]] = {
    1: [
        (AvrCheck("portd_pd5_timing"), check_portd_pd5_led),
        (AvrCheck("avr_headers"), check_avr_headers),
        (AvrCheck("register_style"), check_no_arduino_only),
    ],
    2: [
        (AvrCheck("dual_led_toggle"), check_two_led_button_toggle),
        (AvrCheck("avr_headers"), check_avr_headers),
        (AvrCheck("register_style"), check_no_arduino_only),
    ],
    3: [
        (AvrCheck("train_portb"), check_train_portb),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    4: [
        (AvrCheck("binary_counter"), check_binary_counter_portb),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    5: [
        (AvrCheck("timer_traffic"), check_traffic_no_delay),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    6: [
        (AvrCheck("int0_flag_traffic"), check_traffic_int0_flag),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    7: [
        (AvrCheck("timer1_timer2_isr"), check_dual_timer_isr),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    8: [
        (AvrCheck("timer0_pwm"), lambda c: check_timer0_fast_pwm_oc0a(c, False)),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    9: [
        (AvrCheck("timer0_pwm_debounce"), lambda c: check_timer0_fast_pwm_oc0a(c, True)),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    10: [
        (AvrCheck("lm35_adc_motor"), check_lm35_adc_motor),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    11: [
        (AvrCheck("servo_timer1"), check_servo_timer1_phase_pwm),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    12: [
        (AvrCheck("lcd_counter"), check_lcd_counter_button),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    13: [
        (AvrCheck("uart_pwm"), check_uart_pwm_led),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    14: [
        (AvrCheck("adc_pot_pwm"), check_adc_pot_motor_pwm),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
    15: [
        (AvrCheck("i2c_bmp_oled"), check_i2c_bmp280_oled),
        (AvrCheck("avr_headers"), check_avr_headers),
    ],
}
