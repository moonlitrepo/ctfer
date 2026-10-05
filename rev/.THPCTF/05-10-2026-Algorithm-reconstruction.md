# Algorithm Reconstruction

## chall 
chall reverse buatan claude, namun cukup untuk mengetes kemampuan pembacaan algortima enkripsi dasar.

## vulnerable point
- proses enkripsi terlalu lemah
  hanya mengandalkan xor dalam menyembunyikan data dan melakukan validasi bukan ide terbaik. karena xor merupakan enkripsi dua arah. jika key digunakan langsung di source code
  dan hacker mendapatkan keynya. maka proses enkripsi sudah terbongkar karena dalam xor kunci enkripsi = kunci dekripsi
- tidak ada anti debugging & obfuscation lain dalam program

## analysis & exploit

saya awali _information gathering_ dengan melakukan _fast check_ . langkah yang saya lakukan adalah memeriksa metadata, proteksi, lalu menjalankan program.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day5-algorithm-reconstruct)
└> file chall ; pwn checksec chall
chall: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=40feb6a3baf7b0e74ddc1b934ff979160b667501, for GNU/Linux 3.2.0, stripped
[*] '/home/rotalactf/reno/rev/3-week/day5-algorithm-reconstruct/chall'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
┌[rotalactf]-[LAPTOP-6QMID52F]-(day5-algorithm-reconstruct)
└> ./chall
Flag: thpctf
Salah.
```
file ini merupakan `stripped elf x86-64 binary` dengan proteksi lengkap. saat dijalankan ,program ini tidak melakukan banyak hal. dia hanya mencetak flag: meminta input. lalu 
asumsi saya program ini melakukan validasi pada input yang saya berikan. karena saya memberikan input random tentu saja program langsung menolaknya dan mencetak teks Salah.

saya melakukan ltrace untuk mencari tahu apa saja fungsi yang digunakan. disini ltrace berhasil membocorkan satu fungsi validasi yang digunakan program. yaitu strlen. tidak menampilkan
fungsi compare atau perbandingan lain tapi program ini mengambil panjang string input. ini menarik karena artinya validasi melibatkan panjang string.
```
└> ltrace ./chall
printf("Flag: ")                                                            = 6
fgets(Flag: thpctf
"thpctf\n", 64, 0x7103dcc048e0)                                       = 0x7ffd66b53d70
strcspn("thpctf\n", "\n")                                                   = 6
strlen("thpctf")                                                            = 6
puts("Salah."Salah.
)                                                              = 7
+++ exited (status 1) +++
```

untuk melanjutkan analisis saya mendecompile program ini menggunakan ghidra. 

metadata file tertulis stripped, itu artinya program ini menghilangkan nama fungsi nya. namun bukan masalah besar karena saya tetap bisa melacak main function via entry point atau
xref string. saya akan gunakan xref string saja sesuai silabus pembelajaran.

saat proses fast check , saya melihat program mencetak string Flag dan Salah, saya akan gunakan Flag . pertama saya pergi ke menu search -> for strings -> search -> lalu ketik
Flag di filter bar. 

hasilnya
```
PARTIALLY_DEFINED	0010202b		?? 2Eh    .	".Flag: "	string	8	false
```
string flag disimpan di alamat **0x10202b**, untuk pergi ke alamat tersebut bisa klik 2 kali baris kolom itu atau gunakan fitur go to dengan klik huruf g. 
saya prefer klik dua kali karena lebih simpel.

```asemmbly
                             s_Flag:_0010202c                                XREF[2]:     FUN_001011e9:00101204(*), 
                                                                                          FUN_001011e9:0010120b(*)  
        0010202c 46 6c 61        ds         "Flag: "
                 67 3a 20 00

```

lihat, string ini memiliki 2 xref yang berasal dari fungsi yang sama : **FUN_001011e9**, saya coba klik xref pertama 
```
FUN_001011e9:00101204
```

lalu saya di arahkan ke fungsi tersebut tepat di baris ini
```C
        00101204 48 8d 05        LEA        RAX,[s_Flag:_0010202c]                           = "Flag: "
                 21 0e 00 00

```
saat melihat sekitar ternyata saya sudah berada di main function, ini dibuktikan dengan adanya fungsi puts dan printf yang mencetak string seperti Salah, Flag, dan lainnya.

berikut fungsi main yang sudah saya rename 

main()
```C

undefined8 FUN_001011e9(void)

{
  char *valid;
  undefined8 ret;
  size_t length;
  long in_FS_OFFSET;
  int i;
  byte input [72];
  long canary;
  
  canary = *(long *)(in_FS_OFFSET + 40);
  printf("Flag: ");
  valid = fgets((char *)input,64,stdin);
  if (valid == (char *)0) {
    ret = 1;
  }
  else {
    length = strcspn((char *)input,"\n");
    input[length] = 0;
    length = strlen((char *)input);
    if (length == 24) {
      for (i = 0; i < 24; i = i + 1) {
        if ((input[i] ^ (&4byte-key_0x102028)[i % 4]) != (&enc_0x102010)[i]) {
          puts("Salah.");
          ret = 1;
          goto cek_canary;
        }
      }
      puts("Benar!");
      ret = 0;
    }
    else {
      puts("Salah.");
      ret = 1;
    }
  }
cek_canary:
  if (canary != *(long *)(in_FS_OFFSET + 40)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return ret;
}

```

bagian validasi input ada di bagian ini
```C
 length = strcspn((char *)input,"\n");
    input[length] = 0;
    length = strlen((char *)input);
    if (length == 24) {
      for (i = 0; i < 24; i = i + 1) {
        if ((input[i] ^ (&4byte-key_0x102028)[i % 4]) != (&enc_0x102010)[i]) {
          puts("Salah.");
          ret = 1;
          goto cek_canary;
        }
      }
      puts("Benar!");
      ret = 0;
    }
```
pertama progam mengambil panjang input , jika panjangnya sama dengan 24 maka program mulai melakukan validasi kedua menggunakan perulangan for. perulangan tersebut dilakukan dari
nol hingga 23 (24 iterasi) 

tiap iterasi nya program akan melakukan operasi xor antara input dengan key, lalu hasil nya dibandingkan dengan enc yang merupakan pointer yang menunjuk ke suatu alamat berisi 
byte byte random yang saya asumsikan sebagai flag terenkripsi. key yang digunakan berukuran 4 byte / panjangnya 4 karakter. dan proses xor dilakukan per byte, plain[i] ^ key[i%4]
penggunaan i mod 4 adalah sebagai batas apabila iterasi melebihi panjang key, maka mod4 akan mengembalikan valuenya menjadi nol lagi, dan iterasi ke5 akan terenkripsi dengan key[0] bukan key[5]


ini proses enkripsi ini biasanya disebut juga dengan _repeating key xor cipher_ . 

**&4byte-key_0x102028**
```
        00102028 5a              ??         5Ah    Z
        00102029 13              ??         13h
        0010202a c7              ??         C7h
        0010202b 2e              ??         2Eh    .
```
key = [0x5a,0x13,0xc7,0x2e]

**&enc_0x102010**
```
        00102010 0e              ??         0Eh
        00102011 5b              ??         5Bh    [
        00102012 97              ??         97h
        00102013 6d              ??         6Dh    m
        00102014 0e              ??         0Eh
        00102015 55              ??         55h    U
        00102016 bc              ??         BCh
        00102017 56              ??         56h    V
        00102018 35              ??         35h    5
        00102019 61              ??         61h    a
        0010201a 98              ??         98h
        0010201b 47              ??         47h    G
        0010201c 2e              ??         2Eh    .
        0010201d 66              ??         66h    f
        0010201e 98              ??         98h
        0010201f 47              ??         47h    G
        00102020 34              ??         34h    4
        00102021 65              ??         65h    e
        00102022 a8              ??         A8h
        00102023 42              ??         42h    B
        00102024 2f              ??         2Fh    /
        00102025 60              ??         60h    `
        00102026 ae              ??         AEh
        00102027 53              ??         53h    S
```

jika hasil xor antara input dan key tersebut tidak sama dengan tiap byte di enc ini maka program akan mencetak teks Salah lalu keluar.

untuk membalik rumusnya cukup sederhana
```
if input[i] ^ key[i % 4] =! enc[i]
bisa dirubah jadi
plain[i] = enc[i] ^ key[i%4]
```
kenapa key yang sama digunakan untuk proses dekripsi? ini karena operasi xor adalah operasi involusi dimana key yang digunakan untuk mengenkripsi juga merupakan key dekripsinya.
```
cipher = plain ^ key
untuk mendapatkan plain tinggal dibalik
plain = cipher ^ key
karena cipher merupakan hasil xor dengan key, jika di xor untuk kedua kalinya akan mengembalikan nilai asli cipher
plain = (plain ^ key) ^ key
selain itu karena sifatnya asosiatif maka bisa 
= plain ^ (key ^ key) (jika nilai nya sama dan dilakukan xor maka hasilnya selalu nol (0) )
 berdasarkan identitasnya, angka apapun yang di xor dengan nol hasilnya adalah angka itu sendiri.
```

saya menggunakan skrip python untuk automasi enkripsi.

```python
key = [0x5a,0x13,0xc7,0x2e]
enc = [
    0x0e,0x5b,0x97,0x6d,
    0x0e,0x55,0xbc,0x56,
    0x35,0x61,0x98,0x47,
    0x2e,0x66,0x98,0x47,
    0x34,0x65,0xa8,0x42,
    0x2f,0x60,0xae,0x53
    ]

print("".join([chr(enc[i] ^ key[i%4]) for i,c in enumerate(enc)]))
```
sedikit flexing juga karena ini sudah saya sederhanakan sehingga proses dekripsi hanya memakan satu baris. haha. 

result : 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day5-algorithm-reconstruct)
└> python3 solver.py
THPCTF{xor_itu_involusi}
┌[rotalactf]-[LAPTOP-6QMID52F]-(day5-algorithm-reconstruct)
└> ./chall
Flag: THPCTF{xor_itu_involusi}
Benar!
```
flag benar, agar automasi penuh saya perbarui skrip sehingga otomatis mengirim flag ke binary:
```
from pwn import *

key = [0x5a,0x13,0xc7,0x2e]
enc = [
    0x0e,0x5b,0x97,0x6d,
    0x0e,0x55,0xbc,0x56,
    0x35,0x61,0x98,0x47,
    0x2e,0x66,0x98,0x47,
    0x34,0x65,0xa8,0x42,
    0x2f,0x60,0xae,0x53
    ]

d = "".join([chr(enc[i] ^ key[i%4]) for i,c in enumerate(enc)])
p = process("./chall")
p.sendline(d.encode())
print(p.recv().decode())
p.close()

```

done 
FLAG : **THPCTF{xor_itu_involusi}**

# gdb analysis
selain itu saya juga melakukan analisis pada gdb, namun mungkin tidak se kompleks ghidra. saya akan analisis bagian perulangan saat membandingkan hasil xor antara input 
dan key dengan enc per iterasinya.

karena program ini dilengkapi pie dan stripped akan cukup tricky dalam memasang breakpoint. namun saya menggunakan plugin pwndbg yang memudahkan analisis nya.
saya mendapat target tempat breakpoint dari ghidra.

```asemmbly
        00101261 e8 4a fe ff ff CALL <EXTERNAL>::strlen size_t strlen(char * __s)
```
saya akan pasang break di alamat 0x101261 .

langkah awal saya dalam pemasangan breakpoint adalah menjalankan program dan berhenti tepat di awal program di mulai, saya lakukan dengan instruksi **starti** 
```
pwndbg> starti
Starting program: /home/rotalactf/reno/rev/3-week/day5-algorithm-reconstruct/chall

Program stopped.
0x00007ffff7fe4540 in _start () 
```
saya sudah punya alamat breakpoint, namun belum mengetahui offsetnya. karena tidak bisa memasang sembarangan,
menggunakan perintah info file saya mendapatkan info bahwa section .text ada di offset berikut
```
   0x0000555555555100 - 0x0000555555555316 is .text
```
sementara awal program menggunakan alamat
```
        Entry point: 0x555555555100
        0x0000555555554318 - 0x0000555555554334 is .interp
```
maka kemungkinan base address nya adalah 0x555555554000, saya coba prove pakai vmmap:
```
pwndbg> vmmap
LEGEND: STACK | HEAP | CODE | DATA | WX | RODATA
             Start                End Perm     Size  Offset File (set vmmap-prefer-relpaths on)
    0x555555554000     0x555555555000 r--p     1000       0 chall
```
karena dengan breakrva akan menggunakan relative virtual address, maka alamat target break **0x101261**  akan terlalu besar ,

jadi saya potong 2 digit terbesarnya menyisakan **0x1261** . kenapa tidak 3 digit saja karena biasanya pie tidak mengacak 3 digit terakhir, awalnya saya memang
berfikir begitu, namun jika diperhatikan, base sekarang adalah 0x4000, jika + 0x261 saja maka akan menjadi 0x4261. dan ini tidak di dalam section.text karena kita tahu sendiri bahwa
section text tadi ada di rentang 0x5000 bukan 0x4000. karena itu saya gunakan 4 digit nya. yaitu **0x1261** sehingga 0x4000 + 0x1261 = 0x5261 , tepat di dalam section .text alias
alamat instruksi program.

```
pwndbg> breakrva 0x1261
Breakpoint 1 at 0x555555555261
pwndbg> c
pwndbg> c
Continuing.
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
Flag: THPCTF{xor_itu_involusi}
```
saya sengaja memasukkan flag agar saya bisa menganalisis instruksi tiap iterasinya. (proses validasi tiap iterasi pasti lolos jadi loop tidak berhenti)

berikut proses loop dalam bahasa asemmbly
```
   [0]
   0x55555555528b:      mov    eax,DWORD PTR [rbp-0x54]
   0x555555555290:      movzx  ecx,BYTE PTR [rbp+rax*1-0x50]
   0x555555555295:      mov    edx,DWORD PTR [rbp-0x54]
   0x555555555298:      mov    eax,edx
   [1]
   0x55555555529a:      sar    eax,0x1f
   0x55555555529d:      shr    eax,0x1e
   0x5555555552a0:      add    edx,eax
   0x5555555552a2:      and    edx,0x3
   0x5555555552a5:      sub    edx,eax
   0x5555555552a7:      mov    eax,edx
   0x5555555552a9:      cdqe
   [2]
   0x5555555552ab:      lea    rdx,[rip+0xd76]        # 0x555555556028
   0x5555555552b2:      movzx  eax,BYTE PTR [rax+rdx*1]
   0x5555555552b6:      xor    ecx,eax
   0x5555555552b8:      mov    eax,DWORD PTR [rbp-0x54]
   0x5555555552bb:      cdqe
   0x5555555552bd:      lea    rdx,[rip+0xd4c]        # 0x555555556010
   0x5555555552c4:      movzx  eax,BYTE PTR [rax+rdx*1]
   0x5555555552c8:      cmp    cl,al
   0x5555555552ca:      je     0x5555555552e
```
[0] bagian ini proses pengambilan data dari buffer mulai dari iterasi di **[rbp-0x54]**, dan nilai input di **[rbp+rax*1-0x50]** bisa disederhanakan **[rbp-0x50 + rax]** 
iterasi dipindahkan ke eax sedangkan input di ecx

[1] sebenarnya inti utama dari proses ini adalah key[i % 4], namun ini menjadi sedikit kompleks karena iterasi (i) di deklarasikan sebagai integer yang dapat bernilai negatif.
maka compiler akan melakukan semacam 'pengaman' untuk menjaga hasil operasi modulus tetap konsisten sesuai angka awal. saya tidak bisa menjelaskan detailnya tapi andaikan iterasi itu
somehow berubah jadi value negatif, maka hasil operasi modulus dengan positif 4 akan mengembalikan value positif karena significant bit nya pasti berbeda, maka instruksi seperti
sar, shr, add dan sub dibawah and itu di tambahkan agar hasilnya tetap konsisten negatif . walaupun pada kasus ini mustahil ada iterasi negatif karena iterasi dimulai dari nol hingga
23 (<24).

untuk operasi modulusnya sendiri sebenarnya hanya satu baris yaitu **   0x5555555552a2:      and    edx,0x3** , and edx,0x3 
kenapa 3 ? dan kenapa operasinya bukan mod tapi and. sederhananya compiler sedang melakukan optimasi. untuk operasi modulus dengan angka kelipatan dua seperti 2, 4, 8 , 16 dan sebagainya
compiler akan mengganti operasi modulus yang mahal di cpu itu menjadi operasi and (kelipatan2-1). mod4 = and 4-1. keajaiban ini terjadi pada level bit. dimana
pada angka 3, bit pertama hingga ke dua terisi oleh 1 (011) sehingga berapapun angka yang melebihi 3 misal 4 (100) ketika di and akan kembali jadi 0. sama persis seperti operasi 
mod 4. hasil bagi angka 4 dengan 4 adalah nol, 

saya akan contohkan kasus iterasi 5 . 5 mod 4 = 1, key[1] lalu di gdb 5 & 3 , 101 and 011 = 001 hasil dari and ini sama persis dengan modulus 4.

```asemmbly
   0x555555555298    mov    eax, edx                      EAX => 5
   0x55555555529a    sar    eax, 0x1f
   0x55555555529d    shr    eax, 0x1e
   0x5555555552a0    add    edx, eax                      EDX => 5 (5 + 0)
   0x5555555552a2    and    edx, 3                        EDX => 1 (5 & 3)
 ► 0x5555555552a5    sub    edx, eax                      EDX => 1 (1 - 0)
   0x5555555552a7    mov    eax, edx                      EAX => 1
```
eax = iterasi
lalu iterasi tersebut di and dengan 3 sehingga menjadi 1, artinya pada iterasi ke5, key akan menggunakan index ke 5 and 3 = 1 untuk mengenkripsi (xor) plain di index ke 5
persis plain[5] ^ key[5%4]

## refleksi :
- saya awalnya mengira bahwa proses modulus pada asemmbly memang se kompleks itu, namun setelah saya telusuri itu hanya pengaman bawaan kompiler dalam menangani proses modulus
  pada tipe data int, jika saja dari source nya iterasi disimpan pada unsigned int, maka tidak mungkin ada negatif sehingga pengaman tersebut tidak akan digunakan.

  prove : saya membuat program sederhana dengan deklarasi unsigned
```C
  #include <stdio.h>

int main(){
	unsigned d;
	unsigned c = 5;
	d = c % 4;
	printf("%u\n",d);

return 0;
}

```
lalu saya compile dan analisis di gdb
```asemmbly
   0x555555555155 <main+12>    mov    dword ptr [rbp - 8], 5       [0x7fffffffdd08] <= 5
   0x55555555515c <main+19>    mov    eax, dword ptr [rbp - 8]     EAX, [0x7fffffffdd08] => 5
   0x55555555515f <main+22>    and    eax, 3                       EAX => 1 (5 & 3)
```
lihat, proses nya benar benar sederhana , karena compiler tahu bahwa tipe data unsigned itu tidak akan menyimpan nilai negatif. jadi tidak perlu instruksi tambahan untuk mengatasi
operasi modulus dengan nilai negatif.

setelah ini saya akan perhatikan tipe data untuk mengetahui estimasi bagaimana bahasa asm mengatasinya.

- sebelumnya saya saat akan memasang breakrva saya menggunakan 0x261 daripada 0x1261. tentu dengan alasan dalam pie 3 digit terakhir tidak akan di acak. itu benar namun dalam kasus ini
  permasalahnnya bukan hanya pie tapi base address. di ghidra base address yang digunakan adalah 0x100000, sedangkan di gdb menggunakan 0x4000 + pie jadi 0x555555554000. maka butuh ketelitian dalam memindah
  alamat dari ghidra ke gdb . setelah ini saya akan terus pastikan apakah offset tersebut benar benar ada di section .text atau tidak, jika tidak maka offset yang saya gunakan belum tepat.
  
## saran
program ini memang sudah dilengkapi proteksi yang kuat, dan stripped. namun itu belum cukup untuk menyembunyikan data di binary. saran perbaikan nya adalah untuk memperkompleks enkripsi
atau jika tidak ingin benar benar bisa di bobol seperti xor ini gunakan enkripsi satu arah seperti hash. 
pada level os / compile lebih baik gunakan -02 , selain membuat program lebih efisien, alur program juga berubah dan akan menyulitkan hacker untuk melakukan reverse pada program ini
saran terakhir & opsional, tambahkan obfuscation dan RDTSC Anti-Debugging agar hacker akan kesulitan saat debugging menggunakan gdb.

kombinasi tersebut akan membuat file ini menjadi jauh lebih aman dari serangan reverse.
