#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <iostream>

#define BUFNUM 100

using namespace std;

/* Function for getting recognition result */
void Get_RecognitionResult( char *path ){

  FILE *fp;  
  char buffer1[BUFNUM], buffer2[BUFNUM];
  string Result;

  // Execute automatic speech recognition system (julius)
  if( !( fp = popen( path, "r") ) ){
    perror("ERROR:: popen");
    exit(EXIT_FAILURE);
  }
  
  while( memset(buffer1, 0, sizeof(buffer1)), fgets(buffer1, sizeof(buffer1) - 1, fp) != 0 ) {
    
    if( !strncmp(buffer1,"sentence1:", 10) ){
      strncpy( buffer2, &buffer1[16], strlen( buffer1 ) - 22 ); // Tips: "sentence1: silB  silE" --> 20 characters
      buffer2[ strlen( buffer1 ) - 22 ] = '\0';
      Result = string( buffer2 ); // Recognition result is substituted to [Result]
      cout << Result << endl;     // Output recognition result (Please remove if not necessary)
    }
  }

  pclose( fp );
}

/* Main function */
int main( void ){

  Get_RecognitionResult((char*)("./julius -C main.jconf"));

  return( 0 );
}
