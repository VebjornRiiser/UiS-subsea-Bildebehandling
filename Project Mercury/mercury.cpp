/**
 * @file mercury.cpp
 * @author ArcticMeteor246 (mats1809@gmail.com)
 * @brief Program som håndterer kommunikasjonen mellom forskjellige program som kjører i ROV hjernen
 * @version 0.1
 * @date 2022-01-06
 * 
 * @copyright Copyright (c) 2022
 * 
 */

#include <opencv4/opencv2/opencv.hpp>

using namespace cv;

using namespace std;

int main() {

Mat image;

namedWindow("Display window");/*  */

VideoCapture cap(0);

if (!cap.isOpened()) {

cout << "cannot open camera";

}

while (true) {

cap >> image;

imshow("Display window", image);

waitKey(25);

}

return 0;

}

