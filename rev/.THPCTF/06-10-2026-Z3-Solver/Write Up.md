# Z3 Solver

# deskripsi
Nama Challenge : mathme  
point : -  
Kategori : Reverse Engineering
File terlampir : [mathme](mathme)

FLAG : **PRALKS{18_7_6_3_9_12_255_167}**

## Note
chall ini adalah buatan claude ai, namun spesifikasi dan kualitas chall sudah lebih dari cukup untuk digunakan belajar dasar teknik _reconstruct algorithm_ dan penggunaan _Z3 Solver_

## Lingkungan
OS: Ubuntu 24.04.5 LTS (Noble Numbat) x86_64  
Kernel: Linux 6.6.87.2-microsoft-standard-WSL2

## Ringkasan
chall ini memiliki 5 persamaan yang harus di selesaikan. setiap persamaan  yang telah diselesaikan merupakan bagian dari flag tersebut. beberapa memang bisa diselesaikan secara manual. namun saya akan menggunakan pendekatan automasi menggunakan _python libc_ **z3** yang jauh lebih andal dalam menyelesaikan persamaan matematika baik itu sederhana maupun kompleks.


## analisis awal
saya awali dengan mencari informasi metadata serta _surface behavior_ (perilaku permukaan) dari program ini.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day6-Z3-solver)
└> file level2
level2: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=a324704cf63c6d8dc4a00101e19a2da3c2ae958e, for GNU/Linux 3.2.0, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(day6-Z3-solver)
└> ./level2
Level 1 - masukkan x: 11
  Level 1 gagal.
Level 2 - masukkan a b: 2
2
  Level 2 gagal.
Level 3 - masukkan p q r: 2
2
2
  Level 3 gagal.
Level 4 - masukkan t (0-255): 2
  Level 4 gagal.
Level 5 - masukkan k: 2
  Level 5 gagal.

Belum semua level lolos, flag belum keluar.
```
Observasi :
- Program merupakan file elf x86-64. kabar baiknya nama fungsi program ini tidak disembunyikan.(not stripped) ini akan memudahkan saya dalam melakukan analisis nanti.
- saat dijalankan, program ini meminta beberapa input untuk nilai variabel. saya masukkan angka random dan tentu saja, semuanya salah.
- walaupun input saya salah, program tetap naik level , total terdapat 5 level dan asumsi saya flag hanya keluar jika semua angka yang dimasukkan itu benar.
- setiap angka memiliki validasi sendiri yang semuanya harus bernilai _true_ agar flag dicetak

untuk memverifikasi beberapa asumsi saya di atas, saya lanjutkan _static analysis_ menggunakan ghidra dan mendekompilasi file ini.

# _Ghidra static analysis & Reconstruct algorithm_ 
menggunakan Ghidra , setelah saya _upload_ file program nya saya tidak melihat nama fungsi yang menarik, jadi saya mengambil langkah untuk langsung menganalisis **main()** _function_ nya:

dekompilasi fungsi main (hasil _reconstruct algorithm_):
```C
#include <stdio.h>

int main(void){
  int x; 
  int a;
  int b;
  int p;
  int q;
  int r;
  unsigned int t;
  unsigned int k;
  int valid ;

  
  printf("Level 1 - masukkan x: ");
  scanf("%d",&x);
  if (x == 18) {
    puts("  Level 1 lolos!");
  }
  else {
    puts("  Level 1 gagal.");
    valid = 0;
  }

  printf("Level 2 - masukkan a b: ");
  scanf("%d %d",&a,&b);
  if ((b + a * 2 == 20) && (a - b == 1)) {
    puts("Level 2 lolos!");
  }
  else {
    puts("Level 2 gagal.");
    valid = 0;
  }

  printf("Level 3 - masukkan p q r: ");
  scanf("%d %d %d",&p,&q,&r);
  if ( p < 1 || 99 < p || r + p + q != 24 || p * 3 != q || p + q != r ){
    puts("  Level 3 gagal.");
    valid = 0;
  }
  else {
    puts("  Level 3 lolos!");
  }

  printf("Level 4 - masukkan t (0-255): ");
  scanf("%u",&t);
  if ((t < 256) && ((char)t == -1)) {
    puts("  Level 4 lolos!");
  }
  else {
    puts("  Level 4 gagal.");
    valid = 0;
  }

  printf("Level 5 - masukkan k: ");
  scanf("%u",&k);
  if ((k >> 4 == 10) && (k == 167)) {
    puts("  Level 5 lolos!");
  }
  else {
    puts("Level 5 gagal.");
    valid = 0;
  }

  if (valid == 0) {
    puts("\nBelum semua level lolos, flag belum keluar.");
  }
  else {
    printf("\nFLAG: PRALKS{%d_%d_%d_%d_%d_%d_%u_%u}\n",x,a,b,p,q,r,t,k);
  }

  return 0;
}

```
analisis singkat :
- berdasarkan referensi format string yang digunakan. variabel x,a,b,p,q,r di cetak oleh printf dengan format string %d, dimana %d adalah format string yang digunakan untuk _signed int_. ini alasan saya mendeklarasikannya sebagai int. (walaupun sebelumnya tidak ada error saat proses dekompile jika variabel tersebut tetap saya deklarasikan sebagai uint) 
- dua variabel terakhir : t,k di cetak menggunakan format string %u : _unsigned int_. kebetulan juga variabel tersebut memang sudah dideklarasikan sebagai uint oleh ghidra.
- selanjutnya saya hapus pointer yang berhubungan dengan _canary_ karena tidak relevan , selain itu juga karena cukup sulit menulis ulangnya. 

permasalahan utama :
- tiap tiap levelnya memiiliki persamaan dimana value dari persamaan tersebut merupakan bagian dari flag. jika semua persamaan diselesaikan dengan benar maka semua nya akan digabung menjadi satu string flag. ini dibuktikan pada baris terakhir program bagian printf():
```C
printf("\nFLAG: PRALKS{%d_%d_%d_%d_%d_%d_%u_%u}\n",x,a,b,p,q,r,t,k);
```
alasan kenapa saya tidak mendapatkan flag padahal pada percobaan pertama berhasil menyentuh level5 adalah karena walaupun input tidak valid / tidak menyelesaian persamaan, program tetap naik level namun dengan return nilai valid = 0 , sedangkan syarat untuk print flag adalah else dari valid = 0. 

# analisis lanjutan
saya mulai dengan menganalisis level 1 , persamaannya adalah x = 18 (dari if (x == 18)). ini cukup mudah, jadi saya langsung coba masukkan nilai 18 itu ke level 1.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day6-Z3-solver)
└> ./decompile
Level 1 - masukkan x: 18
  Level 1 lolos!
Level 2 - masukkan a b: ^C
```
lolos, tapi masih ada 4 level lagi.

saya kumpulkan semua logika _if_ (persamaan) agar lebih mudah di analisis.
berikut persamaan nya :
```C
level 1 : (x == 18)
level 2 : (b + a * 2 == 20) && (a - b == 1)
level 3 : ( p<1 || 99<p || r+p+q != 24 || p*3 != q || p+q != r )
level 4 : (t < 256) && ((char)t == -1)
level 5 : (k >> 4 == 10) && (k == 167)
```
beberapa bisa di hitung manual atau menggunakan skrip python, namun langkah terbaik untuk menangani kasus persamaan seperti ini adalah menggunakan skrip _python_ + _lib z3 Solver_.

## Langkah Exploitasi 

```python
from z3 import *
from pwn import *

key = []

def l1():
    s = Solver()
    print("[+] l1 : sat")
    key.append(str(18).encode())# hasil dekompilasi ghidra sudah tertulis 18. asumsi ini merupakan free key , atau memang sebelumnya ada persamaan namun sudah di selesaikan oleh dekompiler ghidra sendiri.

def l2():
    s = Solver()
    a,b = BitVecs('a b',32)
    s.add(b+a*2 == 20 , a-b ==1)
    if s.check() == sat:
        print("[+] l2 : sat")
        key.append(str(s.model()[a].as_long()).encode())
        key.append(str(s.model()[b].as_long()).encode())
    else:
        print("[-] l2 : unsat")

def l3():
    s = Solver()
    p,q,r = BitVecs('p q r',32)
    s.add(UGE(p,1),ULE(p,99),r + p + q == 24 , p * 3 == q , p + q == r) # sebelumnya adalah kondisi gagal namun persamaan itu bisa ditulis ulang menjadi kondisi sama dengan
# menghapus p<1 dan 99<p. memang ini work sebelumnya namun persamaannya tanpa batas itu akan menghasillkan value unik, kebetulan sekali yang dipilih oleh z3 solver adalah
# yang pertama kali ia selesaikan, untuk mengembalikan batas ini sehingga tiap variabel hanya memiliki 1 penyelesaian cukup mennggunakan perbandingan dalam unsigned. UGO & # ULE (Unsigned Greater Equal) dan (Unsigned Less Equal)
    if s.check() == sat:
        print("[+] l3 : sat")
        key.append(str(s.model()[p].as_long()).encode())
        key.append(str(s.model()[q].as_long()).encode())
        key.append(str(s.model()[r].as_long()).encode())
    else:
        print("[-] l3 : unsat")
        return None

def l4():
    s = Solver()
    t = BitVec('t',32)
    s.add(ULT(t,256))  # unsigned less than, digunakan untuk perbandingan kurang dari jika angka nya bertipe data unsigned int
    s.add(Extract(7,0,t) == -1) # mengambil tepat 8 bit terakhir  (least significant byte) (1 byte terakhir dari 4 byte) untuk dibandingkan dengan -1
    if s.check() == sat:
        print("[+] l4 : sat")
        key.append(str(s.model()[t].as_long()).encode())
    else:
        print("[-] l4 : unsat")
        return None

def l5():
    s = Solver()
    k = BitVec('k',32)
    s.add(LShR(k,4) == 10 , k == 167)  # Logical Shift Right, pada operasi pergeseran ini, nilai bit paling kiri akan di isi oleh nol. cocok untuk tipe data unsigned 
    if s.check() == sat:
        print("[+] l5 : sat")
        key.append(str(s.model()[k].as_long()).encode())
    else:
        print("[-] l5 : unsat")
        return None


l1();l2();l3();l4();l5()

p = process("./decompile")
print("="*50)
for i in key:
    print("KEY FOUND : " ,text.bold_green(i.decode()))
    p.sendline(i)
print("="*50)
print(p.recv().decode())
p.close()

# semua tipe data di solver di deklarasikan dengan BitVec(x,32), saya menggunakan 32 bit karena semua tipe data yang ditampilkan hasil dekompilasi adalah int, baik signed
# atau tidak, dan ukuran tipe data int adalah 4 byte, (32 bit)

```
result : 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(try)
└> python3 solver3.py
[+] l1 : sat
[+] l2 : sat
[+] l3 : sat
[+] l4 : sat
[+] l5 : sat
[+] Starting local process './level2': pid 49207
KEY FOUND :  18
KEY FOUND :  7
KEY FOUND :  6
KEY FOUND :  3
KEY FOUND :  9
KEY FOUND :  12
KEY FOUND :  255
KEY FOUND :  167

Level 1 - masukkan x:   Level 1 lolos!
Level 2 - masukkan a b:   Level 2 lolos!
Level 3 - masukkan p q r:   Level 3 lolos!
Level 4 - masukkan t (0-255):   Level 4 lolos!
Level 5 - masukkan k:   Level 5 lolos!

FLAG: PRALKS{18_7_6_3_9_12_255_167}

[*] Process './level2' stopped with exit code 0 (pid 49207)
```
flag : **PRALKS{18_7_6_3_9_12_255_167}**

## kesimpulan
program ini memiliki persamaan yang sebenarnya cukup sulit di selesaikan secara manual. maka sangat diperlukan pemahaman dasar dalam bahasa _python_ serta penggunaan _library z3 solver_ dalam penyelesaian persamaannya. automasi bukan satu satunya langkah yang bisa menyelesaikan _challenge_ ini, namun automasi adalah cara paling efisien baik dalam segi waktu dan kemudahan menyelesaikan persmasalahan matematika kompleks.
