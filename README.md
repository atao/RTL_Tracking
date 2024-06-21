# rtl_tracking

The idea behind this project is to save the detections of [rtl_433](https://github.com/merbanan/rtl_433/) in a database.

You will need an SDR device to use this program.

--

For example, this program enabled me to learn how to retrieve data stream **sdout** and reuse into a python script.
So this project can be reused for other things !


## Usage

Simple way :
```bash
rtl_433 -F json | python3 rtl_tracking.py
```
With log :
```bash
rtl_433 -F json | python3 rtl_tracking.py
```