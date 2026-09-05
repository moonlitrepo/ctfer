# crackmes.one-Gate.md

# overview
<img width="740" height="380" alt="image" src="https://github.com/user-attachments/assets/e8442eb5-e4f1-4da4-99a0-3e3b76bc13ca" />

challenge ini cukup sederhana karena flag tertulis secara hardcoded di decompiler, namun jika melihat ke isi format flagnya sepertinya kita bisa mengakses nya tanpa melihat source
codenya. aku menggunakan gdb untuk mencoba mengakses flag tersebut.

# analysis & exploit

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(Gate)
└> file batcave
batcave: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=d19c2260ca1f7fef8f0b43b5cab491e526b0a2f4, for GNU/Linux 3.2.0, with debug_info, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(Gate)
└> pwn checksec batcave
[*] '/home/rotalactf/reno/rev/crackme/Gate/batcave'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      No PIE (0x400000)
    Stack:    Executable
    RWX:      Has RWX segments
```
proteksi yang dimiliki oleh program ini sangat buruk. tidak ada yang aktif dan jelas kerentanan yang dimiliki juga semakin banyak, langsung saja eksekusi pakai gdb

```
pwndbg> info functions
All defined functions:

File batcave_gate.c:
24:     void check_password(void);
43:     int main(void);
16:     void open_batcave(void);
```
fungsi target adalah `open_batcave(void)` karena flag tertulis disitu. langkah untuk memaksa program masuk ke fungsi itu adalah dengan melakukan jump ke alamat fungsi itu.

```
pwndbg> disas open_batcave
Dump of assembler code for function open_batcave:
   0x0000000000401186 <+0>:     push   rbp
```
lalu pasang breakpoint di main dan lakukan jumpnya 
```
pwndbg> b main
Breakpoint 1 at 0x401281: file batcave_gate.c, line 44.
pwndbg> r

```

<img width="457" height="95" alt="image" src="https://github.com/user-attachments/assets/82a4c163-f043-4313-92eb-823c28cac9f1" />

