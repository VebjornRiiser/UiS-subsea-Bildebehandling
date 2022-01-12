/**
 * @file topside2can.cpp
 * @author ArcticMeteor246 (mats1809@gmail.com)
 * @brief 
 * @version 0.1
 * @date 2022-01-05
 * 
 * @copyright Copyright (c) 2022
 * 
 */

# include <stdio.h>
# include <string.h>
# include <iostream>
//# include <thread>

#ifdef linux //Includes for Linux
#include <fcntl.h> // Contains file controls like O_RDWR
#include <errno.h> // Error integer and strerror() function
#include <termios.h> // Contains POSIX terminal control definitions
#include <unistd.h> // write(), read(), close()
#endif
#include <unistd.h>

#ifdef _WIN32
#include <windows.h>
#endif



#ifdef _WIN32

#endif

char serialBuffer[16] = {0};
int serialBufferTeller = 0;
struct termios tty;

#define BLEN    48
unsigned char rbuf[BLEN];
unsigned char *rp = &rbuf[BLEN];
int bufcnt = 0;

/* get a byte from intermediate buffer of serial terminal */
static unsigned char getbyte(int serial_com)
{
    if ((rp - rbuf) >= bufcnt) {
        /* buffer needs refill */
        bufcnt = read(serial_com, rbuf, BLEN);
        if (bufcnt <= 0) {
            /* report error, then abort */
            printf("OBS, ingen data!\n");
        }
        rp = rbuf;
    }
    return *rp++;
}

/**
 * @brief Hovedfunksjon for kommunikasjon
 * 
 * @return int 
 */
int main( void ) {
  #ifdef linux
    std::cout << "Connecting to USB...\n";
    int serial_com = open("/dev/ttyACM0", O_RDWR);
  #endif
  if(tcgetattr(serial_com, &tty) != 0) {
    printf("Error %i from tcgetattr: %s\n", errno, strerror(errno));
  }
  tty.c_lflag &= ~ICANON;
  tty.c_lflag &= ~ECHO; // Disable echo
  tty.c_lflag &= ~ECHOE; // Disable erasure
  tty.c_lflag &= ~ECHONL; // Disable new-line echo
  tty.c_lflag &= ~ISIG; // Disable interpretation of INTR, QUIT and SUSP
  tty.c_iflag &= ~(IGNBRK|BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL); // Disable any special handling of received bytes
  tty.c_oflag &= ~OPOST; // Prevent special interpretation of output bytes (e.g. newline chars)
  tty.c_oflag &= ~ONLCR; // Prevent conversion of newline to carriage return/line feed

  // Save tty settings, also checking for error
  if (tcsetattr(serial_com, TCSANOW, &tty) != 0) {
      printf("Error %i from tcsetattr: %s\n", errno, strerror(errno));
  }


  std::cout << serial_com;
  while (1) {

    // Ny startbyte?
    while (getbyte(serial_com) != 0x02) {

    }

    // Restart teller
    serialBufferTeller = 0;
    memset(serialBuffer, 0, 12);

    // Les data til sluttbyte er funnet, avbryt etter 12 byte
    while ( (serialBuffer[serialBufferTeller] = getbyte(serial_com)) != 0x03 ) {
        
        /* accumulate data until end found */ 
        serialBufferTeller++;
        if (serialBufferTeller >= 12) {
          memset(serialBuffer, 0, 12);

          std::cout << serialBuffer;
          break;
        }
    }
    // Print funnet data
    //std::cout << serialBuffer;
  }
  std::cout << "test4\n";
}