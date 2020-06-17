"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.memory = [0] * 256
        self.registers = [0] * 8
        self.SP = 7
        self.registers[self.SP] = 0xf4  # initialize the SP
        self.PC = 0
        self.IR = 0
        self.MAR = 0
        self.MDR = 0
        self.flags = 0b00000000

    def load(self, file=None):
        """Load a program into memory."""

        address = 0

        # go back to fix this.
        if len(sys.argv) > 1:
            file = sys.argv[1]
            with open(file, 'r') as p:
                program = [line.split()[0] for line in p if len(
                    line.split()) > 0 and line.split()[0] != '#']
        else:
            program = [
                # From print8.ls8
                0b10000010,  # LDI R0,8
                0b00000000,
                0b00001000,
                0b01000111,  # PRN R0
                0b00000000,
                0b00000001,  # HLT
            ]

        for instruction in program:
            self.memory[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        def ADD(reg_a, reg_b):
            # its possible to come back and do these bitwise, but for now MVP
            self.registers[reg_a] += self.registers[reg_b]

        def SUB(reg_a, reg_b):
            self.registers[reg_a] -= self.registers[reg_b]

        def MULT(reg_a, reg_b):
            # its possible to come back and only use the add and subtract functions
            # for mult and div but again, MVP for now
            self.registers[reg_a] *= self.registers[reg_b]
        self.aluOps = {0: ADD,
                       2: MULT}
        try:
            oper = self.aluOps[op]
            oper(reg_a, reg_b)
        except:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            # self.fl,
            # self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.registers[i], end='')

        print()

    def run(self):
        """CPU Functions"""
        def LDI(temp_a, temp_b):
            self.registers[temp_a] = temp_b
            self.PC += 3

        def PRN(register, temp_b):
            print(self.registers[register])
            self.PC += 2

        def HLT(temp_a, temp_b):
            self.running = False

        def PUSH(temp_a, temp_b):
            self.registers[self.SP] -= 1
            self.ram_write(self.registers[self.SP], self.registers[temp_a])
            self.PC += 2

        def POP(temp_a, temp_b):
            if self.registers[self.SP] < 0xf4:
                self.registers[tem_a] = self.ram_read(self.registers[7])
                self.registers[self.SP] += 1
                self.PC += 2

        self.cpuOps = {1: HLT,
                       7: PRN,
                       2: LDI,
                       5: PUSH,
                       6: POP}

        """Run the CPU."""
        self.running = True
        while self.running:
            # get the data out of the instruction
            bits = int(self.ram_read(self.PC), 2)
            self.IR = bits & int('00001111', 2)
            temp_a = int(self.ram_read(self.PC + 1), 2) if (bits &
                                                            int('11000000', 2)) >> 6 >= 1 else None
            temp_b = int(self.ram_read(self.PC + 2), 2) if (bits &
                                                            int('11000000', 2)) >> 6 == 2 else None

            # execute the instruction
            if bits & int('00100000', 2):
                self.alu(self.IR, temp_a, temp_b)
                self.PC += 3 if temp_b is not None else 2
            else:
                try:
                    oper = self.cpuOps[self.IR]
                    oper(temp_a, temp_b)
                except:
                    raise Exception('Unsupported CPU operation')

    def ram_read(self, address):
        return self.memory[address]

    def ram_write(self, address, value):
        self.memory[address] = value


if __name__ == '__main__':
    cpu = CPU()
    cpu.load()
    cpu.run()
