#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <iostream>

#include <ros/ros.h>
#include <std_msgs/String.h>

#define BUFNUM 100

using namespace std;

ros::Publisher result_pub;

/* Function for getting recognition result */
void Get_RecognitionResult( char *path ){

  FILE *fp;  
  char buffer1[BUFNUM], buffer2[BUFNUM];
  string Result;
  std_msgs::String result;

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
      result.data = Result;
      result_pub.publish(result);
    }
  }

  pclose( fp );
}

/* Main function */
int main(int argc, char **argv){

  ros::init(argc, argv, "as_julius_english");
  ros::NodeHandle nh;

  result_pub = nh.advertise<std_msgs::String>("/julius/speech2text/en",10);

//  Get_RecognitionResult((char*)("./julius -C main.jconf"));
  Get_RecognitionResult((char*)("/home/ema/robocup2018_education/src/as_julius_english/src/julius -C /home/ema/robocup2018_education/src/as_julius_english/src/main.jconf")); 

  return( 0 );
}
