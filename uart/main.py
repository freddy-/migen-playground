from migen import *
from migen.genlib.cdc import MultiReg
from shared.board.fpga_dev_board import Platform
from shared.clkdiv import ClkDiv
from shared.utils import delay


BAUD_RATE = 115200


class UartRX(Module):
    def __init__(self, sysClkFreq):
        self.i_rx = Signal(reset=1)
        self.o_data = Signal(8)
        self.o_stb = Signal()

        #  #  #

        baudCounter = Signal(max=5)
        bitCounter = Signal(max=10)
        buffer = Signal(8)
        rx = Signal(reset=1)

        self.specials += MultiReg(self.i_rx, rx, reset=1)
        self.submodules.clkDiv = clkDiv = ClkDiv(sysClkFreq, targetFreq=BAUD_RATE * 2)

        self.sync += [
            If(clkDiv.o_clk,
                baudCounter.eq(baudCounter + 1)
            )
        ]

        self.submodules.rx_fsm = FSM(reset_state="IDLE")
        self.rx_fsm.act("IDLE",
            NextValue(self.o_stb, 0),
            If(~rx,
                NextValue(clkDiv.i_enable, 1),
                NextState("WAIT_HALF_BAUD")
            )
        )
        self.rx_fsm.act("WAIT_HALF_BAUD",
            If(clkDiv.o_clk,
                NextValue(baudCounter, 0),
                NextState("READ")
            )
        )
        self.rx_fsm.act("READ",
            If(baudCounter == 2,
                If(bitCounter < 8,
                    NextValue(buffer, Cat(buffer[1:], rx)),
                    NextValue(bitCounter, bitCounter + 1),
                    NextValue(baudCounter, 0)
                ).Else(
                    NextState("FINISH")
                )
            )
        )
        self.rx_fsm.act("FINISH",
            If(clkDiv.o_clk,
                NextValue(self.o_stb, 1),
                NextValue(self.o_data, buffer),
                NextValue(bitCounter, 0),
                NextValue(baudCounter, 0),
                NextValue(clkDiv.i_enable, 0),
                NextState("IDLE")
            )
        )


class UartTX(Module):
    def __init__(self, sysClkFreq):
        self.i_wr = Signal()
        self.i_data = Signal(8)
        self.o_busy = Signal()
        self.o_tx = Signal(reset=1)

        #  #  #

        busy = Signal()
        register = Signal(8)
        shiftCounter = Signal(4)

        self.submodules.clkDiv = clkDiv = ClkDiv(sysClkFreq, targetFreq=BAUD_RATE)

        self.comb += self.o_busy.eq(busy)

        self.submodules.rx_fsm = FSM(reset_state="IDLE")
        self.rx_fsm.act("IDLE",
            If((self.i_wr) & (~busy),
                NextValue(register, self.i_data),
                NextValue(busy, 1),
                NextValue(clkDiv.i_enable, 1),
                NextValue(self.o_tx, 0),
                NextState("SEND_DATA")
            )
        )
        self.rx_fsm.act("SEND_DATA",
            If(clkDiv.o_clk,
                If(shiftCounter < 8,
                    NextValue(register, register >> 1),
                    NextValue(self.o_tx, register[0]),
                    NextValue(shiftCounter, shiftCounter + 1)
                ).Else(
                    NextValue(self.o_tx, 1),
                    NextState("FINISH")
                )
            )
        )
        self.rx_fsm.act("FINISH",
            If(clkDiv.o_clk,
                NextValue(busy, 0),
                NextValue(shiftCounter, 0),
                NextValue(clkDiv.i_enable, 0),
                NextState("IDLE")
            )
        )


class UartLed(Module):
    def __init__(self, sysClkFreq):
        self.i_signal = Signal(reset=1)
        self.o_led = Signal()

        #  #  #

        self.submodules.clkDiv = clkDiv = ClkDiv(sysClkFreq, targetFreq=100)

        self.sync += [
            If(~self.i_signal,
                self.o_led.eq(1),
                clkDiv.i_enable.eq(1)
            ),

            If(clkDiv.o_clk,
                self.o_led.eq(0),
                clkDiv.i_enable.eq(0)    
            )
        ]


class Main(Module):
    def __init__(self, platform):
        sysClkFreq = platform.clkFreq

        uart = platform.request("uart")
        self.o_tx = uart.tx
        self.i_rx = uart.rx

        self.o_txLed = platform.request("green_led")
        self.o_rxLed = platform.request("orange_led")

        #  #  #

        self.submodules.uartTx = uartTx = UartTX(sysClkFreq)
        self.submodules.uartRx = uartRx = UartRX(sysClkFreq)

        self.submodules.txLed = txLed = UartLed(sysClkFreq)
        self.submodules.rxLed = rxLed = UartLed(sysClkFreq)

        self.submodules.oneSecTimer = oneSecTimer = ClkDiv(sysClkFreq, targetFreq=1)

        self.comb += [
            self.o_tx.eq(uartTx.o_tx),
            uartRx.i_rx.eq(self.i_rx),

            self.o_txLed.eq(txLed.o_led),
            self.o_rxLed.eq(rxLed.o_led),

            txLed.i_signal.eq(uartTx.o_tx),
            rxLed.i_signal.eq(self.i_rx)
        ]

        buffer = Signal(8)

        self.submodules.rx_fsm = FSM(reset_state="IDLE")
        self.rx_fsm.act("IDLE",
            If(uartRx.o_stb,
                NextValue(oneSecTimer.i_enable, 1),
                NextValue(buffer, uartRx.o_data),
                NextState("WAIT")
            )
        )
        self.rx_fsm.act("WAIT",
            If(oneSecTimer.o_clk,
                NextValue(oneSecTimer.i_enable, 0),
                NextValue(uartTx.i_data, buffer),
                NextValue(uartTx.i_wr, 1),
                NextState("START_SEND")
            )
        )
        self.rx_fsm.act("START_SEND",
            NextValue(uartTx.i_wr, 0),
            NextState("SENDING")
        )
        self.rx_fsm.act("SENDING",
            If(~uartTx.o_busy,
                NextState("IDLE")
            )
        )


def rxGenerator(dut):
    yield from delay(10)
    yield dut.i_rx.eq(0)
    yield from delay(10)
    yield dut.i_rx.eq(1)
    yield from delay(100)

def txGenerator(dut):
    yield from delay(10)
    yield dut.i_data.eq(0b00001111)
    yield dut.i_wr.eq(1)
    yield from delay(1)
    yield dut.i_wr.eq(0)
    yield from delay(100)

def uartLedGenerator(dut):
    yield dut.i_signal.eq(1)
    yield from delay(5)
    yield dut.i_signal.eq(0)
    yield
    yield dut.i_signal.eq(1)
    yield from delay(100)


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "sim-rx":
        dut = UartRX(sysClkFreq=1)
        run_simulation(dut, rxGenerator(dut), vcd_name="test.vcd")

    if sys.argv[1] == "sim-tx":
        dut = UartTX(sysClkFreq=BAUD_RATE * 4)
        run_simulation(dut, txGenerator(dut), vcd_name="test.vcd")

    if sys.argv[1] == "sim-led":
        dut = UartLed(sysClkFreq=1)
        run_simulation(dut, uartLedGenerator(dut), vcd_name="test.vcd")

    else:
        platform = Platform()
        platform.build(Main(platform))
        platform.create_programmer().load_bitstream("build/top.bit")

