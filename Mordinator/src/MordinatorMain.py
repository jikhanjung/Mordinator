'''
Created on 2012. 9. 26.

@author: jikhanjung
'''

import wx
import sys
from main_frame import MordinatorFrame
import os.path

class MordinatorGUI(wx.App):
    def OnInit(self):
        self.dbpath = ""

        ''' initiate frame '''
        self.frame = MordinatorFrame(None, -1, 'Mordinator' )
        self.frame.Show(True) 
        self.SetTopWindow(self.frame)
        self.basepath = os.path.expanduser("~")
        
        sys.stdout = open(os.path.join(self.basepath,"my_stdout.log"), "w", 0)
        sys.stderr = open(os.path.join(self.basepath,"my_stderr.log"), "w")
        return True 

if __name__ == '__main__':
    app = MordinatorGUI(0) 
    #print sys.argv[0]
    app.MainLoop()
 