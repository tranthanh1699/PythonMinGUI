## GUI For Microcontroller Interconnect Network protocol

This MIN repository includes the specification, a standard C API and
reference implementations for C and Python. See the Wiki for further
details:

http://github.com/min-protocol/min/wiki

To build .exe file
run command python -m PyInstaller --onefile --windowed --icon=icon.ico MinTool.py

File structure:

    target/	                Embedded code
        min.c               MIN code designed to run on an embedded system (from 8-bit MCUs upwards)
        min.h               Header file that defines the API to min
	    sketch_example1     Arduino sketch for an example program
    host/                   Python code to run on a host PC
        min.py              MIN 2.0 reference implementation with support for MIN via Pyserial
	    listen.py           Example program to run on a host and talk to an Arduino board

There is also a Rust implementation of MIN for both host and target:

https://github.com/qianchenzhumeng/min-rs

This is the GUI for window through UART protocol for easy sending MIN frame to Microcontroller

To build .exe file:
    run command: python -m PyInstaller --onefile --windowed --icon=icon.ico MinTool.py