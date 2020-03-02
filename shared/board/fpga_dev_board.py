from migen.build.generic_platform import *
from migen.build.xilinx import XilinxPlatform
from migen.build.xilinx.programmer import FpgaProg


_io = [
    ("green_led", 0, Pins("P82"), IOStandard("LVCMOS33"), Drive(24), Misc("SLEW=QUIETIO")),
    ("orange_led", 0, Pins("P81"), IOStandard("LVCMOS33"), Drive(24), Misc("SLEW=QUIETIO")),

    ("buttons", 0, Pins("P97 P99 P101 P104"), IOStandard("LVCMOS33")),

    ("encoder", 0,
        Subsignal("a", Pins("P134"), IOStandard("LVCMOS33"), Misc("SLEW=SLOW")),
        Subsignal("b", Pins("P133"), IOStandard("LVCMOS33"), Misc("SLEW=SLOW"))
    ),

    ("clk29", 0, Pins("P55"), IOStandard("LVCMOS33")),

    ("uart", 0,
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

    ("seven_seg", 0,
        Subsignal("digits", Pins("P118 P117 P115 P112"), IOStandard("LVCMOS33"), Misc("SLEW=SLOW")),
        Subsignal("segments", Pins("P88 P114 P116 P111 P105 P102 P100 P98"), IOStandard("LVCMOS33"), Misc("SLEW=SLOW"))
    ),

    ("spi_display", 0,
        Subsignal("bl_led", Pins("P120")),
        Subsignal("blue_led", Pins("P119")),
        Subsignal("reset", Pins("P126")),
        Subsignal("dc", Pins("P124")),
        Subsignal("cs_n", Pins("P131")),
        Subsignal("clk", Pins("P123")),
        Subsignal("mosi", Pins("P121")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    ),
]




_connectors = []

# http://blog.lambdaconcept.com/doku.php?id=migen:migen_platform
class Platform(XilinxPlatform):

    # 29.498MHZ
    default_clk_name = "clk29"
    default_clk_period = 29.498
    clkFreq = (int) (default_clk_period * 1000000)

    def __init__(self):
        XilinxPlatform.__init__(self, "xc6slx9-tqg144-2", _io, _connectors)

    def create_programmer(self):
        return FpgaProg(flash_proxy_basename="bscan_spi_lx9.bit")