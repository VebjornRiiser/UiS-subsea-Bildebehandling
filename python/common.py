from inspect import currentframe, getframeinfo
import subprocess
import math

# Print info om nåværende linje.
def ln(melding:str=""):
    cf = currentframe()
    print(f"Linjenummer: {cf.f_back.f_lineno}, {melding + ', ' if melding != '' else ''}fil: { getframeinfo(cf.f_back).filename.split('/')[-1] }")

def get_apu_temp(string_out=True):
    temperature = subprocess.check_output("sensors | grep \"Tdie\" | tr -s ' ' " " | cut -d ' ' -f 2", shell=True)[:-1].decode('utf-8')
    if string_out:
        return temperature
    else:
        return float(temperature.replace('°C', ''))


def calc_distance(dist, focal_len=400, camera_space=60): # Calculates distance to object using test data, needs position on object in two pictures
    """Regner ut distansen til et objekt. for stereo kamera

    Args:
        centers (_type_): Senterkoortdinat til objektet i begge bildene
        focal_len (float, optional): Focallength oppgitt i pixler. Defaults to 33.2.
        camera_space (int, optional): Distansen mellom kameraene i mm. Defaults to 60.

    Returns:
        int: Avstand i mm
    """
    #dist = abs(centers[0][0]-centers[1][0])
    if dist == 0:
        return 300
    #y =-0,000326267081189824000000000000x3 + 0,248885323144369000000000000000x2 - 61,946537053035200000000000000000x + 5 155,964477808620000000000000000000
    return int((-0.000326267081189824)*(dist**3) + 0.248885323144369*(dist**2) - 61.9465370530352*dist + 5155.96447780862) # cm
    #return int((3.631e-6 * (dist**4)) - (0.003035 * (dist**3)) + (0.9672 * (dist**2)) - (139.9 * dist) + 7862)
    #return int(((focal_len*camera_space)/dist))

class Cursor: #______/\______
    def __init__(self, line_len:int, spacing:int, offset:tuple) -> None: 
        self.line_len = line_len
        self.spacing = spacing
        self.offset = offset # (xpos, ypos) Normally center in a picture
        self.points = [
            (self.offset[0]-self.spacing-self.line_len, self.offset[1]),
            (self.offset[0]-self.spacing, self.offset[1]),
            (self.offset[0], self.offset[1]-self.spacing),
            (self.offset[0]+self.spacing, self.offset[1]),
            (self.offset[0]+self.spacing+self.line_len, self.offset[1])
        ]


    def rotate_point(self, x, y, angelrad):

        x -= self.offset[0]
        y -= self.offset[1]
        x1 = x
        y1 = y

        x = x1*math.cos(angelrad) - y1*math.sin(angelrad)
        y = x1*math.sin(angelrad) + y1*math.cos(angelrad)

        x += self.offset[0]
        y += self.offset[1]
        return [int(y),int(x)]

    def get_points(self, angel):
        point_list = []
        angelrad = math.radians(angel)
        for a in self.points:
            point_list.append(self.rotate_point(a[0], a[1], angelrad))
        return point_list
