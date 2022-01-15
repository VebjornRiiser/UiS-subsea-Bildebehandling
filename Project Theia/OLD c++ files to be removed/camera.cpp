
# include <iostream>
# include <opencv2\opencv.hpp>
# include <thread>



int start_camerafeed(int cameraid) {
     cv::VideoCapture cap(cameraid);
     double dWidth = cap.get(cv::CAP_PROP_FRAME_WIDTH); //get the width of frames of the video
     double dHeight = cap.get(cv::CAP_PROP_FRAME_HEIGHT); //get the height of frames of the video

    std::cout << "Resolution of the video : " << dWidth << " x " << dHeight << "\n";

    std::string window_name = "My Camera Feed";
    cv::namedWindow(window_name); //create a window called "My Camera Feed"
 
  while (true)
 {
  cv::Mat frame;
  bool bSuccess = cap.read(frame); // read a new frame from video 

  //Breaking the while loop if the frames cannot be captured
  if (bSuccess == false) 
  {
   std::cout << "Video camera is disconnected \n";
   std::cin.get(); //Wait for any key press
   break;
  }

  //show the frame in the created window
  imshow(window_name, frame);

  //wait for for 10 ms until any key is pressed.  
  //If the 'Esc' key is pressed, break the while loop.
  //If the any other key is pressed, continue the loop 
  //If any key is not pressed withing 10 ms, continue the loop 
  if (cv::waitKey(10) == 27)
  {
   std::cout << "Esc key is pressed by user. Stoppig the video \n";
   break;
  }
 }

 return 0;


};