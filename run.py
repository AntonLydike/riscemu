from riscemu import *

if __name__ == '__main__':
    example_progr = """
            .data 0x200
fibs:   .space 56

        .text
main:
        add s1, zero, 0     # storage index
        add s2, zero, 56    # last storage index
        add t0, zero, 1     # t0 = F_{i}
        add t1, zero, 1     # t1 = F_{i+1}
loop:
        sw  t0, fibs(s1)    # save 
        add t2, t1, t0      # t2 = F_{i+2}
        add t0, t1, 0       # t0 = t1
        add t1, t2, 0       # t1 = t2
        add s1, s1, 4       # increment storage pointer
        blt s1, s2, loop    # loop as long as we did not reach array length
        # exit gracefully
        add a0, zero, 0
        add a7, zero, 93
        scall               # exit with code 0
    """
    tk = RiscVTokenizer(RiscVInput(example_progr))
    tk.tokenize()

    print("tokens:")
    for token in tk.tokens:
        print(token)

    ep = ExecutableParser(tk)
    ep.parse()

    print(ep)

