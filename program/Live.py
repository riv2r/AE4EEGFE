import numpy as np
import cv2

class Live(object):

    '''
    windows resolution: 1280x720 
    '''
    def __init__(self):

        self.win_sz=720
        self.block_sz=80 # 16 times

        self.cap=cv2.VideoCapture(0)
        cv2.namedWindow("capture",0)
        cv2.setWindowProperty("capture",cv2.WND_PROP_TOPMOST,1)

        self._move_window()
    
    def _move_window(self):

        # self.cap.set(3,self.win_sz)
        # self.cap.set(4,self.win_sz/16*9)
        texture_sz=self.win_sz
        cap_w=texture_sz-2*self.block_sz
        cap_h=cap_w//16*9
        cv2.resizeWindow("capture",cap_w,cap_h)
        cv2.moveWindow("capture",640-cap_w//2-8,360-cap_h//2)
    
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