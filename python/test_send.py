from network_handler import Network


if __name__ == "__main__":
    network = Network(is_server=False, port=6969, connect_addr='10.0.0.2')
    while True:
        network.send(b'123asd')