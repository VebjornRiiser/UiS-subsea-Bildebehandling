#def mercury():
    # #init
    # context = zmq.Context()
    # network_socket = context.socket(zmq.PAIR)
    # network_socket.connect("tcp://127.0.0.1:6892")
    # print("STARTING SENDING\n")
    # while True:
    #     network_socket.send(b'TEST')
    #     time.sleep(1)


        # ZMQ socket INIT
        # Network socket recive
        #context = zmq.Context()
        #self.network_rcv_socket = context.socket(zmq.PAIR)

        # Network socket send
        #context2 = zmq.Context()
        #self.network_snd_socket = context.socket(zmq.REQ)
        # Waiting for TOPSIDE
        #self.network_snd_socket.connect(f'tcp://{self.connect_ip}:{self.connect_port}')



#######################################################
        #   GAMMAL SENDE BILDE FUNKSJON   #
#######################################################
        if f_video_feed:
            picture_send_pipe(crop_frame)
            start = time.time()
            #package = crop_frame.flatten().tobytes()
            _, pack = cv2.imencode('.jpg',crop_frame)
            pack = pack.tobytes()
            #pack = package#.tobytes()
            #package = np.array(package)
            #print(len(package[1]))
            #print(package[0])
            video_stream_socket.sendto(b'start', ("127.0.0.1", 6888))
            time.sleep(0.001)
            #print(len(pack))
            #video_stream_socket.sendto(pack, ("127.0.0.1", 6888))
            #print(len(pack))
            pack_len = len(pack)
            for x in range(6):
                if x*50000 < pack_len:
                    video_stream_socket.sendto(pack[(x*50000):(x+1)*50000],("127.0.0.1", 6888))
                else:
                    video_stream_socket.sendto(pack[(x*50000):-1],("127.0.0.1", 6888))
                    break
                #video_stream_socket.sendto(package[(x*61440):(x+1)*61440], ("127.0.0.1", 6888))
                #video_stream_socket.sendto(package[(x*61440):(x+1)*61440], ("127.0.0.1", 6888))
                time.sleep(0.0004)
            total_list.append(time.time()-start)
    connection.send("Quit")
    print(f'Median time per package:{mean(total_list)}\n Max time per package:{max(total_list)}')
    feed.release()
    cv2.destroyAllWindows()