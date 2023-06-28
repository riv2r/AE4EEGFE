import numpy as np
import cv2

class Live(object):

    '''
    linux resolution: 1920x1080
    windows resolution: 1280x720 
    '''
    def __init__(self):

        self.w=1280 #1920
        self.h=720  #1080
        self.size=100

        self.cap=cv2.VideoCapture(0)
        cv2.namedWindow("capture",0)
        cv2.setWindowProperty("capture",cv2.WND_PROP_TOPMOST,1)

        self._move_window()
    
    def _move_window(self):

        self.cap.set(3,self.w)
        self.cap.set(4,self.h)
        texture_sz=720  #1080
        cap_w=round(texture_sz-2*self.size)
        cap_h=round(cap_w/self.w*self.h)
        cv2.resizeWindow("capture",cap_w,cap_h)
        cv2.moveWindow("capture",round(self.w/2-cap_w/2)-10,round(self.h/2-cap_h/2))
    
    def start(self):

        while True:
            ret,frame=self.cap.read()
            cv2.imshow("capture",frame)
            if cv2.waitKey(1) & 0xFF==ord('q'):
                break

    def stop(self):

        self.cap.release()
        cv2.destroyAllWindows()


def startup():
    
    live=Live()
    live.start()
    live.stop()


if __name__=="__main__":

    startup()