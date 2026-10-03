# ghidra static analysis

## warm up
chall warm up : crackme.ones-thefirsttest

## Information gathering
melalui fastcheck saya mendapatkan informasi metadata dan jalannya program. ini merupakan file binary elf x86-64. saat dijalankan program meminta password sekaligus memberikan informasi
bahwa password harus dimasukkan dua kali.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> file thefirsttest
thefirsttest: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=13bb296b4c5377f764ebbb9fde15b813fb25e51c, for GNU/Linux 3.2.0, not stripped

┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> ./thefirsttest
Welcome to your first test!
Please input the password:
WARNING: Please input password twice
123445
123454
Wrong password, try agian!
```
hasil analisis dari ltrace tidak menunjukkan informasi berarti, tidak ada fungsi perbandingan atau pemanggilan fungsi lain.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> ltrace ./thefirsttest
puts("Welcome to your first test!"Welcome to your first test!
)                                                      = 28
puts("Please input the password:"Please input the password:
)                                                       = 27
puts("WARNING: Please input password t"...WARNING: Please input password twice
)                                              = 37
__isoc23_scanf(0x401235, 0x7fff1ba089ec, 0, 0x76e0f771c84412345
12345
)                              = 1
puts("Wrong password, try agian!"Wrong password, try agian!
)                                                       = 27
+++ exited (status 0) +++
```

maka saya lanjutkan static analysis dengan mendekompilasi program ini menggunakan ghidra. mengingat dari metadata program tertulis **not strippedd** sehingga symbol dari file tidak
disembunyikan.

namun di ghidra saya juga tidak menemukan ada fungsi menarik, jadi saya langsung analisis fungsi utama yaitu main()

hasil dekompilasi :

```C

undefined8 main(void)

{
  int local_c;
  
  puts("Welcome to your first test!");
  puts("Please input the password:");
  puts("WARNING: Please input password twice");
  __isoc23_scanf(&DAT_00401235,&local_c);
  if (local_c == 1923855305) {
    puts("Well done, you are a master hacker!");
  }
  else {
    puts("Wrong password, try agian!");
  }
  return 0x0;
}

```
langsung terlihat jelas alur program ini. cukup sederhana, program akan meminta input berupa integer (karena tipe data variabel penampung input di deklarasikan sebagai integer)
lalu program membandingkan variabel tersebut dengan **1923855305**, 

namun saya belum menemukan kenapa ada dua kali input disini. karena tujuan static analysis , mencari password sudah selesai menurutku memahami alur program sudah bukan prioritas utama.

## exploit
langsung saja saya masukkan **1923855305** ke dalam program.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> ./thefirsttest
Welcome to your first test!
Please input the password:
WARNING: Please input password twice
1923855305
1923855305
Well done, you are a master hacker!
```

well done, you are a master hacker!

# laporan pembelajaran

untuk hari ini saya akan mulai dengan mengerjakan chall buatan gemini, tentu saya sengaja tidak membaca source code nya dan langsung melakukan compile dengan flag -s agar
hasil file binary menjadi stripped.

## information gathering
seperti prosedur saya sebelumnya, hasil dari fast check dengan melihat metadata menunjukkan bahwa ini merupakan file binary elf x86-64 stripped, sehingga symbols akan disembunyikan.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> file chall
chall: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=c838812e2a73c84fdd5e99c6bc9cd6884d0bea1b, for GNU/Linux 3.2.0, stripped

┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> ./chall
=== THPCTF Static Analysis Challenge ===
Hint: Find the Xrefs from the strings below!
Enter secret key: idk12345
Invalid input!
```

ini sepertinya adalah kebiasaan gemini yang selalu memberikan hint untuk tiap instruksi. tapi tidak apa karena memang itu yang saya rencanakan untuk menganalisis sebuah stripped binary

saya lanjutkan analisis menggunakan ghidra. dan seperti dugaan awal, semua nama fungsi sudah hilang. tidak ada main(), namun masih ada entry point. 

pada kasus ini saya menemukan dua cara untuk menemukan main, yang pertama via xref konstant string, yang kedua melalui entry point.

saya coba gunakan cara pertama :
- pertama saya kembali ke terminal dan melakukan `strings chall` untuk melihat ada string apa saja di binary ini.
hasil :
```
PTE1
u+UH
QMUQQKr}H
w6vqn6v4H
6v4<6m~
=== THPCTF Static Analysis Challenge ===
Hint: Find the Xrefs from the strings below!
Enter secret key:
Invalid input!
Access Granted! Here is your flag:
Wrong key, try again!
```
cukup banyak, saya akan gunakan `===` sebagai patokan.   
selain itu saya melihat beberapa string menarik, terlihat seperti string acak, namun untuk sekarang saya belum tahu apa, dan darimana string random itu berasal.

melanjutkan analisis , untuk mencari string di ghidra saya pergi ke menu search -> for strings -> pada memory block type chekclist all blocks -> masukkan '===' ke search bar.

hasil pencarian :
```
DEFINED	00102008	s_===_THPCTF_Static_Analysis_Chall_00102008	ds "=== THPCTF Static Analysis Challenge ==="	"=== THPCTF Static Analysis Challenge ==="	string	41	true
```
terlihat string persis dengan yang ada di program, saya mengambil data 00102008, ini merupakan alamat tempat string ini berada. saya tekan g untuk go to dan input alamat tersebut

```C

void FUN_001011c9(void)

{
  puts("=== THPCTF Static Analysis Challenge ===");
  puts("Hint: Find the Xrefs from the strings below!");
  return;
}

```
saya mengarah ke sini, sepertinya ini banner dari chall, sayangnya bukan fungsi utama. tapi ini kemajuan karena saya semakin dekat dengan fungsi main. kenapa demikian? karena fungsi
ini dipanggil oleh main jadi saya tinggal mencari xref dari fungsi ini. 

sebelum itu saya akan rename FUN_001011c9() menjadi banner(). selanjutnya untuk mencari xref nya klik nama fungsi, klik kanan dan pilih reference, lalu klik find references to banner
atau find references to (alamat memori fungsi). akan muncul tabel dengan beberapa instruksi program, saya klik yang melakukan instruksi CALL karena saya mencari fungsi yang melakukan
pemanggilan fungsi banner, apa lagi jika bukan main.

dan benar saja, fungsi yang saya cari akhirnya muncul, di fungsi ini semua instruksi progarm dilakukan, print banner, input, dan flag terenkripsi.
```C
undefined8 FUN_00101214(void)

{
  int iVar1;
  long in_FS_OFFSET;
  undefined4 local_30;
  int local_2c;
  byte local_28 [0x18];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  banner();
  printf("Enter secret key: ");
  iVar1 = __isoc99_scanf(&DAT_00102078,&local_30);
  if (iVar1 == 0x1) {
    iVar1 = FUN_001011f2(local_30);
    if (iVar1 == 0x0) {
      puts("Wrong key, try again!");
    }
    else {
      puts("Access Granted! Here is your flag:");
      local_28[0x0] = 0x51;
      local_28[0x1] = 0x4d;
      local_28[0x2] = 0x55;
      local_28[0x3] = 0x51;
      local_28[0x4] = 0x51;
      local_28[0x5] = 0x4b;
      local_28[0x6] = 0x72;
      local_28[0x7] = 0x7d;
      local_28[0x8] = 0x77;
      local_28[0x9] = 0x36;
      local_28[0xa] = 0x76;
      local_28[0xb] = 0x71;
      local_28[0xc] = 0x6e;
      local_28[0xd] = 0x36;
      local_28[0xe] = 0x76;
      local_28[0xf] = 0x34;
      local_28[0x10] = 0x3c;
      local_28[0x11] = 0x36;
      local_28[0x12] = 0x6d;
      local_28[0x13] = 0x7e;
      local_28[0x14] = 0x0;
      for (local_2c = 0x0; local_28[local_2c] != 0x0; local_2c = local_2c + 0x1) {
        putchar((int)(char)(local_28[local_2c] ^ 0x5));
      }
      putchar(0xa);
    }
  }
  else {
    puts("Invalid input!");
  }
  if (local_10 == *(long *)(in_FS_OFFSET + 0x28)) {
    return 0x0;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


```

pertama saya akan ubah nama FUN_00101214 menjadi main().

namun sebelum menganalisis flagnya saya menemukan satu fungsi lagi yang dipanggil tepat dibawah scanf
```C
iVar1 = __isoc99_scanf(&DAT_00102078,&local_30);
  if (iVar1 == 0x1) {
    iVar1 = FUN_001011f2(local_30);
        if (iVar1 == 0x0) {action...}
```
saya curigai ini sebagai fungsi check / fungsi validasi password. saya coba analisis ini sebagai jalan pertama bypass untuk mendapatkan flag.
berikut hasil dekompilasinya
```C

bool valid(int param_1)

{
  return param_1 == 26974;
}

```
sepertinya hanya ini validasi yang dilakukan, saya coba input nilai **26974** tersebut di binary:
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> ./chall
=== THPCTF Static Analysis Challenge ===
Hint: Find the Xrefs from the strings below!
Enter secret key: 26974
Access Granted! Here is your flag:
THPTTNwxr3stk3s193h{
```

oke, saya berhasil melewati validasi, namun flag yang didapatkan sepertinya rusak. hipotesis yang langsung terlintas di kepalaku adalah secret key memiliki relasi dengan proses deskripsi
flag, tapi di saat yang sama saya juga berfikir bahwa jika ini key yang ku dapatkan dari source , maka walaupun berelasi pun harus sebuah key valid kan? 

maka saya kembali ke ghidra untuk coba melakukan analisis lanjutan

jika hanya fokus pada proses deskripsi flag
```C
    else {
      puts("Access Granted! Here is your flag:");
      local_28[0x0] = 0x51;
      local_28[0x1] = 0x4d;
      local_28[0x2] = 0x55;
      local_28[0x3] = 0x51;
      local_28[0x4] = 0x51;
      local_28[0x5] = 0x4b;
      local_28[0x6] = 0x72;
      local_28[0x7] = 0x7d;
      local_28[0x8] = 0x77;
      local_28[0x9] = 0x36;
      local_28[0xa] = 0x76;
      local_28[0xb] = 0x71;
      local_28[0xc] = 0x6e;
      local_28[0xd] = 0x36;
      local_28[0xe] = 0x76;
      local_28[0xf] = 0x34;
      local_28[0x10] = 0x3c;
      local_28[0x11] = 0x36;
      local_28[0x12] = 0x6d;
      local_28[0x13] = 0x7e;
      local_28[0x14] = 0x0;
      for (local_2c = 0x0; local_28[local_2c] != 0x0; local_2c = local_2c + 0x1) {
        putchar((int)(char)(local_28[local_2c] ^ 0x5));
      }
      putchar(0xa);
```
flag dalam bentuk hex ini ber byte nya akan di dekripsi melalui operasi xor dengan key 0x5. dilakukan secara berulang hingga saat flag sudah full ter dekripsi string tersebut akan 
di tambahkan '0xa' atau \n (new line). 

saya coba lakukan reconstruct algorithm pada proses dekripsi ini untuk memvalidasi flag dan key nya.

berikut proses dekripsi dalam bahasa python (agar lebih mudah dipahami):
```python
local_28 = [0x51,0x4d,0x55,0x51,0x51,0x4b,0x72,0x7d,0x77,0x36,0x76,0x71,0x6e,0x36,0x76,0x34,0x3c,0x36,0x6d,0x7e,0x0]

for i in local_28:
    print(chr(i ^ 0x5) , end= "")

```
sangat sederhana, anehnya hal yang sama terjadi.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> python3 chall.py
THPTTNwxr3stk3s193h{%
```
sepertinya memang flag ini salah, mungkin karena model gemini yang saya gunakan masih gratisan. but kurang lebih begitu lah caraku menemukan flagnya

flag : **THPTTNwxr3stk3s193h{** 

namun tidak berhenti disini, saya kembali ke terminal untuk mengambil flag asli di source code dan melakukan enkripsi nya secara manual,
```python
flag = 'THPCTF{xr3fs_4r3_3p1c}'
enc = [ord(flag[i])^0x5 for i in range(len(flag))]
print(enc)
```
result **[81, 77, 85, 70, 81, 67, 126, 125, 119, 54, 99, 118, 90, 49, 119, 54, 90, 54, 117, 52, 102, 120]**

saya memasukkannya ke source code dan melakukan compile ulang

terakhir saya coba masukkan password yang sama :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> ./chall
=== THPCTF Static Analysis Challenge ===
Hint: Find the Xrefs from the strings below!
Enter secret key: 26974
Access Granted! Here is your flag:
THPCTF{xr3fs_4r3_3p1c}
```

WELL DONE
flag : **THPCTF{xr3fs_4r3_3p1c}**

kedepannya saya akan pertimbangkan lagi mengenai model ai yang akan membuat chall. 

## pelengkap :
~ cara mencari main via entry  
jujur cara mencarinya jauh lebih mudah, pada awal halaman dekompilasi ghidra di symbol tree, pasti ada teks entry di antara nama fungsi . 
klik lalu lihat dia akan pergi ke fungsi apa

```C

void processEntry entry(undefined8 param_1,undefined8 param_2)

{
  undefined1 auStack_8 [0x8];
  
  __libc_start_main(main,param_2,&stack0x00000008,0x0,0x0,param_1,auStack_8);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

```
coba lihat fungsi __libc_start_main(), mudahnya fungsi ini lah yang akan memanggil fungsi utama program. biasanya di argumen satu. 
```C
__libc_start_main(main,param_2,&stack0x00000008,0x0,0x0,param_1,auStack_8);

```
kebetulan fungsi main sudah saya rename jadi disini tertulis
main, namun normal nya pada stripped binary nama main itu akan berbentuk alamat memory dari fungsi main. 


```C
__libc_start_main(FUN_00101214,param_2,&stack0x00000008,0x0,0x0,param_1,auStack_8);
```

nah seperti ini,

biasanya di ghidra untuk pergi ke suatu fungsi cukup klik dua kali alamat memory atau nama fungsi nya, pada ghidra versi yang saya gunakan v 12.1.3 ini bisa dilakukan.
namun harusnya fitur klik2 kali ini sudah ada pada versi versi sebelumnya juga. jika tidak ada pun masih bisa menggunakan fitur go to untuk pergi ke fungsi tujuan memanfaatkan alanat
memori yang dipanggil oleh libc start main ini.


untuk melengkapi analisis saya akan cari tahu dari mana asal string random di hasil strings binary itu, saya coba lakukan strings lagi pada file binary yang sudah ku perbaiki flagnya,
string itu masih ada namun sedikit berbeda dari sebelumnya :
```
QMUFQC~}H
w6cvZ1w6H
w6Z6u4fxH

jika di gabung : QMUFQC~}Hw6cvZ1w6Hw6Z6u4fxH
strings file pertama : QMUQQKr}Hw6vqn6v4H6v4<6m~
```
terlihat abstrak, tapi dari file pertama sepertinya ada sedikit perbedaan . satu satunya yang berubah dari file compile gemini dan compile baruku adalah flagnya, maka saya 
mencurigai ini sebagai flag. saya coba cetak hasil dekripsi tadi dalam bentuk char :
```python
flag = 'THPCTF{xr3fs_4r3_3p1c}'
enc = [ord(flag[i])^0x5 for i in range(len(flag))]
print("".join([chr(i) for i in enc]))
```
result ; 
```
QMUFQC~}w6cvZ1w6Z6u4fx
```
tunggu dulu, bukan kah ini sama ?
```
QMUFQC~}Hw6cvZ1w6Hw6Z6u4fxH
```
hem sepertinya strings pada strings ini tercampur oleh sampah sampah byte lain, saya coba dekripsi langsung dari strings ini
```python
string = 'QMUFQC~}Hw6cvZ1w6Hw6Z6u4fxH'
dec = [chr(ord(string[i])^0x5) for i in range(len(string))]
print("".join(dec))
```
result : **THPCTF{xMr3fs_4r3Mr3_3p1c}M**
sepertinya berhasil, namun ini jelas bukan flag valid, karena ada beberapa karakter yang benar benar random tercampur dengan flag. jika pun tahu key di awal analisis, ini akan menjadi
kebuntuan karena tidak tahu mana flag dan sampah.

kesimpulannya untuk analisis string lebih baik menggunakan hasil dekompilasi daripada tools strings karena strings sejatinnya akan mencetak apapun printable characther di suatu file. 
sehingga informasi yang diberikan tidak bisa 100% bersih.


full code :
```python3
# perbaikan flag
# flag = 'THPCTF{xr3fs_4r3_3p1c}'
# enc = [hex(ord(flag[i])^0x5) for i in range(len(flag))]
# print(enc)

# data dari decompiler  : chall baru setelah di revisi
    #   puts("Access Granted! Here is your flag:");
    #   local_28[0x0] = 0x51;
    #   local_28[0x1] = 0x4d;
    #   local_28[0x2] = 0x55;
    #   local_28[0x3] = 0x46;
    #   local_28[0x4] = 0x51;
    #   local_28[0x5] = 0x43;
    #   local_28[0x6] = 0x7e;
    #   local_28[0x7] = 0x7d;
    #   local_28[0x8] = 0x77;
    #   local_28[0x9] = 0x36;
    #   local_28[0xa] = 0x63;
    #   local_28[0xb] = 0x76;
    #   local_28[0xc] = 0x5a;
    #   local_28[0xd] = 0x31;
    #   local_28[0xe] = 0x77;
    #   local_28[0xf] = 0x36;
    #   local_28[0x10] = 0x5a;
    #   local_28[0x11] = 0x36;
    #   local_28[0x12] = 0x75;
    #   local_28[0x13] = 0x34;
    #   local_28[0x14] = 0x66;
    #   local_28[0x15] = 0x78;

# proses dekripsi flag 
local_28 = [0x51, 0x4d, 0x55, 0x46, 0x51, 0x43, 0x7e, 0x7d, 0x77, 0x36, 0x63, 0x76, 0x5a, 0x31, 0x77, 0x36, 0x5a, 0x36, 0x75, 0x34, 0x66, 0x78]
print("".join([chr(i^0x5) for i in local_28]))

# analisis string pada hasil strings
string = 'QMUFQC~}Hw6cvZ1w6Hw6Z6u4fxH'
dec = [chr(ord(string[i])^0x5) for i in range(len(string))]
print("".join(dec))
```

# crackme1
akhirnya proses mengerjakan chall dari claude dimulai

```
Pertanyaan panduan analisis mandiri
1. Dari string mana kamu mulai dan fungsi apa yang me-xref-nya?
2. Di mana array stages dan apa isi tiap entrinya (offset 0 dan 8)?
3. Bagaimana main memanggil stage, dan kenapa itu bukan call langsung?
4. Tulis rumus transformasi dan bedakan mana kunci, mana tabel.
```
## information gathering
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> file crackme1
crackme1: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=b9fd6bfb78335f308f28b28367eff17c79367e8a, for GNU/Linux 3.2.0, stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> ./crackme1
usage: crackme1 <pass>
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> ./crackme1 password123
Access denied
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> ltrace ./crackme1 pass
strlen("pass")                                                                           = 4
puts("Access denied"Access denied
)                                                                    = 14
+++ exited (status 1) +++
```

hasil analisis singkat ini cukup membantu, program stripped dan input password dilakukan sebagai argumen program. selain itu proses validasi pertama bocor, yaitu strlen. program ini 
memulai validasi dengan menghitung panjang input.

namun tentu saja informasi ini belum cukup , saya akan melanjutkan analisis menggunakan ghidra

saya akan gunakan entry untuk mencari main function :
```C

void processEntry entry(undefined8 param_1,undefined8 param_2)

{
  undefined1 auStack_8 [0x8];
  
  __libc_start_main(FUN_001011f0,param_2,&stack0x00000008,0x0,0x0,param_1,auStack_8);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

```
main : FUN_001011f0  
saya akan rename menjadi **main**

hasil dekompilasi main()
```

undefined8 main(int param_1,long param_2)

{
  int iVar1;
  undefined8 uVar2;
  int local_c;
  
  if (param_1 == 0x2) {
    for (local_c = 0x0; local_c < 0x2; local_c = local_c + 0x1) {
      iVar1 = (*(code *)(&PTR_FUN_00104028)[(long)local_c * 0x2])(*(undefined8 *)(param_2 + 0x8));
      if (iVar1 == 0x0) {
        puts("Access denied");
        return 0x1;
      }
    }
    puts("Access granted");
    uVar2 = 0x0;
  }
  else {
    puts("usage: crackme1 <pass>");
    uVar2 = 0x1;
  }
  return uVar2;
}
```

saya akan fokus pada if else utama :
```C
  if (param_1 == 0x2) {
    for (local_c = 0x0; local_c < 0x2; local_c = local_c + 0x1) {
      iVar1 = (*(code *)(&PTR_FUN_00104028)[(long)local_c * 0x2])(*(undefined8 *)(param_2 + 0x8));
      if (iVar1 == 0x0) {
        puts("Access denied");
        return 0x1;
      }
    }
    puts("Access granted");
    uVar2 = 0x0;
  }
  else {
    puts("usage: crackme1 <pass>");
    uVar2 = 0x1;
  }
```
param_1 == 0x2, saya pernah mempelajari bahwa parameter pertama dan kedua program adalah argc dan argv, argc adalah argumen counter dimana jika valuenya 2 artinya program ini
dijalankan menggunakan 1 buah argumen, bukan 2 karena argumen pertama adalah nama program itu sendiri, lalu disimpan lah argumen tersebut di parameter dua, argv. 

jika dijalankan tanpa argumen maka program akan mencetak **"usage: crackme1 <pass>"** 

selanjutnya program melakukan perulangan for sebanyak 2 kali, dari nol ke satu, jujur saya sendiri belum tahu kenapa menggunakan for, jadi saya lanjutkan analisis apa yang dilakukan for ini. di bawahnya terdapat 
pemanggilan fungsi, sebuah pointer ke suatu alamat memori yang menunjuk ke beberapa fungsi. rupanya for digunakan untuk memanggil ketiga fungsi ini secara bertahap

```
                             PTR_FUN_00104028                                XREF[2]:     main:00101234(*), 
                                                                                          main:0010123b(*)  
        00104028 69 11 10        addr       FUN_00101169
                 00 00 00 
                 00 00
        00104030 17 20 10        addr       s_content_00102017                               = "content"
                 00 00 00 
                 00 00
        00104038 91 11 10        addr       FUN_00101191
                 00 00 00 
                 00 00

```
PTR_FUN_00104028 merupakan sebuah tabel berisi pointer yang menunjuk ke fungsi tujuan, ada 2 fungsi yang di panggil yaitu pada index ke 0 dan index ke 2. **FUN_00101169** dan 
**FUN_00101191**
```C
(&PTR_FUN_00104028)[(long)local_c * 0x2])
```
setelah diperhatikan lebih seksama ternyata perulangan ini hanya memanggil index pertama dan index terakhir, karena pada loop pertama , local_c = 0 *2 = 0. index 0 = FUN_00101169  

lalu loop ke dua local_c = 1 *2 = 2 , index 2 = FUN_00101191

ini teknik pemanggilan fungsi yang efisien dan keren juga menurutku.
terakhir adalah argumen yang digunakan tiap fungsi : **(*(undefined8 *)(param_2 + 0x8));** argumennya adalah param_2 +8 , kenapa+8 , seperti yang sudah saya jelaskan tadi. 
argv pertama dari sebuah program adalah program itu sendiri, ukuran nya adalah 8 byte. sehingga untuk dapat akses ke argumen input, offset nya perlu di tambah 8. sehingga menunjuk ke awal 
argumen input.

dengan ini fungsi for telah di analisis sebagai pemanggil fungsi lain menggunakan param_2 sebagai argumennya (input argumen kita).

sekarang waktunya analisis tiap fungsi akan melakukan apa. di awali dari **FUN_00101169** fungsi pertama di tabel, saya akan rubah namanya menjadi validation_1()
hasil dekompilasi :
```C

bool validation1(char *param_1)

{
  size_t sVar1;
  
  sVar1 = strlen(param_1);
  return sVar1 == 0x8;
}

```
fungsi pertama memeriksa panjang string menggunakan fungsi strlen(), jika panjangnya persis 8 byte maka fungsi ini akan mengembalikan nilai true, jika tidak 8 byte akan false.
sederhana.

lanjut ke fungsi ke dua : **FUN_00101191** , saya rename menjadi validation2
hasil dekompilasi
```C

undefined8 validation2(long param_1)

{
  int local_c;
  
  local_c = 0x0;
  while( true ) {
    if (0x7 < local_c) {
      return 0x1;
    }
    if ((byte)((char)local_c + (*(byte *)(param_1 + local_c) ^ 0x5a)) != (&DAT_00102008)[local_c])
    break;
    local_c = local_c + 0x1;
  }
  return 0x0;
}

```
untuk memudahkan pembacaan kode saya akan merename semua variabelnya.
```C
undefined8 validation2(long param_1)

{
  int i;
  
  i = 0x0;
  while( true ) {
    if (0x7 < i) {
      return 0x1;
    }
    if ((byte)((char)i + (*(byte *)(param_1 + i) ^ 0x5a)) != (&pass_value)[i]) break;
    i = i + 0x1;
  }
  return 0x0;
}

```
masih terlihat hasil dekompiler tapi ini lebih manusiawi untuk dibaca. program lagi lagi melakukan validasi dengan melakukan perulangan untuk mengambil tiap byte argumen kita untuk
di lakukan operasi xor dengan nilai **0x5a** dan penjumlahan sesuai loop lalu hasilnya dibandingkan dengan byte yang ada di pointer &pass_value. karena perbandingan ini saya asumsikan proses enkripsi yang dilalui
&pass_value pasti sama, saya coba inverse rumus ini untuk mendapatkan karakter asli dari &pass_value.

**pass value :**
```asemmbly
                             pass_value                                      XREF[2]:     validation2:001011c8(*), 
                                                                                          validation2:001011cf(*)  
        00102008 1d              ??         1Dh
        00102009 33              ??         33h    3
        0010200a 35              ??         35h    5
        0010200b 41              ??         41h    A
        0010200c 2c              ??         2Ch    ,
        0010200d 40              ??         40h    @
        0010200e 7f              ??         7Fh    
        0010200f 70 6c 65        ds         "plength"
                 6e 67 74 
                 68 00

```
saya ekstrak sebagai list : 
leak = [0x1d,0x33,0x35,0x41,0x2c,0x40,0x7f,0x70]

kenapa tidak saya ekstrak semua?? karena sesuai validasi pertama. panjang password valid adalah 8 byte. selain itu for loop hanya dilakukan dari 0 higga 7, (8 kali)
maka 8 byte pertama lah yang dibandingkan. lagipula data ke 9 merupakan string valid yaitu (length) dan ini jelas bukan hasil enkripsi.

untuk memahami rumus enkripsi saya menulis ulang enkripsi tersebut di bahasa python :
```python
for i in range(0,8):
    enc = (param_1 ^ 0x5a) + i
```
maka inverse nya akan seperti ini
```python
enc = [0x1d,0x33,0x35,0x41,0x2c,0x40,0x7f,0x70]
for i in range(0,8):
    dec = (enc[i] -i) ^ 0x5a
    print(chr(dec),end='')
```

result : 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> python3 crackme1.py
Ghidra#3%
```
agar rapi saya tambahkan baris print() setelah loop untuk membuat newline dan menghapus % nya. 
```
for i in range(0,8):
    dec = (enc[i] -i) ^ 0x5a
    print(chr(dec),end='')
print()
```

result 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> python3 crackme1.py
Ghidra#3
┌[rotalactf]-[LAPTOP-6QMID52F]-(day3-reconstruct-algorithm)
└> ./crackme1 Ghidra#3
Access granted
```

welldone, 

full code yang di buat otomatis input.
```python
from pwn import *

enc = [0x1d,0x33,0x35,0x41,0x2c,0x40,0x7f,0x70]
passwd = ''
for i in range(0,8):
    dec = (enc[i] -i) ^ 0x5a
    passwd += chr(dec)

p = process(['./crackme1',passwd])
print(p.clean().decode())
p.close()
```

Pertanyaan panduan analisis mandiri
1. Dari string mana kamu mulai dan fungsi apa yang me-xref-nya?
2. Di mana array stages dan apa isi tiap entrinya (offset 0 dan 8)?
3. Bagaimana main memanggil stage, dan kenapa itu bukan call langsung?
4. Tulis rumus transformasi dan bedakan mana kunci, mana tabel.

jawaban panduan analisis
saya tidak mencari menggunakan string jika entry point tersedia. ini cara yang cukup cepat untuk mencari main function daripada mengetik string. array stages berisi password terenkripsi
ada di 0x102008 dan isi datanya adalah [0x1d,0x33,0x35,0x41,0x2c,0x40,0x7f,0x70] . main memanggil stage melalui tabel berisi beberapa pointer berisi alamat asli fungsi. alasan pastinya
saya belum yakin tapi asumsi saya ini dibuat untuk penyederhanaan program. asumsi ini lemah karena saya sendiri kekurangan informasi. 

berikut rumus yang digunakan program, saya sederhanakan dan tulis dalam bahasa python. namun masih menggunakan logika bahasa C
```python
for i in range(0,8):
    enc = (param_2[i] ^ 0x5a) + i
    if enc != passwd[i]
    break
```
enc merupakan hasil enkripsi, kuncinya adalah 0x5a, yang nantinya akan dibandingkan dnegan tabel aray berisi hasil enkripsi password. yaitu passwd.


terakhir saya coba compile ulang chall ini dengan optimization -O2
```bash
gcc -O2 -o crackme1 crackme1.c && strip crackme1
```

langsung saya decompile dan rename semua fungsinya. dan sebenarnya hal yang sangat berbeda ada disini.
dekompilasi main()
```C

undefined8 main(int param_1,long param_2)

{
  undefined8 uVar1;
  int iVar2;
  
  if (param_1 == 0x2) {
    uVar1 = *(undefined8 *)(param_2 + 0x8);
    iVar2 = length_validation(uVar1);
    if (iVar2 != 0x0) {
      iVar2 = xor_validation(uVar1);
      if (iVar2 != 0x0) {
        puts("Access granted");
        return 0x0;
      }
    }
    puts("Access denied");
  }
  else {
    puts("usage: crackme1 <pass>");
  }
  return 0x1;
}

```

strukturnya benar benar berbeda, bagi saya ini terlihat lebih sederhana dan efisien daripada hasil dekompilasi sebelumnya. sekarang saya juga menemukan jawaban kenapa yang pertama 
memanggil stage, karena program source nya memang sengaja dibuat begitu dan di compile tanpa optimization sehingga tiap instruksi akan ditulis mirip persis dengan source code.

sedangkan dengan flag -O2 , compiler akan mulai merombak struktur asli nya dan menulis ulang kode dalam bentuk yang jauh lebih efisien, bisa dilihat sekarang fungsi tidak dipanggil
dengan tabel namun langsung di panggil saja dari main. perubahan yang signifikan ini menghilangkan beberapa baris kode dan membuat ukuran program bisa menyusut serta kecepatan run program
akan meningkat. 

kekurangannya mungkin di beberapa kasus kompleks akan sulit membaca hasil dekompilernya karena struktur kodenya sendiri di rubah,
namun di kasus saya chall ini justru terlihat lebih sederhana dan mudah di mengerti. tidak semua kasus
optimization ini ketika di decompile akan jadi lebih sederhana ya. 


kesimpulan menganalisis membutuhkan lebih banyak informasi untuk menjawab pertanayaan tak diketahui, karena tingkat akurasi fakta dari jawaban pertanyaan analisis berbanding lurus
dengan jumlah informasi yang dimiliki.
