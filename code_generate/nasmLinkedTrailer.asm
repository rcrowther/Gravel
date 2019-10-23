; Simple frame for NASM testing.
; Trial compile easily using the script trailer.
; The runners fully link.
BITS 64
DEFAULT REL


;SECTION .data
    ;dispMsg db 'You have entered: '
    ;lenDispMsg equ $-dispMsg 


;SECTION .text          ;Code Segment
   
;main:

    ;;Output the message 'The entered number is: '
    ;mov eax, 4
    ;mov ebx, 1
    ;mov ecx, dispMsg
    ;mov edx, lenDispMsg
    ;int 80h  


    
    ;ret

;section	.data
    ;userPrompt db 'Please enter a number: ' ;Ask the user to enter a number
    ;lenUserPrompt equ $-userPrompt    ;length of the message
    ;msg db 'Hello, world!', 0xa ;string to be printed
    ;len equ $ - msg             ;length of the string

;! need rodata in ELF
section	.rodata
    asciiMinus db 45
    ;asciiPlus db 43
    ;asciiLF db 10
    ; ASCII 0, 1, 2.... 
    ;asciiNumerics db 48, 49, 50, 51, 52, 53, 54, 55, 56, 57
    ;! Also hex...
    ; 0123456789ABCDEF
    
;section .bss           ;Uninitialized data
;    num resb 9
        
;section	.text

global main	
main:
    ;prompt
    ;mov	rax, 1      ;system call number (sys_write)
    ;mov	rdi, 1      ;file descriptor (stdout)
    ;mov	rsi, userPrompt     ;message to write
    ;mov	rdx, lenUserPrompt  ;message length
    ;syscall
    
    ;;Read and store the user input
    ;mov rax, 0      ;system call number (sys_read)
    ;mov rdi, 2      ;file descriptor
    ;mov rsi, num  
    ;mov rdx, 9      ;5 bytes (numeric, 1 for sign) of that information
    ;syscall
   
    ;;mov qword[num], 62
   
    ;;Output the number entered
    ; ! use stack and reverse, or use some memory?
    ; jump if not negative
    ;cmp 0, rax
    ;jge loop
    ; for the printout, negate rax
    ;neg rax
    ; Print "-"
    ;push rax
    ;mov rax, 1      ;system call number (sys_write)
    ;mov rdi, 1      ;file descriptor (stdout)
    ;mov rsi, asciiMinus   ;print '-'
    ;mov rdx, 1     ;5 bytes (numeric, 1 for sign)
    ;syscall
    ;pop rax

    ;push rax
    ;push 62
    ;mov rax, 1      ;system call number (sys_write)
    ;mov rdi, 1      ;file descriptor (stdout)
    ;mov rsi, asciiNumerics + 4   ;address of thing to print
    ;mov rdx, 1     ;5 bytes (numeric, 1 for sign)
    ;syscall
    ;pop rax
    ;pop rax
    
    ;;Output the message
    ;mov	rax, 1      ;system call number (sys_write)
    ;mov	rdi, 1      ;file descriptor (stdout)
    ;mov	rsi, msg    ;message to write
    ;mov	rdx, len    ;message length
    ;syscall
    
    ; simple exit
    bmov	rax, qword 60     ;system call number (sys_exit)
    mov	rdi, qword 42     ;system call number return
    syscall
