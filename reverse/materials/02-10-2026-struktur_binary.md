# Struktur Binary


# write up 
name challenge : thp_rev1   
category : reverse engineering   
flag : THPCTF{r3v_1s_f0r_3v3ry}


# analysis & exploit

saya melakukan _fast check_ dengan memeriksa metadata dan mendapatkan informasi bahwa symbols pada filel binary ini sudah dihilangkan, ini ditandai dari adanya teks **stripped** pada metadata nya. ketika dijalankan program ini meminta input flag. input random akan membuat akses ditolak.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day2-struktur-biner)
└> file thp_rev1
thp_rev1: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=b5f145bc3978392860f42d2eb9643f48c2e844ff, for GNU/Linux 3.2.0, stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(day2-struktur-biner)
└> ./thp_rev1
=== THP Crackme #1 ===
Enter flag: flag
Access denied.
```
saya coba gunakan strings dan mendapatkan flag dummy yang ketika di input, binary akan memberikan respon lain.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day2-struktur-biner)
└> strings thp_rev1 | grep -i thp
THPCTF{n0t_th3_fl4g_s0rry}
THPCTF{
=== THP Crackme #1 ===
┌[rotalactf]-[LAPTOP-6QMID52F]-(day2-struktur-biner)
└> ./thp_rev1
=== THP Crackme #1 ===
Enter flag: THPCTF{n0t_th3_fl4g_s0rry}
Nice try. strings aja gak cukup :)
```

tidak ada flag lain disitu, namun ada string format flag yang tidak selesai. menarik. 

karena ini adalah file binary stripped, saya lebih memilih menggunakan ghidra sebagai tools analisis pertama ku.

setelah mendekompilasi saya langsung di arahkan ke entry point program.
```C
 oid processEntry entry(undefined8 param_1,undefined8 param_2)

{
  undefined1 auStack_8 [0x8];
  
  __libc_start_main(FUN_00401513,param_2,&stack0x00000008,0x0,0x0,param_1,auStack_8);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}
```

terlihat jelas, fungsi __libc_start_main() hanya memanggil **FUN_00401513**, setelah saya telusuri ternyata memang benar ini adalah fungsi main. bisa dibuktikan dengan adanya string yang di cetak saat program sedang di jalankan.

main
```C
undefined8 FUN_00401513(void)

{
  int iVar1;
  char *pcVar2;
  undefined8 uVar3;
  size_t sVar4;
  char local_88 [0x80];
  
  printf("=== THP Crackme #1 ===\nEnter flag: ");
  pcVar2 = fgets(local_88,0x80,stdin);
  if (pcVar2 == (char *)0x0) {
    uVar3 = 0x1;
  }
  else {
    sVar4 = strcspn(local_88,"\n");
    local_88[sVar4] = '\0';
    iVar1 = strcmp(local_88,PTR_s_THPCTF{n0t_th3_fl4g_s0rry}_004040c0);
    if (iVar1 == 0x0) {
      puts("Nice try. strings aja gak cukup :)");
      uVar3 = 0x1;
    }
    else {
      iVar1 = FUN_0040144b(local_88);
      if (iVar1 == 0x0) {
        puts("Access denied.");
      }
      else {
        puts("Access granted! Flag benar.");
      }
      uVar3 = 0x0;
    }
  }
  return uVar3;
}

```

pada baris if else ke dua saya menemukan fungsi validasi yang akan memberikan akses jika mengembalikan nilai true. untuk memudahkan proses analisis aku akan mengganti nama fungsi tersebut menjadi fungsi **check**

```
FUN_0040144b() = check()
```

berikut hasil dekompilasi fungsi check()
```C

undefined8 check(char *param_1)

{
  int iVar1;
  size_t sVar2;
  undefined8 uVar3;
  
  sVar2 = strlen(param_1);
  if (sVar2 == 0x18) {
    iVar1 = strncmp(param_1,"THPCTF{",0x7);
    if (iVar1 == 0x0) {
      if (param_1[0x17] == '}') {
        iVar1 = FUN_00401292(param_1 + 0x7);
        if (iVar1 == 0x0) {
          uVar3 = 0x0;
        }
        else {
          iVar1 = FUN_004012ee(param_1 + 0xb);
          if (iVar1 == 0x0) {
            uVar3 = 0x0;
          }
          else {
            iVar1 = FUN_004013e8(param_1 + 0x11);
            if (iVar1 == 0x0) {
              uVar3 = 0x0;
            }
            else {
              uVar3 = 0x1;
            }
          }
        }
      }
      else {
        uVar3 = 0x0;
      }
    }
    else {
      uVar3 = 0x0;
    }
  }
  else {
    uVar3 = 0x0;
  }
  return uVar3;
}
```
program ini melakukan 6 validasi untuk memeriksa apakah flag  yang diinput merupakan flag valid. 3 validasi pertama adalah penentu panjang dan format flag.

```C
  sVar2 = strlen(param_1);
  if (sVar2 == 0x18) { /* VALIDASI PERTAMA */
    iVar1 = strncmp(param_1,"THPCTF{",0x7); /* validasi kedua */
    if (iVar1 == 0x0) {
      if (param_1[0x17] == '}') {  /* validasi ke tiga */
```

dari 3 validasi pertama ini bisa di simpulkan bahwa flag memiliki panjang **0x18 karakter**, format flag **THPCTF{** (7 karakter pertama) dan diakhiri dengan '}' di ujung.

flag_extracted : **THPCTF{aaaaaaaaaaaaaaaa}**

flag ini akan dengan mudah melewati 3 validasi pertama. selanjutnya adalah menganalisis validasi ke 4, 5, dan 6. tiap validasi ini program memanggil fungsi yang tidak diketahui. namun tiap fungsi melakukan sesuatu yang dicurigai sebagai proses validasi per beberapa index di flag.



saya akan ubah nama masing  masing menjadi func:
```
validasi ke 4 : FUN_00401292 -> func4
validasi ke 5 : FUN_004012ee -> func5
validasi ke 6 : FUN_004013e8 -> func6

```
proses pemanggilan :
```C
iVar1 = func4(param_1 + 0x7);
iVar1 = func5(param_1 + 0xb);
iVar1 = func6(param_1 + 0x11);
```
index ke 7 dari param_1 adalah karakter setelah { di string THPCTF{, untuk mengetahui apa yang dilakukannya saya lanjutkan analisis dengan mendekompilasi func4

## analisis func4
hasil dekompilasi:
```C

undefined8 func4(long param_1)

{
  int local_c;
  
  local_c = 0x0;
  while( true ) {
    if (0x3 < local_c) {
      return 0x1;
    }
    if ((*(byte *)(param_1 + local_c) ^ DAT_00404050) != (&DAT_00402008)[local_c]) break;
    local_c = local_c + 0x1;
  }
  return 0x0;
}

```
pada func4, program akan melakukan xor pada 4 karakter pertama setelah index ke 7 dengan **DAT_00404050** , value nya adalah 0x5a , lalu hasil xornya di bandingkan dengan **DAT_00402008**
saya dapatkan valuenya dari ghidra, namun saya akan coba ambil dari gdb. prove value dari alamat DAT_00404050 dan DAT_00402008
```
pwndbg> x/x 0x404050
0x404050:       0x0000005a
pwndbg> hexdump 0x402008
+0000 0x402008  28 69 2c 05
```
bypass : lakukan xor pada value di **DAT_00402008** untuk mendapatkan string asli nya.


## analisis func5
hasil dekompilasi :
```C

undefined8 func5(char *param_1)

{
  bool bVar1;
  int local_c;
  
  local_c = 0x0;
  while( true ) {
    if (0x5 < local_c) {
      return 0x1;
    }
    bVar1 = false;
    switch(local_c) {
    case 0x0:
      bVar1 = *param_1 == '1';
      break;
    case 0x1:
      bVar1 = param_1[0x1] == 's';
      break;
    case 0x2:
      bVar1 = param_1[0x2] == '_';
      break;
    case 0x3:
      bVar1 = param_1[0x3] == 'f';
      break;
    case 0x4:
      bVar1 = param_1[0x4] == '0';
      break;
    case 0x5:
      bVar1 = param_1[0x5] == 'r';
    }
    if (!bVar1) break;
    local_c = local_c + 0x1;
  }
  return 0x0;
}
```

kali ini jauh lebih mudah karena input dibandingkan dengan char hardcoded berurutan yaitu : **'1s_f0r'**


## analisis func6
hasil dekompilasi
```C
undefined8 func6(long param_1)

{
  int iVar1;
  int local_c;
  
  local_c = 0x0;
  while( true ) {
    if (0x5 < local_c) {
      return 0x1;
    }
    iVar1 = (*(code *)PTR_ARRAY_00404068[(long)local_c * 0x2])(*(undefined1 *)(param_1 + local_c));
    if (iVar1 == 0x0) break;
    local_c = local_c + 0x1;
  }
  return 0x0;
}

```
ini sedikit merepotkan tapi sederhananya, func6 akan memanggil 6 fungsi secara berurutan, fungsi tersebut tersimpan sebagai array di **PTR_ARRAY_00404068** dan tiap index flag akan jadi argumennya.
daftar fungsi :
```C
bool FUN_004011f6(int param_1)
{
  return param_1 == 0x5f;

bool FUN_0040120d(int param_1)
{
  return param_1 == 0x33;
}

bool FUN_00401224(int param_1)
{
  return param_1 == 0x76;
}

bool FUN_0040123b(uint param_1)
{
  return (param_1 & 0x7fffffff) == 0x33;
}


bool FUN_00401256(int param_1)
{
  return param_1 == 0x72;
}


undefined8 FUN_0040126d(int param_1)
{
  undefined8 uVar1;
  
  if ((param_1 < 0x79) || (0x79 < param_1)) {
    uVar1 = 0x0;
  }
  else {
    uVar1 = 0x1;
  }
  return uVar1;
}

```
6 index terakhir bagian flag , masing masing index akan di validasi oleh satu fungsi yang berbeda. untungnya semuanya hardcoded dan tidak terlalu kompleks.
hasil ekstrak : [0x5f,0x33,0x76,0x33,0x72,0x79]

### note 
untuk index ke 6 ada fungsi dengan if else  if ((param_1 < 0x79) || (0x79 < param_1)), ini artinya if param_1 == 0x79 karena if ini hanya menghasillkan kondisi false jika param_1 lebih dari atau kurang dari 0x79. disimpulkan bahwa kondisi valid / true hanya saat param_1 == 0x79.


## exploit
langkah terakhir adalah mengumpulkan semua data dan menyusun flag asli. saya menggunakan bahasa python untuk membuat skrip nya.

```python3

def flag():
    val1 = 'A'
    val2 = 'THPCTF{'
    val3 = '}'
    
    return val2 + val1 + val3

def val4():
    leak = [0x28 ,0x69 ,0x2c, 0x05]
    key = 0x5a
    dec = [chr(i^key) for i in leak]

    return "".join(dec)

def val5():
    s = '1s_f0r'
    
    return s


def val6():
    leak = [0x5f,0x33,0x76,0x33,0x72,0x79]
    return "".join([chr(i) for i in leak])

string = val4() + val5() + val6()
flag = flag()

full_flag = flag.replace('A',string)
print(full_flag)
```
result : 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day2-struktur-biner)
└> python3 solver.py
THPCTF{r3v_1s_f0r_3v3ry}
┌[rotalactf]-[LAPTOP-6QMID52F]-(day2-struktur-biner)
└> ./thp_rev1
=== THP Crackme #1 ===
Enter flag: THPCTF{r3v_1s_f0r_3v3ry}
Access granted! Flag benar.
```

done

flag : **THPCTF{r3v_1s_f0r_3v3ry}**


kesimpulan : program ini menggunakan teknik obfuscation dalam fungsi fungsi validasi flagnya, namun semua data masih ada secara hardcoded di source code. sehingga peretas masih bisa mendapatkan flag dengan mengumpulkan data demi data lalu menyusunnya menjadi satu informasi utuh

saran perbaikan :
untuk password validasi sebaiknya menggunakan enkripsi satu arah daripada custom obfuscation. 

berikut contoh kode yang disederhanakan
```Python
x = input_user
if fungsi_enkripsi_hash(x) == <hasil_hash_dari_password_asli>:
```


## laporan kegiatan belajar 02-10-2026

- segment & section

segment adalah semacam pembagian lokasi memori mana yang akan di berikan alamat memory ram ketika program sedang di jalankan, tidak semua segment akan di alokasikan alamat memory saat running, hanya segment INTERP, LOAD, DAN DYNAMIC . sisanya sebagian besar hanya segment berisi metadata yang tidak memengaruhi alur eksekusi program binary.

- section
adalah bagian lokasi memory yang lebih kecil dan ada di dalam segment, contoh pada segment load terdapat section .text . section ini berisi kode instruksi yang tentunya jadi bagian utama program. dan wajib di alokasikan memori di ram saat sedang di jalankan.

selain itu section juga membagi hak akses program terhadap datanya. terdapat section .text yang dapat di read dan execute namun tidak bisa di write karena ini memengaruhi alur program. sementara ada section .rodata yang memiliki hak akses read only, program tidak bisa mengeksekusi apa yang ada di rodata. 

ini tentunya akan menjaga keamanan program dan mengurangi resiko terjadinya crash karena dengan adanya section ini, program dapat mengetahui bagian memori mana saja yang executable dan tidak. 

- contoh segment dan section

salah satu segment yang akan di alokasikan memori ketika program berjalan adalah LOAD / PT_LOAD . di dalam segment ini terdapat section .data , .text , .rodata , dan .bss
yang masing masing memiliki hak akses berbeda. 

contoh section pada binary **thp_rev1** :

pada binary tersebut, terdapat teks yang dicetak saat program dijalankan. string seperti itu akan disimpan di rodata, read only data.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day2-struktur-biner)
└> objdump -s -j .rodata thp_rev1

thp_rev1:     file format elf64-x86-64

Contents of section .rodata:
 402000 01000200 00000000 28692c05 54485043  ........(i,.THPC
 402010 54467b6e 30745f74 68335f66 6c34675f  TF{n0t_th3_fl4g_
 402020 73307272 797d0000 13f3ffff 27f3ffff  s0rry}......'...
 402030 3ff3ffff 57f3ffff 6ff3ffff 87f3ffff  ?...W...o.......
 402040 54485043 54467b00 3d3d3d20 54485020  THPCTF{.=== THP
 402050 43726163 6b6d6520 2331203d 3d3d0a45  Crackme #1 ===.E
 402060 6e746572 20666c61 673a2000 0a000000  nter flag: .....
 402070 4e696365 20747279 2e207374 72696e67  Nice try. string
 402080 7320616a 61206761 6b206375 6b757020  s aja gak cukup
 402090 3a290041 63636573 73206772 616e7465  :).Access grante
 4020a0 64212046 6c616720 62656e61 722e0041  d! Flag benar..A
 4020b0 63636573 73206465 6e696564 2e00      ccess denied..
```
kenapa rodata? karena string tersebut bersifat konstan dan tidak akan berubah apapun alur program nya. string literal ini tertulis secara hardcoded di source sehingga valuenya  tidak akan berubah,  maka karena itu program mengamankan data ini di section .rodata

contoh penggunaan section lain : .data

section ini memiliki hak akses rw- , read n write. artinya program bisa menulis dan membaca section data ini dan bebas menggantinya. karena value disini bisa berubah rubah maka program akan menggunakan section .data untuk menyimpan value dari sebuah variabel , dimana variabel kan sifatnya tidak konstan, dia relatif dan dapat berubah karena alur program dan untuk merubah data tentu butuh hak akses write. sehingga program akan menggunakan .data .

funfact, section ini termasuk ke kategori 'string printable' yang akan selalu dicetak ketika binary di eksekusi dengan tools strings
```
└> strings thp_rev1 | grep -i thp
THPCTF{n0t_th3_fl4g_s0rry}
THPCTF{
=== THP Crackme #1 ===
```

berikut contoh kode di program yang melibatkan variabel: for loop xoring
```C
undefined8 func4(long param_1)

{
  int local_c;
  
  local_c = 0x0;
  while( true ) {
    if (0x3 < local_c) {
      return 0x1;
    }
    if ((*(byte *)(param_1 + local_c) ^ DAT_00404050) != (&DAT_00402008)[local_c]) break;
    local_c = local_c + 0x1;
  }
  return 0x0;
}

```

ghidra :
```
// .data // SHT_PROGBITS  [0x404040 - 0x4040c7] // ram:00404040-ram:004040c7
```
untuk bisa melihat valuenya harus pakai gdb dan memasang break pada fungsi ini, 
```
pwndbg> hexdump 0x404050
+0000 0x404050  5a 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  │Z.......│........│
+0010 0x404060  00 00 00 00 00 00 00 00  f6 11 40 00 00 00 00 00  │........│..@.....│
+0020 0x404070  01 00 00 00 00 00 00 00  0d 12 40 00 00 00 00 00  │........│..@.....│
+0030 0x404080  02 00 00 00 00 00 00 00  24 12 40 00 00 00 00 00  │........│$.@.....│
+0000 0x404090  03 00 00 00 00 00 00 00  3b 12 40 00 00 00 00 00  │........│;.@.....│
+0010 0x4040a0  04 00 00 00 00 00 00 00  56 12 40 00 00 00 00 00  │........│V.@.....│
+0020 0x4040b0  05 00 00 00 00 00 00 00  6d 12 40 00 00 00 00 00  │........│m.@.....│
+0030 0x4040c0  0c 20 40 00 00 00 00 00  00 00 00 00 00 00 00 00  │..@.....│........│
```
lihat, ada value 5a, ini adalah kunci xor yang digunakan. dan ada beberapa data sisa cache instruksi lain.

contoh penggunaan .bss
bss adalah section yang mengurus buffer besar. dia read write karena merupakan tempat penyimpanan variabel juga, namun biasanya dipakai menyimpan variabel besar seperti buffer, (char buff[100]) dan sebagainya.

hal keren dari .bss adalah jika saja sebuah program memiliki buffer sebesar 10mb, ukuran binary tidak akan mencapai 10mb. karena bss hanya menyimpan sizeof dari buffer tersebut, dan baru menyediakan ukuran sebesar 10mb ketika program di jalankan. 

contoh kode :
```C
#include <stdio.h>

char buffer_rahasia[10 * 1024 * 1024];

int main() {
    printf("Program jalan!\n");
    
    // Coba isi byte pertama dan terakhir biar keliatan kalau RAM-nya benar-benar disiapin OS
    buffer_rahasia[0] = 'A';
    buffer_rahasia[sizeof(buffer_rahasia) - 1] = 'Z';
    
    printf("Isi indeks pertama: %c\n", buffer_rahasia[0]);
    printf("Isi indeks terakhir: %c\n", buffer_rahasia[sizeof(buffer_rahasia) - 1]);
    
    printf("Tekan Enter untuk keluar...");
    getchar();
    return 0;
}
```
karena buffer_rahasia di deklarasi tanpa inisiasi, dan dilakukan di global. maka program nanti akan langsung menyimpan buffer itu di section .bss. ukuran dari buffer itu sendiri adalah 10mb.

hasil compile : 
```
└> ls -lh 10mb
-rwxr-xr-x 1 rotalactf rotalactf 14K Oct  2 11:06 10mb
```

ukuranya masih di kisaran **14kb**

kemana 10mb nya? seperti yang ku jelaskan tadi , program hanya menyimpan sizeof nya di .bss , baru setelah program di jalankan, program akan mengalokasikan memori sebanyak 10mb untuk buffer tersebut.

hasil readelf .bss
```
  [26] .bss              NOBITS           0000000000403380  00002370
       0000000000a00020  0000000000000000  WA       0     0     32
```
lihat ukuran **0000000000a00020**, dalam hex itu adalah 10485792 , 

jika dihitung dari source code **$1024 * 1024 = 1.048.576 **
```
pwndbg> p/d 10485792 / 1048576
$2 = 10
```
pas 10 mb kan.
itu hanya sizeof, belum di alokasikan di ram


terakhir plt dan got.

fungsi fungsi libc seperti printf dan lainnya , tidak dipanggil dari binary tapi dari libc nya langsung, jika suatu file binary di compile dengan dynamic linking. maka program akan menggunakan section plt dan got untuk memanggil fungsi fungsi tersebut.plt sendiri menyimpan alamat dari got , namun saat pertama kali dijalankan, program belum me 'load' semua alamat libc di got. sehingga butuh bantuan dari file ld bawaan linux : /lib/ld-linux-x86-64.so.2 untuk x86-64 . sehingga saat got sudah terisi address dari alamat fungsi asli di libc. maka panggilan kedua tidak akan mengarahkan program ke /lib/ld-linux-x86-64.so.2 lagi sehingga instruksi berjalan jauh lebih cepat.

beda cerita jika sebuah binary di compile secara static, semua fungsi libc yang digunakan akan dimasukkan bersama program sehingga ukuranya membengkak, kelebihannya program tidak membutuhkan bantuan plt dan got lagi sehingga akan kompitabel di linux versi berapapun. 

partial & full relro

sebagian dan full memindahkan alamat got setelah relokasi alammat, full relro lebih aman karena akan memindah full alamat. sedangkan partial hanya setengah / sebagian
