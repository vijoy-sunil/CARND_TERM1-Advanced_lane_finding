#import packages
import numpy as np
import cv2

def find_curvature(ploty, leftx, rightx, lefty, righty):
    ym_per_pix = 30/720
    xm_per_pix = 3.7/600
    y_eval = np.max(ploty)
    
# Fit new polynomials to x,y in world space
    left_fit_cr = np.polyfit(lefty*ym_per_pix, leftx*xm_per_pix, 2)
    right_fit_cr = np.polyfit(righty*ym_per_pix, rightx*xm_per_pix, 2)

# Calculate the new radii of curvature
    left_curverad = ((1 + (2*left_fit_cr[0]*y_eval*ym_per_pix + left_fit_cr[1])**2)**1.5) / np.absolute(2*left_fit_cr[0])
    right_curverad = ((1 + (2*right_fit_cr[0]*y_eval*ym_per_pix + right_fit_cr[1])**2)**1.5) / np.absolute(2*right_fit_cr[0])

    rad = (left_curverad + right_curverad)/2
# return radius of curvature is in meters
    return left_curverad, right_curverad, rad

#function to calculate distance from center
def dist_center(img, left_fit, right_fit, binary):
    xm_per_pix = 3.7/780
# Distance from center is image x midpoint - mean of l_fit and r_fit intercepts 
    if left_fit is not None and right_fit is not None:
        car_pos = binary.shape[1]/2
        h = binary.shape[0]
        left_fit_x_int = left_fit[0]*h**2 + left_fit[1]*h + left_fit[2]
        right_fit_x_int = right_fit[0]*h**2 + right_fit[1]*h + right_fit[2]
        lane_center_position = (left_fit_x_int + right_fit_x_int) /2
        center_dist = (car_pos - lane_center_position) * xm_per_pix
    return center_dist

#function to annotate measurements
def annotate(img, rad, d_center):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = 'Curve radius: ' + '{:04.2f}'.format(rad) + 'm'
    cv2.putText(img, text, (40,70), font, 1.5, (200,255,155), 2, cv2.LINE_AA)
    
    direction = ''
    if d_center > 0:
        direction = 'right'
    elif d_center < 0:
        direction = 'left'
    abs_d_center = abs(d_center)
    text = 'Distance from center: ' + '{:04.3f}'.format(abs_d_center) + 'm ' + ', ' + direction
    cv2.putText(img, text, (40,120), font, 1.5, (200,255,155), 2, cv2.LINE_AA)

    return img