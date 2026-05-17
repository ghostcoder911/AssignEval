"""Parse AVR bare-metal assignment questions."""

from __future__ import annotations

import re
from pathlib import Path

from assigneval.questions import Question

_MODULE_MARKERS = {
    "Timers": "timers",
    "Interrupts": "interrupts",
    "PWM": "pwm",
    "ADC": "adc",
    "LCD": "lcd",
    "UART": "uart",
    "SPI": "spi",
    "I2C": "i2c",
}


def _keywords_for(text: str) -> tuple[str, ...]:
    low = text.lower()
    pools = [
        ["portd", "pd5", "led", "3 second", "5 second"],
        ["red", "green", "button", "toggle", "switch"],
        ["train", "portb", "sequential", "shift"],
        ["binary", "counter", "portb", "portd", "0000", "1111"],
        ["traffic", "green", "orange", "red", "timer"],
        ["interrupt", "int0", "emergency", "flag", "isr"],
        ["timer1", "timer2", "compare", "heartbeat", "2 second", "500"],
        ["timer0", "pwm", "ocr0a", "duty", "oc0a"],
        ["timer0", "pwm", "debounc", "duty", "25%"],
        ["lm35", "adc", "motor", "temperature"],
        ["servo", "potentiometer", "timer1", "phase correct", "oc1a"],
        ["lcd", "counter", "long press", "short press"],
        ["uart", "9600", "brightness", "serial"],
        ["potentiometer", "adc", "timer0", "pwm", "motor"],
        ["bmp280", "i2c", "oled", "temperature", "twi"],
    ]
    for pool in pools:
        if sum(1 for w in pool if w in low) >= 2:
            return tuple(pool)
    words = re.findall(r"[a-z0-9]{4,}", low)
    return tuple(words[:8])


def parse_avr_questions(source: Path | str) -> list[Question]:
    from assigneval.pdf_text import load_document_text

    text = source if isinstance(source, str) else load_document_text(Path(source))
    parts = re.split(r"(?m)^\s*(\d{1,2})[\.\)]\s*", text)
    if len(parts) < 3:
        return []

    questions: list[Question] = []
    category = ""

    i = 1
    while i + 1 < len(parts):
        num_str, body = parts[i], parts[i + 1]
        try:
            num = int(num_str)
        except ValueError:
            i += 2
            continue

        if num < 1 or num > 15:
            i += 2
            continue

        for marker, cat in _MODULE_MARKERS.items():
            if marker.lower() in body[:250].lower():
                category = cat
                break

        obj_m = re.search(
            r"(?:Objective:\s*)?(.+?)(?=Requirements:)",
            body,
            re.DOTALL | re.I,
        )
        req_m = re.search(r"Requirements:\s*(.+)", body, re.DOTALL | re.I)
        objective = " ".join(obj_m.group(1).split()) if obj_m else ""
        requirements = " ".join(req_m.group(1).split()) if req_m else body.strip()
        title = (objective or requirements or f"AVR Assignment {num}")[:200]
        description = f"{objective} {requirements}".strip()

        questions.append(
            Question(
                number=num,
                title=title,
                description=description,
                keywords=_keywords_for(description),
                category=category,
            )
        )
        i += 2

    # Deduplicate by number (keep first)
    by_num: dict[int, Question] = {}
    for q in questions:
        if q.number not in by_num:
            by_num[q.number] = q
    return [by_num[n] for n in sorted(by_num)]


def default_avr_questions_path() -> Path:
    from assigneval.question_paths import resolve_questions_path

    return resolve_questions_path("avr")
