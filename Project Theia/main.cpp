/**
 * @file main.cpp
 * @author Christoffer
 * @brief 
 * @version 0.1
 * @date 2022-01-06
 * 
 * @copyright Copyright (c) 2022
 * 
 */

# include <opencv2\opencv.hpp>
# include <thread>
# include <camera.hpp>


/**
 * @brief Main Camera loop
 * 
 * @return int 
 */

int main() {
    std::thread cameratrad1 (start_camerafeed, 1);
    cameratrad1.join();
    //start_camerafeed(1);
}