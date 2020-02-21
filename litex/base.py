from migen import *
from shared.board.fpga_dev_board import Platform

from litex.build.generic_platform import *

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.uart import UARTWishboneBridge
from litex.soc.cores import dna, xadc
from litex.soc.cores.spi import SPIMaster
from litex.soc.cores.gpio import GPIOOut

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


platform = Platform()
soc = BaseSoC(platform)
builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
builder.gateware_toolchain_path=None
builder.build()
platform.create_programmer().load_bitstream("build/gateware/top.bit")