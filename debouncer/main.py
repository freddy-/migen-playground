from migen import *
from shared.board.fpga_dev_board import Platform

simulation = True

class ClockDiv(Module):
    def __init__(self, countUntil=294980):
        self.o_clk = Signal()

        counter = Signal(max=countUntil)

        self.sync += [
            If(counter == countUntil,
                counter.eq(0),
                self.o_clk.eq(1)
            ).Else(
                counter.eq(counter + 1),
                self.o_clk.eq(0)
            )
        ]

class Debouncer(Module):
    def __init__(self):
        self.i_raw = Signal()
        self.o_clean = Signal()

        debouncedOutput = Signal()
        counter = Signal(8)

        if (simulation):
            self.submodules.clkDivider = ClockDiv(countUntil=5)
        else:
            self.submodules.clkDivider = ClockDiv()

        self.comb += self.o_clean.eq(debouncedOutput)

        self.sync += [
            If(self.clkDivider.o_clk,
                counter.eq(Cat(~self.i_raw, counter[:-1]))
            ),

            If(counter == 0xFF,
                debouncedOutput.eq(1)
            ).Elif(counter == 0x00,
                debouncedOutput.eq(0)
            ).Else(
                debouncedOutput.eq(debouncedOutput)
            )
        ]
        

class LedToggler(Module):
    def __init__(self, i_toggle, o_led):
        ledState = Signal()
        prevDebouncedOutput = Signal()
        debouncedOutput = Signal()

        self.submodules.debouncer = Debouncer()

        self.comb += [
            o_led.eq(ledState),
            self.debouncer.i_raw.eq(i_toggle),
            debouncedOutput.eq(self.debouncer.o_clean)
        ]

        self.sync += [
            If(prevDebouncedOutput != debouncedOutput,
                prevDebouncedOutput.eq(debouncedOutput),
                
                If(debouncedOutput == 1,
                    ledState.eq(~ledState)
                )
            )
        ]


class Main(Module):
    def __init__(self, platform):
        buttons = platform.request("buttons")
        green_led = green_led = platform.request("green_led")
        orange_led = orange_led = platform.request("orange_led")

        self.submodules += [
            LedToggler(buttons[0], green_led),
            LedToggler(buttons[1], orange_led),
        ]


def delay(clks):
    for i in range(clks):
        yield

def debouncerGenerator(dut):
    yield dut.i_raw.eq(1)
    yield from delay(10)
    yield dut.i_raw.eq(0)
    yield from delay(70)
    yield dut.i_raw.eq(1)
    yield from delay(100)

def ledTogglerGenerator(dut, i_toggle, o_led):
    yield i_toggle.eq(1)
    yield from delay(10)
    yield i_toggle.eq(0)
    yield from delay(50)
    yield i_toggle.eq(1)
    yield from delay(100)
    yield i_toggle.eq(0)
    yield from delay(50)
    yield i_toggle.eq(1)
    yield from delay(100)
    

if __name__ == "__main__":
    import sys

    if sys.argv[1] == "sim-cdiv":
        dut = ClockDiv(countUntil=5)
        run_simulation(dut, delay(100), vcd_name="test.vcd")

    if sys.argv[1] == "sim-deb":
        dut = Debouncer()
        run_simulation(dut, debouncerGenerator(dut), vcd_name="test.vcd")

    if sys.argv[1] == "sim-lt":
        i_toggle = Signal()
        o_led = Signal()
        dut = LedToggler(i_toggle, o_led)
        run_simulation(dut, ledTogglerGenerator(dut, i_toggle, o_led), vcd_name="test.vcd")
    
    else:
        simulation = False
        platform = Platform()
        platform.build(Main(platform))
        platform.create_programmer().load_bitstream("build/top.bit")
