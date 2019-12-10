	.file	"test.c"
	.intel_syntax noprefix
	.text
	.section	.rodata
	.align 8
	.type	str_builder_min_size, @object
	.size	str_builder_min_size, 8
str_builder_min_size:
	.quad	32
	.text
	.globl	main
	.type	main, @function
main:
.LFB5:
	.cfi_startproc
	push	rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	mov	rbp, rsp
	.cfi_def_cfa_register 6
	sub	rsp, 16
    ; calloc
	mov	esi, 24
	mov	edi, 1
	call	calloc@PLT
    ; strut in rbp-8
	mov	QWORD PTR -8[rbp], rax
    ; malloc
	mov	eax, 32
	mov	rdi, rax
	call	malloc@PLT
    ; str in rdx
	mov	rdx, rax
    ; sb->str 
	mov	rax, QWORD PTR -8[rbp]
    ; mov str ptr to first strut
	mov	QWORD PTR [rax], rdx
	mov	rax, QWORD PTR -8[rbp]
    ; get string from strut, set 0
	mov	rax, QWORD PTR [rax]
	mov	BYTE PTR [rax], 0
    ; put 32 on second strut item
	mov	edx, 32
	mov	rax, QWORD PTR -8[rbp]
	mov	QWORD PTR 8[rax], rdx
    ; put 0 on third strut item
	mov	rax, QWORD PTR -8[rbp]
	mov	QWORD PTR 16[rax], 0
	mov	eax, 0
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE5:
	.size	main, .-main
	.ident	"GCC: (Ubuntu 7.4.0-1ubuntu1~18.04.1) 7.4.0"
	.section	.note.GNU-stack,"",@progbits
