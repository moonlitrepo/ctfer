# Strings Revenge

# analysis & exploit step by step

- mengidentifikasi file dengan memeriksa metadata dan menjalankannya. program ini meminta flagnya. ltrace tidak bisa dilakukan pada file ini.

<p align="center"> <img width="1919" height="492" alt="image" src="https://github.com/user-attachments/assets/a5e9c74f-7f5a-4b22-8040-28942f36796a" /> </p>


maka aku lanjutkan analisis dengan mendecompilenya menggunakan ghidra:

- karena file ini stripped maka tidak ada fungsi main, jadi aku pergi ke entry poin dan mencari fungsi utama nya : 
<p align="center" ><img width="80%" alt="image" src="https://github.com/user-attachments/assets/304e7372-e588-40b1-a14c-2fd3acaac44c" /> </p>

**FUN_004023aa()** :
```C

undefined8 FUN_004023aa(void)

{
  int iVar1;
  undefined8 uVar2;
  undefined1 local_38 [26];
  undefined1 local_1e;
  undefined1 local_16;
  undefined1 local_15;
  undefined1 local_14;
  undefined1 local_13;
  undefined1 local_12;
  undefined1 local_11;
  undefined8 local_10;
  
  uVar2 = FUN_00401d26(&local_16);
  uVar2 = FUN_0040257a(uVar2);
  FUN_00423c10(uVar2);
  uVar2 = FUN_00401ea6(&local_15);
  uVar2 = FUN_0040261e(uVar2);
  FUN_00423c10(uVar2);
  uVar2 = FUN_0040208e(&local_14);
  local_10 = FUN_004026c2(uVar2);
  uVar2 = FUN_0040218a(&local_13);
  uVar2 = FUN_00402766(uVar2);
  FUN_0041a920(uVar2,local_38);
  local_1e = 0;
  iVar1 = thunk_FUN_00433490(local_38,local_10);
  if (iVar1 == 0) {
    uVar2 = FUN_00402232(&local_12);
    uVar2 = FUN_0040280a(uVar2);
    FUN_00423c10(uVar2);
  }
  else {
    uVar2 = FUN_004022ea(&local_11);
    uVar2 = FUN_004028ae(uVar2);
    FUN_00423c10(uVar2);
  }
  return 0;
}

```

semua nama fungsi sudah dihilangkan secara agresif. namun masih bisa diperkirakan.

<p align="center"> <img width="75%"  alt="image" src="https://github.com/user-attachments/assets/ec4787c3-52e8-45a4-a9f9-b49f82e45ea8" />
</p>

variabel iVar1 adalah sebuah return value dari fungsi `thunk_FUN_00433490` yaitu 0. fungsi ini mirip dengan strcmp, atau memang strcmp. karena
jika melihat ke dokumentasi fungsi strcmp, 0 adalah sama dengan (string yang di masukkan bernilai sama). karena di fungsi utama ini hanya ada 1 percabangan if else, bisa di asumsikan
bahwa ini adalah fungsi yang membandingkan input ku dengan sesuatu. 

<p align = "center"><img width="80%"  alt="image" src="https://github.com/user-attachments/assets/48de5cdb-6040-4c7b-aee0-5cc15e6bde37" />
</p>

alamat call fungsi tersebut adalah `00402446` / `0x402446` dalam hex valid. tapi aku akan targetkan ke 1 alamat sebelumnya yaitu `0x402443` untuk melihat value dari register
rdi dan rsi yang menyimpan argumen dari strcmp nya. 

- aku melanjutkan solve dengan gdb

```
pwndbg> b *0x402443
Breakpoint 1 at 0x402443
pwndbg> r
Starting program: /home/rotalactf/reno/rev/LKS/stringsRevenge/chall
You cannot find this strings in your decompiler right? ^-^
Let's make this NOT TOO EASY but STILL EASY, what's the LKS flag for this challenge?
AAAAAAAAAAAAAAAAAAAAAAAAAAA
```

program menabrak breakpoint tepat setelah aku memasukkan input, maka tidak salah lagi bahwa itu adalah fungsi perbandingan. berikut adalah posisiku di breakpoint

```Assembly
   0x40243c:    lea    rax,[rbp-0x30]
   0x402440:    mov    rsi,rdx
=> 0x402443:    mov    rdi,rax
   0x402446:    call   0x401098
```

karena aku berhenti disini, maka instruksi mov rdi,rax belum tereksekusi sehingga value rdi masih kosong ,maka aku mengecek register rax dan rsi.

```
pwndbg> i r $rax
rax            0x7fffffffdd60      0x7fffffffdd60
pwndbg> x/s 0x7fffffffdd60
0x7fffffffdd60: 'A' <repeats 25 times>
```
input ku adalah argumen pertama, maka argumen kedua adalah string target.
```
pwndbg> i r $rsi
rsi            0x4db3f8            0x4db3f8
pwndbg> x/s 0x4db3f8
0x4db3f8:       "LKS{y0u_C_4n't_C++_m3???}"
```

done kah? 

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(stringsRevenge)
└> ./chall
You cannot find this strings in your decompiler right? ^-^
Let's make this NOT TOO EASY but STILL EASY, what's the LKS flag for this challenge?
LKS{y0u_C_4n't_C++_m3???}
Correct!
```

done

flag = **LKS{y0u_C_4n't_C++_m3???}**

sebenarnya karena aku menggunakan pwndbg , string flag sudah tercetak sejak aku menabrak bp. namun cara yang aku lakukan tadi lebih ke cara manual apabila gdb tidak dilengkapi
plugin seperti pwndbg atau gef.

<p align = "center"> <img width="1841" height="783" alt="image" src="https://github.com/user-attachments/assets/673b4438-18e6-42a0-8020-9d75e257f4ff" /> </p>

Tools :
- GDB
- Ghidra

