import numpy as np
import cv2

class Live(object):

    def __init__(self):

        self.w=1920
        self.h=1080
        self.size=100

        self.cap=cv2.VideoCapture(0)
        cv2.namedWindow("capture")

        self._move_window()
    
    def _move_window(self):

        texture_sz=1024
        cap_w=round(texture_sz-2*self.size)
        cap_h=round(cap_w/self.w*self.h)
        self.cap.set(3,cap_w)
        self.cap.set(4,cap_h)
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