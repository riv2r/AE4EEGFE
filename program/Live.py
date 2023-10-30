import cv2

class Live(object):

    '''
    windows resolution: 1280x720 
    '''
    def __init__(self):

        self.cap=cv2.VideoCapture(0)
        cv2.namedWindow("capture",0)
        cv2.setWindowProperty("capture",cv2.WND_PROP_TOPMOST,1)

        self._move_window()
    
    def _move_window(self):

        cv2.resizeWindow("capture",500,375)
        cv2.moveWindow("capture",315,155)
        
    def start(self):

        while True:
            ret,frame=self.cap.read()
            cv2.imshow("capture",frame)
            if cv2.waitKey(1) & 0xFF==ord('q'):
                break

    def stop(self):

        self.cap.release()
        cv2.destroyAllWindows()


def main():
    
    live=Live()
    live.start()
    live.stop()


if __name__=="__main__":
    main()