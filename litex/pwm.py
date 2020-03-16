from migen import *
from shared.pwm import PWM as _PWM
from litex.soc.interconnect.csr import AutoCSR, CSRStorage

class PWM(Module, AutoCSR):
    def __init__(self, sys_clk_freq, o_pwm):
        self.duty  = CSRStorage(8)
        self.enable  = CSRStorage()

        self.submodules.pwm = _PWM(sys_clk_freq)

        self.comb += o_pwm.eq(self.pwm.o_pwm)

        self.sync += [
            self.pwm.i_duty.eq(self.duty.storage),
            self.pwm.i_enable.eq(self.enable.storage)
        ]
