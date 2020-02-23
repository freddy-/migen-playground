from migen import *
from shared.board.fpga_dev_board import Platform
from rotary_encoder import RotaryEncoder
from seven_segment import SevenSegmentDisplay

from litex.build.generic_platform import *

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.uart import UARTWishboneBridge
from litex.soc.cores import dna, xadc
from litex.soc.cores.spi import SPIMaster
from litex.soc.cores.gpio import GPIOOut
from litex.soc.interconnect.csr import *


# Create our soc (fpga description)
class UartBaseSoC(SoCMini):
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


class CpuSoC(SoCMini):
    def __init__(self, platform, **kwargs):
        sys_clk_freq = platform.clkFreq

        # SoC with CPU
        SoCCore.__init__(self, platform,
            cpu_type                 = "vexriscv",
            clk_freq                 = sys_clk_freq,
            ident                    = "LiteX CPU Test SoC", ident_version=True,
            integrated_rom_size      = 0x4000,
            integrated_main_ram_size = 0x2000,
            uart_name                = "uart")

        # Clock Reset Generation
        self.submodules.crg = CRG(platform.request("clk29"), ~platform.request("buttons")[3])

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


platform = Platform()
soc = CpuSoC(platform)
builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
builder.gateware_toolchain_path=None
builder.build()
platform.create_programmer().load_bitstream("build/gateware/top.bit")