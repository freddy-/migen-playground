from migen import *
from shared.rotary_encoder import RotaryEncoder as _RotaryEncoder
from litex.soc.interconnect.csr import AutoCSR, CSRStatus

class RotaryEncoder(Module, AutoCSR):
    def __init__(self, sys_clk_freq, pins):
        self.value = CSRStatus(8)

        self.submodules.encoder = _RotaryEncoder(sys_clk_freq)

        self.comb += [
            self.encoder.i_a.eq(pins.a),
            self.encoder.i_b.eq(pins.b)
        ]

        self.sync += self.value.status.eq(self.encoder.o_counter)
