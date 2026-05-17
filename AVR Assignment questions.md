
  1)  Objective: Write a program to toggle an LED connected to PORTD Pin 5 with specific timing intervals for the ON and OFF states.

Requirements: The LED must be interfaced with PORTD Pin 5. Upon system start or reset, the LED must immediately turn ON and remain in that state for exactly 3 seconds. After the ON period, the LED must turn OFF for a duration of exactly 5 seconds. The program must be designed to continuously loop this 3-second ON and 5-second OFF sequence.

   2) Objective: Write a program to toggle between a Red LED and a Green LED using a momentary push-button switch.

Requirements: The system must interface with a Red LED, a Green LED, and a push-button switch. When the switch is pressed, the program must toggle the current active LED state. If the Red LED is currently ON, it must be turned OFF while the Green LED is turned ON. Conversely, if the Green LED is currently ON, it must be turned OFF while the Red LED is turned ON. Each individual press of the switch should trigger exactly one transition between the two LEDs.

   3) Objective: Write a program to create a "train" animation where a single active LED appears to move across a series of connected GPIO pins.

Requirements: The system must control a sequence of at least eight LEDs connected to PORTB. When the program starts, only the first LED should turn ON. After a short delay, the first LED must turn OFF and the second LED must turn ON. This sequential shifting must continue until the last LED in the row is reached. Once the "train" reaches the end of the line, the pattern should immediately reset to the first LED and repeat the sequence indefinitely to create a continuous moving light effect.

  4)  Objective: Write a program that uses four LEDs to display a 4-bit binary count triggered by a switch.

Requirements: Four LEDs must be connected to PORTB (Pins 0 through 3) and a push-button must be connected to PORTD Pin 2. Every time the switch is pressed, the value displayed by the LEDs must increment by one in binary format (from 0000 to 1111). When the count reaches 15 (all LEDs ON), the next press must reset the counter back to 0. The program should use a dedicated function to update the LED states based on the current counter variable. Module 3: Timers

   5) Objective: Write a program to simulate a basic one-way traffic light controller using three LEDs to represent the Green, Orange, and Red signals without using inbuilt _delay() function.

Requirements: The system must control three LEDs connected to any three available GPIO pins on PORTB. Upon system start, the Green LED must turn ON for a duration of 10 seconds. After this period, the Green LED must turn OFF and the Orange LED must turn ON for 3 seconds. Once the Orange duration ends, it must turn OFF and the Red LED must turn ON for 10 seconds. The program must be designed to continuously cycle through this Green-Orange-Red sequence indefinitely.

                                                                               Module 3: Interrupts

   6) Objective: Write a program to manage a traffic light sequence that includes a high-priority interrupt designed to trigger a state change only after the current light cycle completes its minimum safe duration.

Requirements: The system must control three LEDs (Green, Orange, and Red) connected to PORTB. Under normal operation, the program should cycle through the Green (10s), Orange (3s), and Red (10s) states in a continuous loop. An emergency push-button must be interfaced with the External Interrupt 0 (INT0) pin. When the button is pressed, the program should set a flag within the Interrupt Service Routine (ISR) rather than jumping states immediately. The main program logic must check this flag at the end of the current light's duration. If the flag is set, the system must then prioritize the Green light for a set duration before clearing the flag and resuming the normal cycle.

  7)  Objective: Write a program that manages two independent timing tasks simultaneously using the 16-bit Timer1 and the 8-bit Timer2.

Requirements: The system must control two different LEDs. Timer1 must be configured to toggle a "Status LED" on PORTB Pin 1 exactly every 2 seconds. Simultaneously, Timer2 must be configured to toggle a "Heartbeat LED" on PORTB Pin 2 every 500 milliseconds. The program must use the Compare Match interrupt for both timers to ensure high precision. Each LED's timing logic must reside in its respective Interrupt Service Routine, allowing both sequences to run independently without interfering with each other.

                                                                                       Module 3: PWM

   8) Objective: Write a program to control the brightness of an LED or the speed of a small DC motor using the hardware PWM capability of Timer0.

Requirements: The program must initialize Timer0 in Fast PWM mode with the output directed to the OC0A pin (PORTD Pin 6). The system should start with a 25% duty cycle. A push-button connected to an input pin should be used to cycle the duty cycle through four levels: 25%, 50%, 75%, and 100% OFF. Each time the button is pressed, the program should update the Output Compare Register (OCR0A) to the next level. The transition between speeds must be handled by a dedicated function that updates the timer registers.

9.Objective: Write a program to control the brightness of an LED or the speed of a small DC motor using the hardware PWM capability of Timer0.

Requirements: The program must initialize Timer0 in Fast PWM mode with the output directed to the OC0A pin (PORTD Pin 6). The system should start with a 25% duty cycle. A push-button connected to an input pin should be used to cycle the duty cycle through four levels: 25%, 50%, 75%, and 100% OFF. Each time the button is pressed, the program should update the Output Compare Register (OCR0A) to the appropriate value corresponding to the selected duty cycle. The duty cycle sequence should repeat continuously in a loop (i.e., after 100%, it should return to 25%). The button input should be properly debounced (either via software delay or logic) to avoid multiple unintended triggers.

                                                                                         Module 3: ADC

  10)  Objective: Write a program to create an automated cooling system using an LM35 sensor and a DC motor with manual power control.

Requirements: The system must interface with an LM35 temperature sensor and a DC motor. A push-button must be used to toggle the entire system ON and OFF. When the system is ON, it should read the temperature and adjust the motor speed accordingly. At lower temperatures, the motor should run at a reduced speed, and at higher temperatures, the motor should automatically switch to a higher speed. The program logic for sensor reading, speed calculation, and motor control must be implemented using separate functions.

  11)  Write a program to control the angular position of a servo motor based on the analog input received from a potentiometer.

Requirements: The system must interface a potentiometer with ADC Channel 0 and a servo motor with the OC1A pin (PORTB Pin 1). The program must configure Timer1 in 16-bit Phase Correct PWM mode to generate the 50Hz signal required for servo operation. A dedicated function should read the 10-bit analog value from the potentiometer and map it to the corresponding pulse width required to move the servo from 0 to 180 degrees. The motor position must update in real-time as the potentiometer is turned.

                                                  Module 3: LCD (16 x 2) - Parallel Port Programming

  12)  Objective: Write a program to show a 9-digit number on an LCD screen that increases with a quick button press and resets to zero with a long press.

Requirements: The system must use a 16x2 LCD and one push-button. On the screen, the counter should start at 000000000. When you press and let go of the button quickly, the count should go up by 1. If you hold the button down for 2 seconds or more, the counter must clear and go back to 0. The program needs to use functions to check how long the button is held and to update the number on the LCD screen.

                                                                               Module 3: UART

   13) Objective: Write a program to manage an LED’s state and intensity through a serial terminal while providing real-time status updates back to the user.

Requirements: The system must use UART communication at a 9600 baud rate to receive instructions. An LED must be connected to a pin capable of hardware PWM. If the user sends the command "ON", the LED must turn on and the system should send back the message "LED is now ON". If the user sends "OFF", the LED must turn off and the system should reply with "LED is now OFF". If the user sends a number between 0 and 100, the program must adjust the LED brightness to that percentage and reply with "Brightness set to [Value]%". Student Instruction: You are responsible for selecting the most appropriate Timer (Timer0, Timer1, or Timer2) and the best PWM mode (Fast PWM or Phase Correct PWM) based on the hardware pins available and the precision required for smooth brightness control. The program must be structured using modular functions for UART communication and PWM updates.

                                                                           Module 3: SPI & I2C

  14)  Objective: Write a program to regulate the rotational speed of a DC motor by mapping an analog input signal to a Pulse Width Modulation (PWM) output.

Requirements: The system must interface a potentiometer with ADC Channel 0 and a DC motor via a motor driver connected to the OC0A pin (PORTD Pin 6). The program must configure Timer0 in Fast PWM mode to drive the motor. A dedicated function should be used to read the 10-bit analog value from the potentiometer and scale it to an 8-bit value suitable for the Output Compare Register (OCR0A). The motor speed must respond linearly to the potentiometer position, reaching maximum speed at the highest voltage input and stopping at the lowest.

  15)  Objective: Write a program to read temperature data and pressure from a BMP280 sensor and display the real-time value on an OLED screen.

Requirements: The system must use the I2C protocol to communicate with both the BMP280 sensor and a 128x64 OLED display. The program should first initialize both devices on the I2C bus. It must then read the raw temperature data from the BMP280, convert it into Celsius, and format the result as a string. Finally, the program must clear the OLED screen and display the current temperature in a readable format. The sensor reading and display updating should happen every 2 seconds.