from migen import *
from shared.board.fpga_dev_board import Platform
from rotary_encoder import RotaryEncoder
from seven_segment import SevenSegmentDisplay
from st7565 import St7565Display
from pwm import PWM

from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.generic_platform import *

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.uart import UARTWishboneBridge
from litex.soc.cores import dna, xadc
from litex.soc.cores.spi import SPIMaster
from litex.soc.cores.gpio import GPIOOut
from litex.soc.interconnect.csr import *

import litex.soc.doc as lxsocdoc

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()

        self.reset = Signal()

        #  #  #

        # Input clock
        clk29_freq = platform.clkFreq
        clk29      = platform.request("clk29")
        clk29b     = Signal()
        self.specials += Instance("BUFIO2",
            p_DIVIDE=1, p_DIVIDE_BYPASS="TRUE",
            p_I_INVERT="FALSE",
            i_I=clk29, o_DIVCLK=clk29b)

        # PLL
        pll_lckd  = Signal()
        pll_fb    = Signal()
        pll_sys   = Signal()

        self.specials.pll = Instance(
            "PLL_ADV",
            name                 = "crg_pll_adv",
            p_SIM_DEVICE         = "SPARTAN6", 
            p_BANDWIDTH          = "OPTIMIZED", 
            p_COMPENSATION       = "SYSTEM_SYNCHRONOUS",
            p_REF_JITTER         = .01,
            p_DIVCLK_DIVIDE      = 1,
            i_DADDR              = 0, 
            i_DCLK               = 0, 
            i_DEN                = 0, 
            i_DI                 = 0, 
            i_DWE                = 0, 
            i_RST                = 0, 
            i_REL                = 0,

            # Input Clocks (29.498 MHz)
            i_CLKIN1             = clk29b,
            p_CLKIN1_PERIOD      = 33.9,
            i_CLKIN2             = 0,
            p_CLKIN2_PERIOD      = 0.,
            i_CLKINSEL           = 1,

            # Feedback
            i_CLKFBIN            = pll_fb, 
            o_CLKFBOUT           = pll_fb, 
            o_LOCKED             = pll_lckd,
            p_CLK_FEEDBACK       = "CLKFBOUT",
            p_CLKFBOUT_MULT      = 17, 
            p_CLKFBOUT_PHASE     = 0.,

            # (100.295 MHz)
            o_CLKOUT0            = pll_sys, 
            p_CLKOUT0_DUTY_CYCLE = .5,
            p_CLKOUT0_PHASE      = 0., 
            p_CLKOUT0_DIVIDE     = 5,
        )

        # Power on reset
        reset = ~platform.request("buttons")[3] | self.reset
        self.clock_domains.cd_por = ClockDomain()
        por = Signal(max=1 << 11, reset=(1 << 11) - 1)
        self.sync.por += If(por != 0, por.eq(por - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, reset)

        # System clock
        self.specials += Instance("BUFG", i_I=pll_sys, o_O=self.cd_sys.clk)
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll_lckd | (por > 0))


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
        sys_clk_freq = 100.295 * 1000000

        # SoC with CPU
        SoCCore.__init__(self, platform,
            cpu_type                 = "vexriscv",
            clk_freq                 = sys_clk_freq,
            ident                    = "LiteX CPU Test SoC", ident_version=True,
            integrated_rom_size      = 0x4000,
            #integrated_rom_init      = get_mem_data("/home/freddy/projetos/migen-playground/litex/firmware/firmware.bin", "little"),
            integrated_main_ram_size = 0x2000,
            uart_name                = "uart")

        # Clock Reset Generation
        self.submodules.crg = _CRG(platform, sys_clk_freq)
        self.platform.add_period_constraint(self.crg.cd_sys.clk, 1e9/sys_clk_freq)

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

        # ST7565 Display
        # TODO usar o modulo spi.py do LiteX para controlar o display pela CPU
        displayPins = platform.request("spi_display")
        self.submodules.display = St7565Display(sys_clk_freq, displayPins)
        self.add_csr("display")

        # PWM
        #self.submodules.pwm = PWM(sys_clk_freq, displayPins.blue_led)
        #self.add_csr("pwm")


platform = Platform()
soc = CpuSoC(platform)
#soc.do_finalize()
builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
builder.gateware_toolchain_path=None
#builder.build()
platform.create_programmer().load_bitstream("build/gateware/top.bit")


#lxsocdoc.generate_docs(
#    soc,
#    builder.output_dir + "/documentation",
#    project_name="DIY FPGA Dev Board", 
#    author="Freddy")