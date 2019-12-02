	.file	"test.c"
	.intel_syntax noprefix
	.text
	.section	.rodata
.LC0:
	.string	"Is 1"
.LC1:
	.string	"Is 2"
.LC2:
	.string	"Is 3"
.LC3:
	.string	"Default"
	.text
	.globl	main
	.type	main, @function
main:
.LFB0:
	.cfi_startproc
	push	rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	mov	rbp, rsp
	.cfi_def_cfa_register 6
	sub	rsp, 16
	mov	QWORD PTR -8[rbp], 1
	mov	rax, QWORD PTR -8[rbp]
	cmp	rax, 2
	je	.L3
	cmp	rax, 3
	je	.L4
	cmp	rax, 1
	jne	.L8
	lea	rdi, .LC0[rip]
	call	puts@PLT
	jmp	.L6
.L3:
	lea	rdi, .LC1[rip]
	call	puts@PLT
	jmp	.L6
.L4:
	lea	rdi, .LC2[rip]
	call	puts@PLT
	jmp	.L6
.L8:
	lea	rdi, .LC3[rip]
	call	puts@PLT
.L6:
	mov	eax, 0
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE0:
	.size	main, .-main
	.ident	"GCC: (Ubuntu 7.4.0-1ubuntu1~18.04.1) 7.4.0"
	.section	.note.GNU-stack,"",@progbits
