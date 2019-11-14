// test with gcc -masm=intel -S test.c -o test.asm
// -S compile only
// intel intel syntax (not att)
#include <stdio.h>
#include <string.h>

int foobar()
{
    //long xx = 432;

    char testStr[] = "cool as tangerine, hot as coke";
    //printf("%ld\n", xx);
    //return xx;
}

int main()
{
    return foobar();
}
