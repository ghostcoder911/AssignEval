C Assignment Questions BASIC REFRESHER

    Write a C program that takes an integer from the user and determines whether the number is even or odd.

Description: The program should prompt the user to enter a whole number. It must then check if the number is perfectly divisible by 2. If it is, the program should display that the number is even; otherwise, it should display that the number is odd. The program should handle both positive and negative integers. Pre-requisites: Conditional Statements, Operators.

    Write a C program that asks the user to enter a number and determines whether that number is prime or not.

Description: A prime number is a natural number greater than 1 that cannot be formed by multiplying two smaller natural numbers. In simpler terms, it is a number that is only divisible by 1 and itself. Your program should take an integer as input and check if it has any divisors other than 1 and the number itself. If the user enters a number like 2, 3, or 5, the program should identify it as prime. However, if the user enters a number less than 2, or a number like 4 or 6 that can be divided by other values, the program should state it is not prime. You should use a simple loop to test for these divisors and a conditional statement to print the final result. Pre-requisites: Loops, Conditional Statements, Operators

    Write a C program that takes a positive integer from the user and calculates its factorial.

Description: The program should prompt the user to enter a single whole number. It must then calculate the factorial of that number, which is the product of all positive integers from 1 up to the number entered. The final result should be displayed clearly on the screen. The program should also account for the fact that the factorial of 0 is Pre-requisites: Operators, Data Types, Loops.

    Write a C program to generate the Fibonacci series up to a given number of terms.

Description: The program should prompt the user to enter the number of terms (n). It should then generate the Fibonacci sequence, where each number is the sum of the two preceding ones, starting from 0 and 1. The program must display the sequence up to the specified number of terms. Pre-requisites: Loops, Variables, Basic Arithmetic Operations

                                                                                      Functions

    Write a C program that uses a function to check whether a given number is a Perfect Number.

    Description: The program should prompt the user to enter a positive integer. A separate function must be written that computes the sum of all proper divisors of the number (excluding the number itself) and returns whether the sum equals the original number. The main function should display whether the number is perfect or not. (Example: 6 = 1+2+3, 28 = 1+2+4+7+14) Pre-requisites: Functions, Loops, Return Values.

    Write a C program that uses a recursive function to find the GCD of two numbers using the Euclidean algorithm.

Description: The program should prompt the user to enter two positive integers. A recursive function must be written that repeatedly applies the Euclidean method replacing the larger number with the remainder of dividing the two until the remainder is zero. The GCD should be returned to the main function and displayed on the screen. Pre-requisites: Functions, Recursion, Modulus Operator.

    Write a C program that uses a function to count the frequency of each digit (0–9) in a given integer.

Description: The program should prompt the user to enter an integer. A separate function must be written that takes the number, extracts each digit using a loop, and updates a frequency array accordingly. The function should not return a single value but instead update the array directly. The main function should then print how many times each digit appears in the number. Pre-requisites: Functions, Arrays, Loops, Pass by Reference (Pointers).

    Write a C program that uses functions to convert a decimal number to any base between 2 and 16.

Description: The program should prompt the user to enter a decimal number and a target base. A separate function must be written that performs the repeated division method, stores each remainder, and builds the result in the correct order. For bases above 9, remainders 10–15 should be represented as letters A–F. The converted value should be displayed from the main function. Pre-requisites: Functions, Loops, Arrays, Character Handling.

    Write a C program that uses functions to evaluate a simple arithmetic expression given two numbers and an operator.

Description: The program should prompt the user to enter two floating-point numbers and an arithmetic operator (+, -, *, /). A separate function must be written for each operation (add, subtract, multiply, divide). A selector function should take the operator as a parameter and call the appropriate function, returning the result to main. Division by zero must be handled gracefully inside the divide function. Pre-requisites: Functions, Switch/Conditionals, Float Arithmetic, Error Handling.

                                                                                       STRINGS

    Write a C program that takes a string of digits from the user and converts it into its equivalent integer value.

Description:The program should prompt the user to enter a number as a string (for example, "1234"). It must then process this string character by character and transform it into an actual integer variable that can be used for mathematical operations. The program should be able to handle positive numbers and display the final integer result on the screen. Pre-requisites: Loops, Strings, Operators.

    Write a C program that takes an integer from the user and converts it into a string of characters.

Description:The program should prompt the user to enter a whole number. It must then process this integer and store each of its digits as characters within a character array (string). The resulting string should represent the number exactly as it was entered, including a negative sign if the number is less than zero. Finally, the program should display the resulting string on the screen. Pre-requisites: Strings, Loops, Operators.

    Write a C program that takes a string from the user and checks whether it is a palindrome.

Description: The program should prompt the user to enter a string. It must determine if the string reads the same forward and backward. The program should then display a message to the user stating whether the input is a palindrome or not. Pre-requisites: Loops, Control Statements, Strings and Operators.

    Write a C program that takes a string from the user and reverses its characters using an iterative approach.

Description: The program should prompt the user to enter a sequence of characters. It must then swap or move the characters within the string using a loop until the entire string is reversed. The final resulting string should be displayed on the screen. Pre-requisites: Loops, Strings. Operators.

    Write a C program that takes a string input from the user and determines whether it is a pangram or not.

Description: The program should prompt the user to enter a sentence or a string of characters. It must then verify if every letter of the alphabet from A to Z appears at least once within the provided text, regardless of whether the letters are uppercase or lowercase. The final output should state if the string is a pangram. Pre-requisites: Loops, Strings, Conditional Statements, ASCII, Operators

    Write a C program that takes a string from the user and replaces every sequence of multiple consecutive spaces with a single space.

Description: The program should prompt the user to enter a sentence that may contain several spaces between words. It must then process the string to ensure that any instance where two or more blank spaces appear together is reduced to just one blank space. The final cleaned string should be displayed on the screen. Pre-requisites: Loops, Strings, Conditional Statements, ASCII, Operators

    Write a C program that takes a string from the user and converts all uppercase letters into their corresponding lowercase letters.

Description: The program should prompt the user to enter a sequence of characters. It must then check each character individually. If a character is an uppercase letter, the program should convert it to its lowercase equivalent. If the character is already lowercase or is not a letter at all, the program should leave it exactly as it is. The final modified string should be displayed on the screen. Pre-requisites: Loops, Strings, Conditional Statements, ACII.

                                                                              Bit Manipulation

    Write a C program that takes a number and toggles a specific number of bits (n) starting from a given position.

Description: The program should prompt the user to enter an integer, a starting bit position, and the number of bits to be modified. It must then change the state of those (n) consecutive bits—switching 0s to 1s and 1s to 0s—while keeping all other bits in the number exactly as they were. The final value of the number after the toggle operation should be displayed on the screen. Pre-requisites: Bitwise operators, Loops, Assignment operators.

    Write a C program that takes an integer from the user and extracts (n) bits starting from a specific bit position.

Description: The program should prompt the user to enter a number, a starting position, and the number of bits to be retrieved. It must then isolate that specific sequence of bits from the original value and display the resulting number on the screen. The other bits in the number should not affect the final output. Pre-requisites: Bitwise Operators.

    Write a C program that takes a number and replaces n of its bits, starting from a given position, with another set of n bits from a second number.

Description: The program should prompt the user to enter two integers, a starting bit position, and the number of bits n to be modified. It must then clear $n$ bits in the first number at the specified position and replace them with the corresponding $n$ bits from the second number. The final resulting value should be displayed on the screen while all other bits in the first number remain unchanged. Pre-requisites: Bitwise Operators

    Write a C program that takes two integers and swaps n bits starting from a given position in both numbers.

Description: The program should prompt the user to enter two integers, a starting bit position, and the number of bits (n) to be swapped. It must then exchange the n consecutive bits at the specified position between the two numbers — the bits from the first number go into the second, and vice versa — while all remaining bits in both numbers stay exactly as they were. Both final values should be displayed on the screen after the swap. Pre-requisites: Bitwise Operators, Loops, Assignment Operators.

                                                                                        Array

    Write a C program to remove duplicate elements from a given array.

Description: The program should prompt the user to enter the size of the array and its elements. It must then identify and remove any duplicate values, ensuring that each element appears only once in the resulting array. The program should finally display the updated array containing only unique elements. Pre-requisites: Arrays, Loops, Conditional Statements

    Write a C program that uses an array to find the second largest and second smallest element in a list of numbers.

Description: The program should prompt the user to enter the size of the array and its elements. It must then scan through the array and determine both the second largest and second smallest values without sorting the array. The program should handle duplicate values correctly — if all elements are the same, it should display an appropriate message. Both results should be displayed on the screen. Pre-requisites: Arrays, Loops, Conditional Statements.

    Write a C program that rotates the elements of an array by n positions in a specified direction.

Description: The program should prompt the user to enter the array elements, the number of positions (n) to rotate, and the direction (left or right). It must then shift the elements accordingly — elements that fall off one end should reappear at the opposite end. The rotation must work for any value of n, including values larger than the array size. The final rotated array should be displayed on the screen. Pre-requisites: Arrays, Loops, Modulus Operator.

    Write a C program that merges two sorted arrays into a single sorted array without using any sorting function.

Description: The program should prompt the user to enter the sizes and elements of two arrays, each already sorted in ascending order. It must then merge them into a third array by comparing elements from both arrays one by one and placing the smaller element first, continuing until all elements are placed. The final merged sorted array should be displayed on the screen. Pre-requisites: Arrays, Loops, Multiple Array Handling.

    Write a C program that finds all pairs of elements in an array whose sum equals a given target value.

Description: The program should prompt the user to enter the size of the array, its elements, and a target sum. It must then examine all possible pairs of elements in the array and identify every pair whose sum matches the target. Each valid pair should be printed on the screen. If no such pair exists, an appropriate message should be displayed. The same element should not be paired with itself. Pre-requisites: Arrays, Nested Loops, Conditional Statements.

    Write a C program that rearranges an array such that all negative numbers appear before all positive numbers while preserving the relative order of both groups.

Description: The program should prompt the user to enter the size of the array and its elements (a mix of positive and negative integers). It must then rearrange the elements so that all negative numbers come first, followed by all positive numbers, without changing the order in which the negatives appear among themselves or the positives among themselves. Zero can be treated as positive. The rearranged array should be displayed on the screen. Pre-requisites: Arrays, Loops, Temporary Storage, Order Preservation Logic.

                                                                                      Structure

    Define a structure Complex with real and imaginary parts. Write a C program to add two complex numbers and display the result.

Description: The program should define a structure to represent a complex number with two members: real part and imaginary part. It must then create functions to perform addition of two complex numbers and to display a complex number in a readable format (e.g., a + bi). The program should take input for two complex numbers, compute their sum using the defined function, and print the result. Pre-requisites: Structures, Functions, Basic Arithmetic Operations, Input/Output