# include <zmq.hpp> // https://github.com/zeromq/cppzmq

# include <iostream>
# include <iomanip>
# include <string>
# include <sstream>

# include <time.h>
# include <assert.h>
# include <stdio.h>
# include <stdarg.h>
# include <signal.h>
# include <sys/time.h>
# include <unistd.h>
# include <pthread.h>

// FOR FIFO
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>


// PUBLIC

// Works
void *Testfunk_recv(void *threadid) {
    long thread_id;
    thread_id = (long) threadid;
    const size_t size = 1024;
    zmq::message_t mottak(size);
    std::cout << "Thread started\nid:" << thread_id;
    pthread_exit(NULL);
    //auto res = socket.recv(mottak, zmq::recv_flags::none);
    //if (res){
    //    std::cout << mottak << '\n';
    //}
}

void *USB_Communication(void *threadid){
    long thread_id;
    thread_id = (long) threadid;
    zmq::context_t ctx1;
    zmq::socket_t socket_USB(ctx1, zmq::socket_type::pair);
    const std::string address_socket_HUB = "tcp://127.0.0.1:5679";
    sleep(1);
    socket_USB.connect(address_socket_HUB);
    std::cout << "Sockets made\n";
    zmq_msg_t melding;
    zmq_msg_init_size (&melding, 32);
    std::memset(zmq_msg_data (&melding), 'i', 32);
    //std::memcpy(zmq_msg_data (&melding), &"Test", 4);
    sleep(1);
    int rc = zmq_sendmsg(socket_USB, &melding, 0);
    std::cout << "Message sendt: " << rc << "\n";
    pthread_exit(NULL);

/*     //FIFO TEST
    char fifo2[] = "/tmp/FIFO_USB";
    //strcpy(fifo1, "/tmp/FIFO_USB");
    //fifo1 = "/tmp/FIFO_USB"; 
    mkfifo(fifo2, 0666); //Creates FIFO named FIFO_USB
    std::cout << "FIFO created!\n";
    int result2 = 42;
    std::cout << result2;
    std::cout << "Test3\n";
    result2 = open(fifo2, O_WRONLY);
    char teststring[] = "USB_COM";
    std::cout << "FIFO Opened\nWriting to FIFO\n";
    write(result2, teststring, strlen(teststring)+1);
    close(result2);
    std::cout << "FIFO Closed\n";
     */
}

int main(int argc, char const *argv[])
{
    zmq_msg_t mottak;
    zmq_msg_init (&mottak);
    zmq::context_t ctx1;
    zmq::socket_t socket_HUB(ctx1, zmq::socket_type::pair);
    const std::string address_socket_HUB = "tcp://127.0.0.1:5679";
    int tall = 2;

    //USB THREAD TEST 2
    int thread2_started;
    pthread_t thread_USB;
    thread2_started = pthread_create(&thread_USB, NULL, USB_Communication, (void*)&tall);
    socket_HUB.bind(address_socket_HUB);
    std::cout << "Start sleep\n";
    sleep(1);
    zmq_recvmsg(socket_HUB, &mottak, 0);
    uint8_t buff[32] = {0};
    printf((char*) zmq_msg_data(&mottak));
    std::cout << "Data recived:" << zmq_msg_data(&mottak) << "\n";
    std::memcpy(buff, zmq_msg_data (&mottak), 6);
    zmq_msg_close (&mottak);
    //printf("0x%X-%X-%X-%X\n",buff[0],buff[1], buff[2], buff[4]);
    std::cout << buff <<"\n";

    // USB THREAD TEST FIFO
/*     tall = 3;
    int thread2_started;
    pthread_t thread_USB;
    std::cout << "Starting USB Thread\n";
    thread2_started = pthread_create(&thread_USB, NULL, USB_Communication, (void*)&tall);
    if (thread2_started){
        std::cout << "Thread failed to start\n";
    }
    std::cout << "Test4\n";
    char *fifo1;
    strcpy(fifo1, "/tmp/FIFO_USB");
    //fifo1 = "/tmp/FIFO_USB"; 
    mkfifo(fifo1, 066zmq_msg_data (&melding)6); //Creates FIFO named FIFO_USB
    int result = 0;
    char teststring[80];
    std::cout << "While started\n";
    result = open(fifo1, O_RDONLY);
    read(result, teststring, 80);
    //std::cout << "Data from USB:\n" << teststring << "\n###\n";
    //std::cout << "Result from reading: \n" << result;
    close(result); */
    return 0;
}
