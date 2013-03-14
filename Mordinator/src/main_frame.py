'''
Created on 2012. 9. 26.

@author: jikhanjung
'''

import wx
import os
import re
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from analysis_frame import AnalysisFrame
from fileopen_dlg import FileOpenDialog
from analysiscfg_dlg import AnalysisConfigDialog
NEWLINE = "\n"
windowSize = wx.Size(800,600)
treePaneWidth = 200 
minTreePaneWidth = 100
itemListHeight = 300
minItemPaneHeight = 200

ID_OBJECT_CONTENT = 77

ID_OPEN_FILE = 1001
ID_NEW_DATASET = 1002
ID_SAVEAS = 1003
ID_IMPORT = 1004
ID_EXPORT = 1005
ID_ANALYSIS = 1006
ID_NEW_OBJECT = 1007
ID_NEW_DATASET = 1008
ID_PREFERENCES = 1009
ID_NEW_DB = 1010
ID_ABOUT = 1011
ID_PERMUTATION = 1012


class OrdData():
    def __init__(self, name = "", category_data = {}, data = []):
        self.name = name
        self.data = data
        self.category_data = {}
        self.pca_result = []
        self.cva_result = []
        i=0
        self.category_data = category_data

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)



class MordinatorFrame( wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, windowSize )
        self.statusbar = self.CreateStatusBar()
        self.app = wx.GetApp()
        self.dataset = {}
        self.data = {}
        self.data_config = {}
        self.analysis_config = {}
        self.images = {}

        ''' Toolbar ''' 
        toolbar = self.CreateToolBar()
        tool_image_opendb = wx.Bitmap( "icon/newdataset.png", wx.BITMAP_TYPE_PNG )
        tool_image_analysis = wx.Bitmap( "icon/analyze.png", wx.BITMAP_TYPE_PNG )
        tool_image_permutation= wx.Bitmap( "icon/analyze.png", wx.BITMAP_TYPE_PNG )

        toolbar.AddSimpleTool( ID_OPEN_FILE, tool_image_opendb, "Open File" )
        toolbar.AddSimpleTool( ID_ANALYSIS, tool_image_analysis, "Analyze" )
        toolbar.AddSimpleTool( ID_PERMUTATION, tool_image_permutation, "Permutation" )

        toolbar.SetToolBitmapSize( wx.Size(32,32))
        toolbar.Realize()

        self.Bind( wx.EVT_TOOL, self.OnOpenFile, id=ID_OPEN_FILE)
        self.Bind( wx.EVT_TOOL, self.OnAnalysis, id=ID_ANALYSIS )
        self.Bind( wx.EVT_TOOL, self.OnPermutation, id=ID_PERMUTATION )
        
        ''' Splitter '''
        self.vsplit= wx.SplitterWindow( self, -1, style= wx.SP_BORDER )
        self.hsplit = wx.SplitterWindow( self.vsplit, -1, style= wx.SP_BORDER )

        ''' Dataset Tree '''
        '''self.w1 = wx.Panel( self.sp1)
        self.w2 = wx.Panel( self.sp1 )
        self.w2.Hide()
        self.w1.SetBackgroundColour("pink")
        self.w2.SetBackgroundColour("sky blue")
        '''
        #self.objectList = wx.ListBox( self.objectSplitter, -1, choices=(["a","b"]), style=wx.LB_EXTENDED )
        self.listctrl = CheckListCtrl( self.vsplit )
        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.listctrl)        
        self.p2 = wx.Panel(self.hsplit)
        self.p3 = wx.Panel(self.hsplit)
        #self.p1.SetBackgroundColour("pink")
        self.p2.SetBackgroundColour("white")
        self.p3.SetBackgroundColour("white")

        self.Image = wx.StaticBitmap(self.p3, bitmap=wx.EmptyBitmap(640,480))
        # Using a Sizer to handle the layout: I never  use absolute positioning
        box = wx.BoxSizer(wx.VERTICAL)
        #box.Add(b, 0, wx.CENTER | wx.ALL,10)

        # adding stretchable space before and after centers the image.
        box.Add((1,1),1)
        box.Add(self.Image, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
        box.Add((1,1),1)
        self.p3.SetSizerAndFit(box)                
        #self.datasetTree= wx.ListBox( self.treeSplitter, -1, choices=(["a","b"]), style=wx.LB_EXTENDED )
        #self.app.objectContent = self.objectContent = MdObjectContent( self.objectSplitter, id=ID_OBJECT_CONTENT )
        #self.app.objectList    = self.objectList = MdObjectList( self.objectSplitter, -1 )
        #self.app.datasetTree   = self.datasetTree = MdDatasetTree(     self.treeSplitter, -1 )
    
        ''' Object content '''
        #self.objectContent.Bind( wx.EVT_LEFT_DCLICK, self.OnDoubleClick, id=ID_OBJECT_CONTENT )
    
        ''' Wrap up '''
        self.hsplit.SplitHorizontally( self.p2, self.p3, itemListHeight )
        self.vsplit.SplitVertically( self.listctrl, self.hsplit, treePaneWidth )
        
        iconFile = "icon/Mordinator.ico"        
        icon1 = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)        
        self.SetIcon(icon1)
        
    def OnItemSelected(self, event):
        item = event.GetItem()
        name = item.GetText()

        if name not in self.images.keys():
            image_dir = self.data_config['image_dir']
            image_path = image_dir + "/" + name + ".png"
            #print image_path
            if os.path.isfile( image_path ):
                img = wx.Image( image_path )
                self.images[name] = img
            else:
                self.images[name] = None
        #print self.images[name]
        if self.images[name]:
            self.Image.SetBitmap( wx.BitmapFromImage( self.images[name]) )
            
        #print self.data[name].data
        #print self.config['image_dir']
        self.Refresh()
        
    def SelectItem(self, name):
        count = self.listctrl.GetItemCount()
        for idx in range( count ):
            self.listctrl.Select( idx, on = 0 )
        idx = self.listctrl.FindItem( 0, name )
        self.listctrl.Select( idx )
        
    def OnOpenFile( self, event ):
        wildcard = "All files (*.*)|*.*"     
        dialog_style = wx.OPEN 
    
        selectfile_dialog = wx.FileDialog(self, "Select a file to open", "", "", wildcard, dialog_style )
        if selectfile_dialog.ShowModal() == wx.ID_OK:
          self.openpath = selectfile_dialog.GetPath()
          #( unc, pathname ) = splitunc( self.importpath )
          fullpath = self.openpath
    #      print pathname
          ( pathname, fname ) = os.path.split( fullpath )
          ( fname, ext ) = os.path.splitext( fname )
        else:
          return
        
        
        open_success = self.OpenFile( fullpath )
        if not open_success:
          wx.MessageBox( "Cannot open selected file!" )
          return
        return

    def OpenFile(self, filepath ):
        f = open( filepath, 'r' )
        filelines = f.read()
        f.close()
        self.dataset['filename'] = filepath
        self.dataset['data'] = []
        
        lines = [ l.strip() for l in filelines.split( NEWLINE ) ]
        
        self.data_config = data_config = {}
        mode = 'HEADER'
        data_index_list = []
        category_index_list = {}
        specimenid_index = -1
        for line in lines:
            line = line.strip()
            if mode == 'HEADER':
                mode = 'DATA'
                columns = re.split( '\t+', line )
                #print columns
                fileopen_dlg = FileOpenDialog( self )
                #print columns
                fileopen_dlg.SetColumns( columns )
                fileopen_dlg.SetFilepath( filepath )
                ret = fileopen_dlg.ShowModal()
                if ret == wx.ID_OK:
                    self.data_config = fileopen_dlg.config
                    #print self.data_config
                    data_index = []
                    for col in self.data_config['data_list']:
                        data_index_list.append( columns.index( col ) )
                    data_index_list.sort()
                    for col in self.data_config['category_list']:
                        category_index_list[col] = columns.index( col )
                    
                    specimenid_index = columns.index( self.data_config['specimenid'] )
                    #print "specimenid index :", self.config['specimenid'],  specimenid_index
                    image_dir = self.data_config['image_dir']
                    self.dataset['image_dir'] = image_dir
                    self.dataset['category_list'] = self.data_config['category_list']
                    #print "okay..."
                else:
                    print "meh.."
                    return

            elif mode == 'DATA':
                data_line = re.split( '\t+', line )
                if len( data_line ) < 2 : continue
                data_config['data_len'] = len( data_index_list )
                actual_data = [ data_line[x] for x in data_index_list ] 
                #category_data = [ data_line[x] for x in category_index_list ]
                category_data = {}
                for category_key in self.data_config['category_list']:
                    idx = category_index_list[category_key]
                    category_data[category_key] = data_line[idx]
                dataname = data_line[specimenid_index]
                #print actual_data
                #print category_data
                #print "name:", specimenid_index, dataname
                orddata = OrdData( data_line[specimenid_index], category_data = category_data, data = actual_data )
                self.dataset['data'].append( orddata )
                self.data[orddata.name] = orddata

       #print config
        #print "data from", data_from
        #
        self.listctrl.ClearAll()
        i = 0
        self.listctrl.InsertColumn( i, 'name' )
        for category in self.data_config['category_list']:
            i+=1
            self.listctrl.InsertColumn( i, category )
        i = 0
        for orddata in self.dataset['data']:
            index = self.listctrl.InsertStringItem( i, orddata.name )
            j = 0
            checked = True
            self.listctrl.SetStringItem( index, j, orddata.name )
            for category in self.data_config['category_list']:
                j += 1
                self.listctrl.SetStringItem( index, j, orddata.category_data[category] )
                #if orddata.category_data[category] == "IR": checked = False
            self.listctrl.CheckItem(index,checked)
            i+= 1
            
        return True

    def OnAnalysis(self, event ):
        #print "analysis"
        dlg1 = AnalysisConfigDialog( self )
        dlg1.SetDataset( self.dataset )
        rv = dlg1.ShowModal()
        if rv == wx.ID_OK:
            self.analysis_config = dlg1.analysis_config
            #print self.analysis_config
            dlg1.Destroy()
        else:
            dlg1.Destroy()
            return
        
        self.analysis_frame = AnalysisFrame(self)
        analysis_data = []
        
        '''
        for i in range( len( self.data ) ):
            if self.listctrl.IsChecked( i ):
                name = self.listctrl.GetItemText( i )
                analysis_data.append( self.data[name] ) 
        '''
        self.analysis_frame.PrepareData( self.dataset['data'], self.data_config, self.analysis_config )
        self.analysis_frame.Analyze()
        self.analysis_frame.Show()

    def OnPermutation(self, event ):
        #print "permutation"
        dlg1 = AnalysisConfigDialog( self )
        dlg1.SetDataset( self.dataset )
        rv = dlg1.ShowModal()
        if rv == wx.ID_OK:
            self.analysis_config = dlg1.analysis_config
            #print self.analysis_config
            dlg1.Destroy()
        else:
            dlg1.Destroy()
            return
        #print "hello"
        filter_by = self.analysis_config['filter_by']
        group_by = self.analysis_config['group_by']

        data = []
        category_data = []
        for obj in self.dataset['data']:
            if obj.category_data[filter_by] in self.analysis_config['include']:
                data.append( [ float( x ) for x in obj.data ] )
                category_data.append( obj.category_data[group_by] )

        category_set = list( set( category_data ) )
        #print category_set
        num_category = len( list( category_set ) )
        #print num_category
        for i in range( num_category - 1 ):
            for j in range( i+1, num_category ):
                #print i, j, category_set[i], category_set[j]
                self.PermutationTest( data, category_data, category_set[i], category_set[j] )

    
    def GetAverage(self, data):
        len_vector = len( data[0] )
        sum1 = [ 0.0 for x in range( len_vector ) ]
        avg1 = [ 0.0 for x in range( len_vector ) ]
        for i in range( len( data ) ):
            for j in range( len_vector ):
                sum1[j] += data[i][j]
        for j in range( len_vector ):
            avg1[j] = sum1[j] / float( len( data ) )
        return avg1
    
    def PermutationTest(self, data, cat_data, cat1, cat2 ):
        print "permute", cat1, cat2
        num_data = len( data )
        len_vector = len( data[0] )
        permutation_count = 10000
        '''calculate multivar average'''
        data1 = []
        data2 = []
        mixed_data = []
        for i in range( num_data ):
            if cat_data[i] == cat1:
                data1.append( data[i] )
                mixed_data.append( data[i] )
            elif cat_data[i] == cat2:
                data2.append( data[i] )
                mixed_data.append( data[i] )
        num_cat1 = len( data1 )
        num_cat2 = len( data2 )
        avg1 = self.GetAverage( data1 )
        avg2 = self.GetAverage( data2 )
        import math
        import random
        '''get euclidean distance'''
        base_euc_dist = 0.0
        for j in range( len_vector ):
            base_euc_dist += ( avg1[j] - avg2[j] ) ** 2
        base_euc_dist = math.sqrt( base_euc_dist )
        
        
        '''loop 1000 times'''
        dist_list = []
        for lp in range( permutation_count ):
            '''    permute and group'''
            random.shuffle( mixed_data )
            group1 = mixed_data[:num_cat1]
            group2 = mixed_data[num_cat1:]
            '''    get euclidean distance again'''
            avg1 = self.GetAverage( group1 )
            avg2 = self.GetAverage( group2 )
            euc_dist = 0.0
            for j in range( len_vector ):
                euc_dist += ( avg1[j] - avg2[j] ) ** 2
            euc_dist = math.sqrt( euc_dist )
            dist_list.append( euc_dist )
        dist_list.sort()
        larger_dist_count = 0
        for dist in dist_list:
            if dist > base_euc_dist:
                larger_dist_count += 1
        percentage_larger_dist = float( larger_dist_count ) / float( len( dist_list ) )    
        print "total", len( dist_list ), "permutation"
        print int( percentage_larger_dist * 10000 ) / 100.0, "% of total cases yielded larger distance than the original one."
        #print dist_list
        #print base_euc_dist
    def OnResize(self,event):
        #self.objectList.OnResize()
        #event.Skip()
        pass