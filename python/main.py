from mercury import Mercury
from theia import Theia


# Our main loop for both programs
def main_loop():
    m = Mercury()
    t = Theia()
    while(1):
        if m.status_flag_list[3]:
            print("Camera function stopped")