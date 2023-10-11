// A minimal crt0.s that works along the stdlib.s file provided to give
// some resemblance of a functioning compilation target :)
//
// Copyright (c) 2023 Anton Lydike
// SPDX-License-Identifier: MIT

.text

.globl _start
_start:
        // TODO: read argc, argv from a0, a1
        // maybe even find envptr?
        jal main
        jal exit
