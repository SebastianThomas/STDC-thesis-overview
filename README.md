# Linear-Exponential Algorithm-based Open Source Dive Computer

## Cloning this repository

To ensure all submodules are available locally, use the following command to 
check out the files: 

```bash
git clone --recurse-submodules git@git.ee.ethz.ch:pbl/FS2026/sebastian_thomas_653.git
```

## File Structure

```bash
.
├── 01_report
├── 02_presentation
├── KiCad
├── STDC_C
├── STDC-Ordering
├── STDC-Ordering.zip
├── STDC-STM32-rs
├── STDC-thalmann
└── README.md
```

## The `STDC-STM32-rs` project

This is the embedded firmware implementation, it is the module required to 
reproduce the experimental results, and to run the firmware on the PCB. 

### Setup environment

1. [Install Rust](https://rust-lang.org/tools/install/)
2. [Install just](https://just.systems/man/en/installation.html)
3. Add target for the embedded STM32 environment: `rustup target add thumbv7em-none-eabihf`

### Running code

It contains a `DEBUGGING.md` file with all the necessary information to debug
an application on the PCB and reproduce simulation results.

A `Justfile` is provided for convenience, it contains all required commands for
simulation, embedding, testing, CI, compiling and checking (without compiling).

It is recommended to use a STM32L476Rxx chip, as this is what the code is
tested on. Power it using a 3.7V fixed DC power supply. Attach the STLink V3
to the computer and debug JTAG pads exposed next to the MCU on the PCB, and 
run any `just` recipe that embeds software onto the MCU. After flashing, a 
terminal window will popup on top of the current session.

