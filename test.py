import cv2


img = cv2.imread("temp.jpg", cv2.IMREAD_UNCHANGED)
img = cv2.putText(img,"1",(50,50),cv2.LINE_4,2,(0,0,0,0.5),8)
img = cv2.putText(img,"1",(50,50),cv2.LINE_4,2,(255,255,255,0.5),2)
cv2.namedWindow("a")
cv2.imshow("a",img)
cv2.waitKey(0)