from migen import *

from shared.debouncer import Debouncer


class RotaryEncoder(Module):
    def __init__(self, sysClkFreq):
        self.i_a = Signal()
        self.i_b = Signal()
        self.o_en = Signal()
        self.o_dir = Signal()
        self.o_counter = Signal(8)

        #  #  #

        a = Signal()
        b = Signal()
        syncA = Signal(4)
        syncB = Signal(4)

        self.submodules.debouncer_a = debouncer_a = Debouncer(sysClkFreq)
        self.submodules.debouncer_b = debouncer_b = Debouncer(sysClkFreq)

        self.comb += [
            debouncer_a.i_raw.eq(self.i_a),
            debouncer_b.i_raw.eq(self.i_b),
            a.eq(debouncer_a.o_clean),
            b.eq(debouncer_b.o_clean),

            self.o_en.eq(syncA[2] ^ syncA[3] ^ syncB[2] ^ syncB[3]),
            self.o_dir.eq(syncA[2] ^ syncB[3])
        ]

        self.sync += [
            syncA.eq(Cat(a, syncA)),
            syncB.eq(Cat(b, syncB)),

            If(self.o_en,
                If(self.o_dir,
                    self.o_counter.eq(self.o_counter + 1)
                ).Else(
                    self.o_counter.eq(self.o_counter - 1)
                )
            )
        ]