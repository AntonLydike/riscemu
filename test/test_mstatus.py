from riscemu.core.csr import MStatusRegister


def test_mstatus_bits():
    status = MStatusRegister()

    status.mpie = 1

    assert "{:032b}".format(int(status.state)) == "00000000000000000000000010000000"

    status.mpie = 0

    assert "{:032b}".format(int(status.state)) == "00000000000000000000000000000000"

    status.mpp = 3

    assert "{:032b}".format(int(status.state)) == "00000000000000000001100000000000"

    status.sd = 1

    assert "{:032b}".format(int(status.state)) == "10000000000000000001100000000000"

    status.mpp = 1

    assert "{:032b}".format(int(status.state)) == "10000000000000000000100000000000"
