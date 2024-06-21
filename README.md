[![Lint Python](https://github.com/atao/rtl_tracking/actions/workflows/main.yml/badge.svg)](https://github.com/atao/rtl_tracking/actions/workflows/main.yml)
# rtl_tracking

The idea behind this project is to save the detections of [rtl_433](https://github.com/merbanan/rtl_433/) in a database.

You will need an SDR device to use this program.

For example, you can track TPMS from cars arround you.

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
rtl_433 -F json | python3 rtl_tracking.py >> output.log
```

Just pipe json file :
```bash
cat my_json_file | python3 rtl_tracking.py
```

You can filter findings from rtl_sdr with **-R** option

See list on [rtl_433](https://github.com/merbanan/rtl_433?tab=readme-ov-file#running)
