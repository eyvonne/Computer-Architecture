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
                '10000010',  # LDI R0,8
                '00000000',
                '00001000',
                '01000111',  # PRN R0
                '00000000',
                '00000001',  # HLT
            ]

        for instruction in program:
            self.memory[address] = instruction
            address += 1
        self.program_end = address

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

            '''00000LGE'''
        def CMP(reg_a, reg_b):
            self.flags = 0
            a = self.registers[reg_a]
            b = self.registers[reg_b]
            if a > b:
                self.flags = 0b00000010
            if a < b:
                self.flags = 0b00000100
            if a == b:
                self.flags = 0b00000001

        self.aluOps = {0: ADD,
                       2: MULT,
                       1: SUB,
                       7: CMP}
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
            if self.registers[self.SP] > self.program_end:
                self.registers[self.SP] -= 1
                self.ram_write(self.registers[self.SP], self.registers[temp_a])
                self.PC += 2
            else:
                raise Exception('Stack is Full')

        def POP(temp_a, temp_b):
            if self.registers[self.SP] < 0xf4:
                self.registers[temp_a] = self.ram_read(self.registers[7])
                self.registers[self.SP] += 1
                self.PC += 2
            else:
                raise Exception("Stack is Empty")

        # the functions for jumping around
        def JMP(temp_a, temp_b):
            self.PC = self.registers[temp_a]

        def JCMP(temp_a, cmp):
            if self.flags & int(cmp, 2):
                JMP(temp_a, None)
            else:
                self.PC += 2

        def JEQ(temp_a, temp_b):
            JCMP(temp_a, '00000001')

        def JGE(temp_a, temp_b):
            JCMP(temp_a, '00000011')

        def JGT(temp_a, temp_b):
            JCMP(temp_a, '00000010')

        def JLE(temp_a, temp_b):
            JCMP(temp_a, '00000101')

        def JLT(temp_a, temp_b):
            JCMP(temp_a, '00000100')

        def JNE(temp_a, temp_b):
            if self.flags & int('00000001', 2):
                self.PC += 2
            else:
                self.PC = self.registers[temp_a]

        self.cpuOps = {1: HLT,
                       7: PRN,
                       2: LDI,
                       5: PUSH,
                       6: POP,
                       }
        self.jOps = {4: JMP,
                     5: JEQ,
                     10: JGE,
                     7: JGT,
                     9: JLE,
                     8: JLT,
                     6: JNE}
        """Run the CPU."""
        self.running = True
        while self.running:
            # print(self.memory)
            # print(self.PC)
            # print(self.registers[self.SP])
            # print(self.program_end)
            # print('------------------------')
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
                    oper = self.cpuOps[self.IR] if not bits & int(
                        '00010000', 2) else self.jOps[self.IR]
                    oper(temp_a, temp_b)
                except KeyError as x:
                    raise Exception(f'Unsupported CPU operation {x}')

    def ram_read(self, address):
        return self.memory[address]

    def ram_write(self, address, value):
        self.memory[address] = value


if __name__ == '__main__':
    cpu = CPU()
    cpu.load()
    cpu.run()
