from riscemu import *

if __name__ == '__main__':
    example_progr = """
            .data 0x200
fibs:   .space 56

        .text
main:
        addi s1, zero, 0     # storage index
        addi s2, zero, 56    # last storage index
        addi t0, zero, 1     # t0 = F_{i}
        addi t1, zero, 1     # t1 = F_{i+1}
loop:
        sw  t0, fibs(s1)    # save 
        add t2, t1, t0      # t2 = F_{i+2}
        addi t0, t1, 0       # t0 = t1
        addi t1, t2, 0       # t1 = t2
        addi s1, s1, 4       # increment storage pointer
        blt s1, s2, loop    # loop as long as we did not reach array length
        # exit gracefully
        addi a0, zero, 0
        addi a7, zero, 93
        ebreak                 # launch debugger
        scall               # exit with code 0
    """
    tk = RiscVTokenizer(RiscVInput(example_progr))
    tk.tokenize()

    print("tokens:")
    for token in tk.tokens:
        print(token)

    ep = ExecutableParser(tk)
    ep.parse()

    exe = ep.get_execuable()

    cpu = CPU(RunConfig())
    le = cpu.load(exe)

    cpu.run_loaded(le)



