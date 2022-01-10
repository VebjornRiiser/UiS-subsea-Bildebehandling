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

uint8_t serial_melding[1] = {0};
uint8_t serialBuffer[11] = {0};
uint8_t serialBufferTeller = 0;
int test = 0;

/**
 * @brief test
 * 
 * @param serial_com 
 */
void read_serial_port(int serial_com) {
  read(serial_com, serial_melding, 1);
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
  std::cout << serial_com;
  while (1) {

    //std::cout << serial_com;
    //std::cout << "start av loop";
    if (test = read(serial_com, serial_melding, 1)) {

      std::cout << test;
      // Start byte
      if (serial_melding[0] == 0x03) {
        std::cout << "ok\n";
        // tøm buffer
        memset(serialBuffer, 0, 11);
        serialBufferTeller = 0;

      // Slutt byte
      } else if (serial_melding[0] == 0x06) {
        serialBuffer[serialBufferTeller] = serial_melding[0];
        serialBufferTeller = 0;

        // sett flagg data
        //std::cout << serialBuffer;

      // Data lenger enn forventa
      } else if (serialBufferTeller >= 12) {
        memset(serialBuffer, 0, 11);
        serialBufferTeller = 0;

      // Behandle data
      } else {
        //std::cout << serial_melding[0] << "Writing to buffer \n";
        serialBuffer[serialBufferTeller] = serial_melding[0];
        serialBufferTeller++;
      }
    } else {
      std::cout << "Test3";
    }
    //std::cout << serial_melding;
  }
  std::cout << "test\n";
}