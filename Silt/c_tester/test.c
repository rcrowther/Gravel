// test with 
// gcc -masm=intel -S test.c -o test.asm
// -S compile only
// intel intel syntax (not att)
// test run,
// gcc -Wall test.c
// ./a.out
//  objdump -Mintel -d a.out
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

//int main()
//{
    ////char testStr[] = "pinky";
    ////printf("%s", testStr);
    ////long xx = 7;
    ////long x = 3;
    ////char testStr[] = "cool as tangerine, hot as coke";
    ////while (xx-- > 33) {
    ////printf("%ld\n", xx);
    ////};
    ////long arry[5] = {19, 10, 8, 17, 9};
    //struct Strut {
      //long id;
      //int value;
      //};  


    //struct Strut ex1;  
    //ex1.id = 6495700;
    //ex1.value = 77;
    //printf( "Ex1 id : %ld\n", ex1.id);
    //printf( "done\n");
    //printf(" ,");
    //return 0;
//}

//void testCall() 
//{
    //printf("%s\n", "block called!");
//}

//static const size_t str_builder_min_size = 32;

struct str_builder {
    char   *str;
    size_t  alloced;
    size_t  len;
};

typedef struct str_builder str_builder_t;

int main()
{
    int x = 5;
    //switch(x) {
      //case 1:
        //printf("%d" , 33);
        //break;
      //case 2:
        //printf("%d" , 55);
        //break;
      //default:
        //printf("%d" , 77);
    //}

    printf("block call?");
    //testCall();
    //long trip = 1;
       //switch(trip) {
      //case 1 :
         //printf("Is 1\n" );
         //break;
      //case 2 :
         //printf("Is 2\n" );
         //break;
      //case 3 :
         //printf("Is 3\n" );
         //break;
      //default :
         //printf("Default\n" );
   //}
    //str_builder_t *sb;

    //sb          = calloc(1, sizeof(*sb));
    //sb->str     = malloc(str_builder_min_size);
    //*sb->str    = '\0';
    //sb->alloced = str_builder_min_size;
    //sb->len     = 0;

    
    return 0;
}
