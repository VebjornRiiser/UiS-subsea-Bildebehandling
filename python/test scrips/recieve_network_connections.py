from network_handler import Network


if __name__ == "__main__":
    network = Network(is_server=True)
    while True:
        data = network.receive()
        if data is not None:
            print(data)