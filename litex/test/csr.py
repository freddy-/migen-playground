from migen import *
from litex.soc.interconnect.csr import *

class Main(Module):
    def __init__(self):
        self.control = CSRStorage(name="teste", fields=[
                CSRField("start",  size=1, offset=0, pulse=True),
                CSRField("length", size=8, offset=8)])
        
        self.st = Signal()
        self.le = Signal(8)

        self.comb += [
            self.st.eq(self.control.fields.start),
            self.le.eq(self.control.fields.length)
        ]


def generator(dut):
    yield dut.control.storage.eq(0xFFFF)
    yield
    yield

if __name__ == "__main__":
    dut = Main()
    run_simulation(dut, generator(dut), vcd_name="test.vcd")