import threading 
import pygame 
from math import sin, pi

NUM_OF_THREAD = 6
b = threading.Barrier(NUM_OF_THREAD)

def blinking_block(points, frequency, win):
    COUNT = 1
    CLOCK = pygame.time.Clock()
    ''' FrameRate '''
    FrameRate = 60
    
    b.wait()    #Synchronize the start of each thread
    while True: #execution block
        CLOCK.tick(FrameRate)
        tmp = sin(2*pi*frequency*(COUNT/FrameRate))
        color = 255*(tmp>0)
        block = pygame.draw.polygon(win, (color, color, color), points, 0)
        pygame.display.update(block)  #can't update in main thread which will introduce delay in different block       
        COUNT += 1
        if COUNT == FrameRate:
            COUNT = 0
        # print(CLOCK.get_time()) #check the time between each frame (144HZ=7ms; 60HZ=16.67ms)


def main():
    pygame.init()
    pygame.TIMER_RESOLUTION = 1 #set time resolutions
    win = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    
    #background canvas
    bg = pygame.Surface(win.get_size())
    bg = bg.convert()
    bg.fill((0,0,0))           #  black background
    #display
    win.blit(bg, (0,0))
    pygame.display.update()
    pygame.display.set_caption("Blinking")
    
    ''' frequency '''
    frequency = [8,9,10,11,12,13] #frequency bank
    ''' POINTS '''
    POINTS = [[(1205,0),(1130,150),(1280,150)],         #takeoff
              [(1205,720),(1130,570),(1280,570)],       #land
              [(565,0),(490,150),(640,150)],            #forward
              [(565,720),(490,570),(640,570)],          #backward
              [(0,360),(150,435),(150,285)],            #left
              [(1130,360),(980,435),(980,285)]]         #right
    
    threads = []
    for i in range(6):
        threads.append(threading.Thread(target=blinking_block, args=(POINTS[i],frequency[i],win)))
        threads[i].daemon=True
        threads[i].start()
     
    RUN = True    
    while RUN:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                RUN = False
        pygame.time.delay(100)

    pygame.quit()
    quit()


if __name__ == '__main__':
    main()
