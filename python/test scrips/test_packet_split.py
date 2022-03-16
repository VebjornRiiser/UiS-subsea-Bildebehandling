import json
def network_callback(data: bytes) -> None:
    for message in bytes.decode(data,"utf-8").split("*"):
        if message == '':
            continue
        if message == 'heartbeat':
            continue
        else:
            if isinstance(message, list):
                return
            message = json.loads(message)
            for item in message:
                if item[0] < 500:
                    print(f"{item = }")
                        #self.serial.write(serial_package_builder())
                    #else:
                     #   self.network_handler.send(create_json('error', 15149))
                else:
                    if isinstance(item[1], str):
                        if item[1].lower() == "tilt":
                            pass
                        elif item[1].lower() == "toggle_front":
                            pass
                            #answ = self.thei.toggle_front()
                            #if not answ:
                             #   self.network_handler.send(create_json('error', 15152))
                    else:
                        print(f"{item[1] = }")
mld = [[70,[161,26,435]],[161,[65]]]

mld = bytes(json.dumps(mld), "utf-8")
seperator = bytes("*", "utf-8")
heartbeat = bytes("heartbeat", "utf-8")
whole = mld+seperator+heartbeat+seperator
print(whole)
network_callback(whole)