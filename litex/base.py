from migen import *
from shared.board.fpga_dev_board import Platform
from shared.seven_segment import SevenSegmentDisplay as _SevenSegmentDisplay
from shared.rotary_encoder import RotaryEncoder as _RotaryEncoder

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
        sys_clk_freq = platform.clkFreq

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
        self.submodules.display7Seg = SevenSegmentDisplay(sys_clk_freq, platform.request("seven_seg"))
        self.add_csr("display7Seg")

        # Encoder
        self.submodules.encoder = RotaryEncoder(sys_clk_freq, platform.request("encoder"))
        self.add_csr("encoder")


class SevenSegmentDisplay(Module, AutoCSR):
    def __init__(self, sys_clk_freq, displayPins):
        self.value = CSRStorage(16)

        self.submodules.display = _SevenSegmentDisplay(sys_clk_freq)

        self.comb += [
            displayPins.digits.eq(~self.display.o_digits),
            displayPins.segments.eq(~self.display.o_segments)
        ]

        self.sync += [
            If(self.value.re,
                self.display.i_value.eq(self.value.storage)
            )
        ]


class RotaryEncoder(Module, AutoCSR):
    def __init__(self, sys_clk_freq, pins):
        self.value = CSRStatus(8)

        self.submodules.encoder = _RotaryEncoder(sys_clk_freq)

        self.comb += [
            self.encoder.i_a.eq(pins.a),
            self.encoder.i_b.eq(pins.b)
        ]

        self.sync += self.value.status.eq(self.encoder.o_counter)


platform = Platform()
soc = BaseSoC(platform)
builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
builder.gateware_toolchain_path=None
builder.build()
platform.create_programmer().load_bitstream("build/gateware/top.bit")