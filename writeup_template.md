[//]: # (Image References)

[image1]: ./output_images/annotate.png "Final overlayed image"
[image2]: ./output_images/calibration_img.png "Chessboard image with corners"
[image3]: ./output_images/dewarp_overlay.png "Dewarped image with lane overlay"
[image4]: ./output_images/histogram.png "Histogram"
[image5]: ./output_images/polyfit.png "Polyfit lane lines"
[image6]: ./output_images/src_warp_points.png "Source warp points"
[image7]: ./output_images/undistort_chessboard.png "Undistorted chessboard image"
[image8]: ./output_images/undistorted_src_img.png "Undistorted image"
[image9]: ./output_images/warped_img.png "Perspective transform"

[image11]: ./test_images/test3.jpg "Source frame"
[video1]: ./project_video.mp4 "Video"

## Advanced Lane Finding

The goal of this project is to develop a pipeline to process a video stream from a forward-facing camera mounted on the front of a car, and output an annotated video which identifies:

* The positions of the lane lines
* The location of the vehicle relative to the center of the lane
* The radius of curvature of the road
* The pipeline created for this project processes images in the following steps:

* Step 1: Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Step 2: Apply a distortion correction to raw images.
* Step 3: Use color transforms, gradients, etc., to create a thresholded binary image.
* Step 4: Apply a perspective transform to rectify binary image ("birds-eye view").
* Step 5: Detect lane pixels and fit to find the lane boundary.
* Step 6: Determine the curvature of the lane and vehicle position with respect to center.
* Step 7: Warp the detected lane boundaries back onto the original image.
* Step 8: Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

### Pipeline description
Step 1: Camera Calibration
#### 1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. A number of images of a chessboard, taken from different angles with the same camera, comprise the input (in ./camera_cal/). Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

The below image depicts the corners drawn onto a sample chessboard image using the OpenCV function drawChessboardCorners:

![alt text][image2]

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

![alt text][image7]

Step 2: Distortion Correction

The camera calibration matrix and distortion coefficients obtained from the above step were used with the OpenCV function undistort() to remove distortion from highway driving images.

![alt text][image11]
![alt text][image8]

Step 3: Perspective Transform

In this step, the undistorted image is transformed to a "birds eye view" of the road which focuses only on the lane lines and displays them in such a way that they appear to be relatively parallel to eachother (as opposed to the converging lines you would normally see).
To achieve the perspective transformation I first applied the OpenCV functions getPerspectiveTransform and warpPerspective which take a matrix of four source points on the undistorted image and remaps them to four destination points on the warped image. The source and destination points were selected manually by visualizing the locations of the lane lines on a series of test images.

The source and destination warp points are shown below:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 585, 460      | 320, 0        | 
| 203, 720      | 320, 720      |
| 1127, 720     | 960, 720      |
| 695, 460      | 960, 0        |

![alt text][image6]

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.

![alt text][image9]

Step 4: Binary thresholding

The binarize() function takes in the undistorted warped image (RGB) and applies and HLS color space and sobel thresholding to create a binary thresholded image which highlight only the lane lines and ignore everything else. The L and S channels in the HLS color space was thresholded to min: 120, max: 255 & min: 40, max: 255 repectively. This was combined applying min: 20, max: 255 threshold to sobel filtered image in x direction. The resultant binary image did a good job of highlighting almost all of the white and yellow lane lines. 

![alt text][image2]

Step 5: Polyfit lane lines

The first of these computes a histogram of the bottom half of the image and finds the bottom-most x position (or "base") of the left and right lane lines. Originally these locations were identified from the local maxima of the left and right halves of the histogram. The image below depicts the histogram generated by sliding_window_polyfit; the resulting base points for the left and right lanes - the two peaks nearest the center - are clearly visible

![alt text][image4]

The function then identifies ten windows from which to identify lane pixels, each one centered on the midpoint of the pixels from the window below. This effectively "follows" the lane lines up to the top of the binary image, and speeds processing by only searching for activated pixels over a small portion of the image. Pixels belonging to each lane line are identified and the Numpy polyfit() method fits a second order polynomial to each set of pixels. The image below demonstrates how this process works:

![alt text][image5]

The polyfit_using_prev_fit"""""" function performs basically the same task without using the blind window search. Instead it leverages a previous fit from a previous video frame and only searching for lane pixels within a certain margin of that fit. The blind window search runs again if the pipeline could not find lanes in the previous frame.

Step 6: Calculate radius of curvature and vehicle position from center

I used the following code to calculate the radius of curvature for each lane line in meters and the final radius of curvature was taken by average the left and right curve radiuses.

![alt text][image2]

The position of the vehicle with respect to the center of the lane is calculated with the following lines of code:

![alt text][image2]

The car position is the difference between these intercept points and the image midpoint (assuming that the camera is mounted at the center of the vehicle).
 
Step 7: Unwarp the image back to its original perspective and  Display the lane curvature and vehicle position on the final image

The final step in processing the images was to plot the polynomials on to the warped image, fill the space between the polynomials to highlight the lane that the car is in, use another perspective trasformation to unwarp the image from birds eye back to its original perspective, and print the distance from center and radius of curvature on to the final annotated image.

![alt text][image1]

### Pipeline (video)

The video pipeline first checks whether or not the lane was detected in the previous frame. If it was, then it only checks for lane pixels in close proximity to the polynomial calculated in the previous frame. This way, the pipeline does not need to scan the entire image, and the pixels detected have a high confidence of belonging to the lane line because they are based on the location of the lane in the previous frame.

If at any time, the pipeline fails to detect lane pixels based on the the previous frame, it will go back in to blind search mode and scan the entire binary image for nonzero pixels to represent the lanes.

Here's a [link to my video result](./project_video.mp4)


---
### Possible Limitations
#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?



The video pipeline developed in this project did a fairly robust job of detecting the lane lines in the test video provided for the project, which shows a road in basically ideal conditions, with fairly distinct lane lines, and on a clear day. It also did a decent job with the challenge video, although it did lose the lane lines momentarily when there was heavy shadow over the road from an overpass.

What I have learned from this project is that it is relatively easy to finetune a software pipeline to work well for consistent road and weather conditions, but what is challenging is finding a single combination which produces the same quality result in any condition.

---
Project video - diagnostic version
[link to my video result](./project_video_output_diag.mp4)

Challenge video - diagnostic version
[link to my video result](./challenge_video_output_diag.mp4)

