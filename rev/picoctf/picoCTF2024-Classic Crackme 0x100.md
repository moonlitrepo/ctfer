# picoCTF2026-Classic Crackme 0x100
hello guys welcome to my write up, chall ini cukup sulit dipahami jika pemahaman tentang bahasa C masih sedikit karena chall ini adalah enkripsi kustom yang dimana kita harus 
bisa memahami apa yang dilakukan program terhadap input kita. 
# overview
sesuai namanya challenge crackme ini cukup classic jika sudah dipahami dengan baik. chall ini akan mengenkripsi input kita dan mencocokkannya dengan password terenkripsi yang tertulis
secara hardcoded di source code program. aku melakukan bruteforce daripada menginversenya karena jika dilihat dari panjang string * alfabet jumlahnya masih sangat bruteforce-able

# recon 
<img width="498" height="401" alt="image" src="https://github.com/user-attachments/assets/6907b342-1a9e-4a26-87fa-2a431ee1acc6" />

aku diberi file program dan instance koneksi ke server. langsung saja aku download dan bongkar file tersebut. mulai dari melihat metadata dan menjalankan program tersebut.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(crackme100)
└> file crackme100
crackme100: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=b55ce0bee6b3e14b9124b881308f0c1f07f1b575, for GNU/Linux 3.2.0, with debug_info, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(crackme100)
└> ./crackme100
Enter the secret password: 67676767
FAILED!
```
kabar baik nya di metadata program ini tertulis not stripped alias isian programnya tidak disembunyikan oleh packer merepotkan.  

selanjutnya aku lanjutkan analisisnya menggunakan ghidra. tidak ada fungsi yang terlihat menarik jadi aku langsung liat fungsi main nya saja.

```C
int main(void)

{
  uint uVar1;
  int iVar2;
  size_t sVar3;
  char input [51];
  char output [51];
  int random2;
  int random1;
  char fix;
  int secret3;
  int secret2;
  int secret1;
  int len;
  int i_1;
  int i;
  
  builtin_strncpy(output,"qhcpgbpuwbaggepulhstxbwowawfgrkzjstccbnbshekpgllze",51);
  setvbuf(stdout,(char *)0x0,2,0);
  printf("Enter the secret password: ");
  __isoc99_scanf(&DAT_00402024,input);
  i = 0;
  sVar3 = strlen(output);
  for (; i < 3; i = i + 1) {
    for (i_1 = 0; i_1 < (int)sVar3; i_1 = i_1 + 1) {
      uVar1 = (i_1 % 0xff >> 1 & 0x55U) + (i_1 % 0xff & 0x55U);
      uVar1 = ((int)uVar1 >> 2 & 0x33U) + (uVar1 & 0x33);
      iVar2 = ((int)uVar1 >> 4) + input[i_1] + -0x61 + (uVar1 & 0xf);
      input[i_1] = (char)iVar2 + (char)(iVar2 / 0x1a) * -0x1a + 'a';
    }
  }
  iVar2 = memcmp(input,output,(long)(int)sVar3);
  if (iVar2 == 0) {
    printf("SUCCESS! Here is your flag: %s\n","picoCTF{sample_flag}");
  }
  else {
    puts("FAILED!");
  }
  return 0;
}
```

oke sepertinya fungsi main ini sudah menjelaskan seluruh akun program nya. jika aku bahas bagian pentingnya dari atas :
```C
builtin_strncpy(output,"qhcpgbpuwbaggepulhstxbwowawfgrkzjstccbnbshekpgllze",51);
```
program ini menyalin string tersebut ke variabel output. maka **output = qhcpgbpuwbaggepulhstxbwowawfgrkzjstccbnbshekpgllze**   
lanjut ke bagian inti enkripsinya : 

```C
  i = 0;
  sVar3 = strlen(output);
  for (; i < 3; i = i + 1) {
    for (i_1 = 0; i_1 < (int)sVar3; i_1 = i_1 + 1) {        <---baris 1----
      uVar1 = (i_1 % 0xff >> 1 & 0x55U) + (i_1 % 0xff & 0x55U);   <---baris 2----
      uVar1 = ((int)uVar1 >> 2 & 0x33U) + (uVar1 & 0x33);     <---baris 3----
      iVar2 = ((int)uVar1 >> 4) + input[i_1] + -0x61 + (uVar1 & 0xf);   <---baris 4----
      input[i_1] = (char)iVar2 + (char)(iVar2 / 0x1a) * -0x1a + 'a';   <---baris 5----
    }
  }
```

program ini melakukan perulangan sebanyak 3 kali baru melakukan enkripsi utamanya.  
untuk bagian setelah perulangan 3 kali tersebut, mulai dari baris 1:

1. program melakukan perulangan for sejumlah panjang output. **(karena sVar3 - strlen(output))** dan mengambil nilai indexnya 
2. uVar1 dibuat dengan **index output** yang di **modulus dengan 0xff**, bitnya digeser **ke kanan sekali**, lalu di **AND dengan 0x55**. hasilnya akan ditambah dengan operasi yang sama tapi tanpa pergeseran bit 
3. uVar1 di update lagi nilainya dengan **pergeseran bit sebanyak 2 kali ke kanan** lalu ditambah dengan nilai nya sendiri yang di **AND dengan 0x33**
4. iVar2 menyimpan value yang dihitung dari perhitungan variabel uVar1. hasil akhir uVar1 di **geser bitnya sebanyak 4 kali ke kanan** lagi, **dikurangi 0x61** , ditambah **uVar1 yang di AND dengan 0xf**
5. akhirnya index ke i_1 dari output akan di tambah dengan value iVar2 dan nilainya dikembalikan ke bentuk ascii lagi dengan menambahkan value ascii dari huruf a (0x61)

**kesimpulan dari program ini:**

program melakukan enkripsi kustom yang identik dengan caesar cipher (pergeseran) namun setiap index memiliki nilai pergeseran yang berbeda. dan enkripsi pegeseran ini dilakukan
sebanyak 3 kali. misal  
pesan = omaga
maka index 0 = o , index 1 = m dan seterusnya. dan program akan melakukan perhitungan untuk membuat proses value pergeseran (iVar2) dari perhitungan uVar1 menggunakan index pesan
lalu tiap index akan memiliki nilai / key pergeseran nya sendiri dan itu berbeda dengan index lain.  

misal
index 0 = key 0, index 1 = key 3
maka pesan dari index 0 digeser sebanyak 0 kali dan index 1 digeser sebanyak 3 kali. dan ini diulangi hingga 3 kali sehingga pesannya akan menjadi benar benar acak.  

kita sudah memahami program nya namun aku tidak menyelesaikannya dengan mencoba melakukan inverse dari enkripsi tersebut, namun aku mencoba melakukan bruteforce karena jika melihat 
karena hasil enkripsi tersebut terbatas pada huruf yang ada di alfabet saja karena sempat ada mod26 pada enkripsinya (alfabet kan ada 26 jadi jika angka hasil perhitungan melebihi
26 misal 27, pergeseran akan menjadi 1 lagi.


jika melihat panjang output "qhcpgbpuwbaggepulhstxbwowawfgrkzjstccbnbshekpgllze" **(50 karakter / index 0 - 49)** dikali jumlah alfabet (26) maka 
total kemungkinan yang bisa di bruteforce adalah 26*50 = **1300 kemungkinan** saja. jelas ini adalah angka yang sangat bruteforce-able.

jadi tujuan ku disini adalah membuat skrip solver yang melakukan bruteforce karakter per index, dan membuat program mencocokkan input ku yang di encrypt sebanyak 3 kali itu. jika salah satu
dari 26 alfabet cocok dengan output (hasil enkripsi password), maka percobaan bruteforce akan bergeser ke index ke 1. dan seterusnya hingga index terakhir, 49.

# exploit 
untuk membuat skripnya aku perlu mengubah proses enkripsi di source code bahasa c tersbut ke python. ini sedikit menantang karena beberapa sintaks yang berbeda atau bahkan tidak ada
versi sintaks serupa di python. namun aku berhasil membuatnya.


```Python

def encode_char(char,index):
  Var1 = (index % 0xff >> 1 & 0x55) + (index % 0xff & 0x55);
  Var1 = (int(Var1) >> 2 & 0x33) + (Var1 & 0x33);
  iVar2 = (int(Var1) >> 4) + ord(char) - ord('a') + (Var1 & 0xf);
  return chr((iVar2 % 26) + ord('a'))
```

selanjutnya aku perlu membuat skrip bruteforcenya

```Python
encoded_password = "qhcpgbpuwbaggepulhstxbwowawfgrkzjstccbnbshekpgllze"

def brute_force(passwd):
  string ='abcdefghijklmnopqrstuvwxyz'
  decoded = ''

  for index,karakter in enumerate(passwd):
    for alfabet in string:
      if encode_char(alfabet,index) == karakter:
        decoded += alfabet
        break
  return decoded

```

terakhir aku menjalankan mereka 3 kali agar enkripsi sesuai dan langsung mengirim hasil decode nya ke file programnya.

```Python
def main():  
  decoded = encoded_password
  for i in range(3):
    decoded = brute_force(decoded)

  io = process('./crackme100')
  io.sendlineafter(b'password: ',decoded.encode())
  data = io.recvall().decode()
  print(data)
  io.close()


if __name__ == "__main__":
  main()
```

berikut full programnya : 

```Python
from pwn import *
context.log_level = 'error'
SERVER = 'titan.picoctf.net'
PORT = 60141 

encoded_password = "qhcpgbpuwbaggepulhstxbwowawfgrkzjstccbnbshekpgllze"

def encode_char(char,index):
  Var1 = (index % 0xff >> 1 & 0x55) + (index % 0xff & 0x55);
  Var1 = (int(Var1) >> 2 & 0x33) + (Var1 & 0x33);
  iVar2 = (int(Var1) >> 4) + ord(char) - ord('a') + (Var1 & 0xf);
  return chr((iVar2 % 26) + ord('a'))



def brute_force(passwd):
  string ='abcdefghijklmnopqrstuvwxyz'
  decoded = ''

  for index,karakter in enumerate(passwd):
    for alfabet in string:
      if encode_char(alfabet,index) == karakter:
        decoded += alfabet
        break
  return decoded


def main():  
  decoded = encoded_password
  for i in range(3):
    decoded = brute_force(decoded)

  # io = process('./crackme100')
  io = remote(SERVER,PORT)
  io.sendlineafter(b'password: ',decoded.encode())
  data = io.recvall().decode()
  print(data)
  io.close()


if __name__ == "__main__":
  main()
```
saatnya eksekusi 


```
┌[rotalactf]-[LAPTOP-6QMID52F]-(crackme100)
└> python3 inv_cipher.py
SUCCESS! Here is your flag: picoCTF{s0lv3_angry_symb0ls_4699696e}
```
Done 
FLAG : **picoCTF{s0lv3_angry_symb0ls_4699696e}**

# conclusion
sebenarnya ini merupakan enkripsi / encode kustom yang cukup klasik karena masih rentan di bruteforce. tidak perlu repot repot melakukan inverse karena ini hanya pergeseran yang 
memiliki kerterbatasan di alfabet saja (26 kemungkinan). namun tetap saja memerlukan pemahaman yang baik tentang bahasa pemrograman C dan python karena untuk memindahkan prosesn enkripsi
atau encoding ini dari C ke python memiliki tantangan tersendiri bagi sebagian orang termasuk aku.








