import numpy as np
from psychopy import core,visual,event
import time


class SSVEPStimuli(object):

    '''
    linux resolution: 1920x1080
    windows resolution: 1280x720 
    '''
    def __init__(self,win=visual.Window(size=(1280,720),fullscr=True,units='pix',color='black')):

        self.win=win

        self.w=win.size[0]
        self.h=win.size[1]
        self.size=100

        # self.white=[1,1,1]
        # self.black=[-1,-1,-1]

        self._get_texture()
        self._get_freq()
    
    def _get_texture(self):

        # power of 2
        texture_sz=1024#min(self.w,self.h)
        texture_mat=np.zeros((5,texture_sz,texture_sz))

        '''
        -1  -1   1  -1  -1  TOP
         1  -1  -1  -1   1  LEFT/RIGHT
        -1  -1   1  -1  -1  BOT
        '''

        for i in range(texture_sz):
            for j in range(texture_sz):
                # TOP
                if j>texture_sz/2-self.size/2 and j<=texture_sz/2+self.size/2 and i>texture_sz-self.size:
                    texture_mat[1][i][j]=1
                # LEFT
                elif i>texture_sz/2-self.size/2 and i<=texture_sz/2+self.size/2 and j<=self.size:
                    texture_mat[2][i][j]=1
                # RIGHT
                elif i>texture_sz/2-self.size/2 and i<=texture_sz/2+self.size/2 and j>texture_sz-self.size:
                    texture_mat[3][i][j]=1
                # BOT
                elif j>texture_sz/2-self.size/2 and j<=texture_sz/2+self.size/2 and i<=self.size:
                    texture_mat[4][i][j]=1
        
        texture_mat_merged=np.zeros((16,texture_sz,texture_sz))
        for flag1 in range(2):
            for flag2 in range(2):
                for flag3 in range(2):
                    for flag4 in range(2):
                        idx=flag4*8+flag3*4+flag2*2+flag1*1
                        texture_mat_merged[idx]=np.logical_or(np.logical_or(np.logical_or(np.logical_or(texture_mat[0],texture_mat[1]*flag1),texture_mat[2]*flag2),texture_mat[3]*flag3),texture_mat[4]*flag4).astype(int)
                        texture_mat_merged[idx][texture_mat_merged[idx]==0]=-1
        
        self.texture=texture_mat_merged
        
    def _get_freq(self):

        # freq=60/fn
        f1=[1,1,1,1,0,0,0,0] # 7.50Hz
        f2=[1,1,1,1,0,0,0]   # 8.57Hz
        f3=[1,1,1,0,0,0]     # 10.0Hz
        f4=[1,1,1,0,0]       # 12.0Hz
        
        fn_list=[len(f1),len(f2),len(f3),len(f4)]

        lcm_freq=1
        for fn in fn_list:
            lcm_freq=np.lcm(fn,lcm_freq)
        self.lcm_freq=lcm_freq

        f1=f1*(lcm_freq/len(f1)).astype(int)
        f2=f2*(lcm_freq/len(f2)).astype(int)
        f3=f3*(lcm_freq/len(f3)).astype(int)
        f4=f4*(lcm_freq/len(f4)).astype(int)

        self.freq=np.vstack((np.vstack((np.vstack((f1,f2)),f3)),f4))

    def stop(self):

        self.win.close()
        core.quit()

    def start(self):

        patterns=[]
        for idx in range(16):
            patterns.append(visual.GratingStim(win=self.win,tex=self.texture[idx],pos=(0,0),units='pix'))
        
        idx=0
        self.clock=core.Clock()
        while True:#self.clock.getTime() < 5.0:
            texture_val=self.freq[:,idx].dot(np.array([1,2,4,8]))
            patterns[texture_val].draw()
            self.win.flip()
            idx+=1
            if idx>=self.lcm_freq:
                idx=0
            if event.getKeys('q'):
                break

        self.clock.reset()


def startup():

    #t1=time.time()
    ssvep_stimuli=SSVEPStimuli()
    #t2=time.time()
    #print(t2-t1)
    ssvep_stimuli.start()
    ssvep_stimuli.stop()
    
    
if __name__=="__main__":

    startup()