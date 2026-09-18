# crackmes.one-Mazzotti's Getting started keygen

# overview 
<img width="746" height="336" alt="image" src="https://github.com/user-attachments/assets/f91600c7-6b1b-4e76-a544-9a2aa9ccf1dd" />

chall ini fokus pada pembuatan keygen dan tidak memiliki flag. namun cukup mudah untuk membuatnya karena hanya melibatkan xor sederhana.

# analysis & exploit
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(getting-started-keygen)
└> file getting_started_keygen
getting_started_keygen: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=226fff4aea936ab7426bf11dcd1e334c1e053104, for GNU/Linux 3.2.0, stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(getting-started-keygen)
└> ./getting_started_keygen
Enter a string of characters (no spaces):
hello
Enter correct number (no spaces):
12345
Send help pls.
```

program ini symbolnya disembunyikan , terbukti dari metadatanya dimana tertulis stripped disitu. jadi aku coba masukkan ke ghidra

```C++

undefined8 FUN_001011f0(void)

{
  int iVar1;
  ostream *poVar2;
  long in_FS_OFFSET;
  int local_7c;
  undefined1 *local_78;
  long local_70;
  undefined1 local_68 [16];
  string local_58 [40];
  long local_30;
  
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  local_78 = local_68;
  local_68[0] = 0;
  local_70 = 0;
  poVar2 = std::operator<<((ostream *)std::cout,"Enter a string of characters (no spaces): ");
  FUN_00101430(poVar2);
  std::operator>>((istream *)std::cin,(string *)&local_78);
  if (5 < local_70 - 5U) {
    std::operator<<((ostream *)std::cout,"Bro, what are you trying to do?");
    FUN_00101430();
                    /* WARNING: Subroutine does not return */
    exit(0);
  }
  poVar2 = std::operator<<((ostream *)std::cout,"Enter correct number (no spaces): ");
  FUN_00101430(poVar2);
  std::istream::operator>>((istream *)std::cin,&local_7c);
  std::__cxx11::string::string(local_58,(string *)&local_78);
  iVar1 = FUN_001014b0(local_58);
  std::__cxx11::string::_M_dispose();
  if (local_7c == iVar1) {
    poVar2 = std::operator<<((ostream *)std::cout,"OMG! You did it! :3");
  }
  else {
    poVar2 = std::operator<<((ostream *)std::cout,"Send help pls.");
  }
  FUN_00101430(poVar2);
  std::__cxx11::string::_M_dispose();
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    return 0;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}
```

ternyata program ini dibuat dari bahasa C++. walaupun symbols dari program ini disembunyikan tapi aku tetap bisa dengan mudah menemukan fungsi main nya karena di program ini hanya 
ada beberapa fungsi saja, fungsi main ada di `FUN_001011f0`

ternyata program ini memiliki syarat kondisi pada input pertama, terlihat di 
```C++
 if (5 < local_70 - 5U) {
    std::operator<<((ostream *)std::cout,"Bro, what are you trying to do?");
    FUN_00101430();
                    /* WARNING: Subroutine does not return */
    exit(0);
  }
```
ini akan membatasi panjang input kita yaitu minimal 5 dan maksimal 10 karakter. 

selanjutnya adalah potongan program yang sangat krusial, bagian compare dan kondisi win :
```C++
  iVar1 = FUN_001014b0(local_58);
  std::__cxx11::string::_M_dispose();
  if (local_7c == iVar1) {
    poVar2 = std::operator<<((ostream *)std::cout,"OMG! You did it! :3");
```
local_58 = input string (input pertama)
local_7c = input angka (input kedua)

local_58 akan dimasukkan kedalam fungsi yang belum diketahui dan menghasilkan ivar1. lalu ivar1 dibandingkan dengan local_7c.

jadi kita harus menebak apa hasil perhitungan yang  dilakukan fungsi `FUN_001014b0` kepada string kita , dan memasukkannya ke input kedua dalam bentuk angka. 

untuk mengetahuinya aku masuk ke fungsi `FUN_001014b0`
```C++
int FUN_001014b0(long *param_1)

{
  char *pcVar1;
  uint *puVar2;
  long lVar3;
  int iVar4;
  
  if (param_1[1] != 0) {
    lVar3 = 0;
    iVar4 = 0;
    do {
      pcVar1 = (char *)(*param_1 + lVar3);
      puVar2 = &DAT_00104020 + lVar3;
      lVar3 = lVar3 + 1;
      iVar4 = iVar4 + ((int)*pcVar1 ^ *puVar2);
    } while (param_1[1] != lVar3);
    return iVar4;
  }
  return 0;
}

```

ternyata fungsi ini melakukan decode terhadap string yang kita masukkan. tiap index akan di xor dengan key yang ada di `&DAT_00104020` secara berurutan. lalu jumlahnya
diakumulasikan menjadi 1 bilangan. berikut key yang sudah aku ekstrak dari `&DAT_00104020` :
```
0x4, 0x4f, 0x81, 0xab, 0xfe, 0x7b, 0xe0, 0xcc, 0x46 , 0x35
```
untuk membuat keygennya aku menggunakan python
```Python

def keygen():
    key = [0x4, 0x4f, 0x81, 0xab, 0xfe, 0x7b, 0xe0, 0xcc, 0x46 , 0x35]
    result = 0
    for i in range(len(string)):
        xored = ord(string[i]) ^ key[i]
        result += xored        
    return result


string = input("enter string : ")
print(keygen())
```
<img width="422" height="162" alt="image" src="https://github.com/user-attachments/assets/819c7a6c-1224-4013-819a-4b6170998862" />

dengan skrip python di atas semua input kita akan di xor dengan key yang tersedia secara hardcoded di source code file program tersebut dan menghasilkan 1 bilangan desimal
sebagai key untuk input ke 2 nya. 

