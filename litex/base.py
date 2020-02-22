from migen import *
from shared.board.fpga_dev_board import Platform
from shared.seven_segment import SevenSegmentDisplay as _SevenSegmentDisplay

from litex.build.generic_platform import *

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.uart import UARTWishboneBridge
from litex.soc.cores import dna, xadc
from litex.soc.cores.spi import SPIMaster
from litex.soc.cores.gpio import GPIOOut
from litex.soc.interconnect.csr import *

# Create our soc (fpga description)
class BaseSoC(SoCMini):
    def __init__(self, platform, **kwargs):
        sys_clk_freq = int(29.498e6)

        # SoCMini (No CPU, we are controlling the SoC over UART)
        SoCMini.__init__(self, platform, sys_clk_freq, csr_data_width=32,
            ident="My first LiteX System On Chip", ident_version=True)

        # Clock Reset Generation
        self.submodules.crg = CRG(platform.request("clk29"))

        # No CPU, use Serial to control Wishbone bus
        self.submodules.serial_bridge = UARTWishboneBridge(platform.request("uart"), sys_clk_freq)
        self.add_wb_master(self.serial_bridge.wishbone)

        # FPGA identification
        self.submodules.dna = dna.DNA()
        self.add_csr("dna")

        # Led
        self.submodules.led = GPIOOut(Cat([
            platform.request("green_led"),
            platform.request("orange_led")
        ]))
        self.add_csr("led")

        # Display 7 Segments
        display = platform.request("seven_seg")
        self.submodules.display7Seg = SevenSegmentDisplay(sys_clk_freq)
        self.add_csr("display7Seg")
        self.comb += [
            display.digits.eq(~self.display7Seg.o_digits),
            display.segments.eq(~self.display7Seg.o_segments)
        ]


class SevenSegmentDisplay(Module, AutoCSR):
    def __init__(self, sys_clk_freq):
        self.value = CSRStorage(16)

        self.o_digits = Signal(4)
        self.o_segments = Signal(8)

        self.submodules.display = _SevenSegmentDisplay(sys_clk_freq)
        self.comb += [
            self.o_digits.eq(self.display.o_digits),
            self.o_segments.eq(self.display.o_segments),
        ]

        self.sync += [
            If(self.value.re,
                self.display.i_value.eq(self.value.storage)
            )
        ]


platform = Platform()
soc = BaseSoC(platform)
builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
builder.gateware_toolchain_path=None
builder.build()
platform.create_programmer().load_bitstream("build/gateware/top.bit")