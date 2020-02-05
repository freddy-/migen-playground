from migen.build.generic_platform import *
from migen.build.xilinx import XilinxPlatform
from migen.build.xilinx.programmer import FpgaProg


_io = [
    ("green_led", 0, Pins("P82"), IOStandard("LVCMOS33"), Drive(24), Misc("SLEW=QUIETIO")),
    ("orange_led", 0, Pins("P81"), IOStandard("LVCMOS33"), Drive(24), Misc("SLEW=QUIETIO")),

    ("buttons", 0, Pins("P97 P99 P101 P104"), IOStandard("LVCMOS33")),

    ("clk29", 0, Pins("P55"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("P93"), IOStandard("LVCMOS33"), Misc("SLEW=SLOW")),
        Subsignal("rx", Pins("P87"), IOStandard("LVCMOS33"), Misc("PULLUP"))
    ),

    ("spiflash", 0,
        Subsignal("cs_n", Pins("P38")),
        Subsignal("clk", Pins("P70")),
        Subsignal("mosi", Pins("P64")),
        Subsignal("miso", Pins("P65"), Misc("PULLUP")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    ),
]

_connectors = []

# http://blog.lambdaconcept.com/doku.php?id=migen:migen_platform
class Platform(XilinxPlatform):

    # 29.498MHZ
    default_clk_name = "clk29"
    default_clk_period = 29.498

    def __init__(self):
        XilinxPlatform.__init__(self, "xc6slx9-tqg144-2", _io, _connectors)

    def create_programmer(self):
        return FpgaProg(flash_proxy_basename="bscan_spi_lx9.bit")