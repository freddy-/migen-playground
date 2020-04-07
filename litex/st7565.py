from migen import *
from litex.soc.interconnect.csr import AutoCSR, CSRStorage
from litex.soc.cores.spi import SPIMaster
from litex.soc.cores.gpio import GPIOOut

class St7565Display(Module, AutoCSR):
    def __init__(self, sys_clk_freq, pins):
        self.submodules.dc        = GPIOOut(pins.dc)
        self.submodules.backligth = GPIOOut(pins.bl_led)
        self.submodules.reset     = GPIOOut(pins.reset)

        pins.miso = Signal()

        self.submodules.spi = SPIMaster(
            pads         = pins,
            data_width   = 8,
            sys_clk_freq = sys_clk_freq,
            spi_clk_freq = 4e6,
        )

