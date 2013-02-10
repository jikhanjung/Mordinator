from wx.lib.plot import *
import wx
from mdstatistics import MdPrincipalComponent, MdCanonicalVariate
import numpy
import os

ID_TEST_BUTTON = 1001


from PIL import Image, ImageEnhance, ImageFont, ImageDraw
class DsImage( wx.Image ):
    def __init__(self, filename,type=wx.BITMAP_TYPE_ANY, index=-1 ):
        wx.Image.__init__( self, filename, type, index )
        

def piltoimage(pil,alpha=True):
    """Convert PIL Image to wx.Image."""
    if alpha:
        #print "alpha 1", clock()
        image = apply( wx.EmptyImage, pil.size )
        #print "alpha 2", clock()
        image.SetData( pil.convert( "RGB").tostring() )
        #print "alpha 3", clock()
        image.SetAlphaData(pil.convert("RGBA").tostring()[3::4])
        #print "alpha 4", clock()
    else:
        #print "no alpha 1", clock()
        image = wx.EmptyImage(pil.size[0], pil.size[1])
        #print "no alpha 2", clock()
        new_image = pil.convert('RGB')
        #print "no alpha 3", clock()
        data = new_image.tostring()
        #print "no alpha 4", clock()
        image.SetData(data)
        #print "no alpha 5", clock()
    #print "pil2img", image.GetWidth(), image.GetHeight()
    return image

def imagetopil(image):
    """Convert wx.Image to PIL Image."""
    #print "img2pil", image.GetWidth(), image.GetHeight()
    pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
    pil.fromstring(image.GetData())
    return pil


#IMAGE_PATH = 'D:/My Documents/My Dropbox/2012 Fall/Progress/Coral export data/images/Agaricid_HJ305.png'
class ShapedFrame(wx.MiniFrame):
    def __init__(self, parent, img, name ):
        wx.MiniFrame.__init__(self, parent, -1, "Shaped Window",
                style = wx.FRAME_SHAPED | wx.SIMPLE_BORDER | wx.FRAME_FLOAT_ON_PARENT )
        self.parent = parent
        self.hasShape = False
        self.delta = wx.Point(0,0)
        self.name = name

        # Load the image
        image = img  
        self.bmp = wx.BitmapFromImage(image)

        self.SetClientSize((self.bmp.GetWidth(), self.bmp.GetHeight()))
        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.bmp, 0,0, True)
        self.SetWindowShape()
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_RIGHT_UP, self.OnHide )
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_WINDOW_CREATE, self.SetWindowShape)

    def SetWindowShape(self, evt=None):
        #print "set Window Shape"
        r = wx.RegionFromBitmap(self.bmp)
        self.hasShape = self.SetShape(r)
    def SetImage(self, img, name ):
        self.bmp = wx.BitmapFromImage( img )
        self.name = name
        self.SetWindowShape()
        self.Refresh()

    def OnDoubleClick(self, evt):
        #print "double click"
        if self.hasShape:
            print "double click hasShape true"
            self.SetShape(wx.Region())
            self.hasShape = False
            print "double click hasShape now set false"
        else:
            print "double click hasShape False"
            self.SetWindowShape()

    def OnPaint(self, evt):
        #print "onpaint"
        dc = wx.PaintDC(self)
        if not self.hasShape:
        #print "has SHape false"
            dc.DrawBitmap(self.bmp, 0,0, True)
            #dc.DrawText( self.name, 5, 5 )
            #self.Refresh()
        else:
            dc.DrawBitmap(self.bmp, 0,0, True)
    def OnHide(self, evt):
        self.Hide()

    def OnLeftDown(self, evt):
        self.CaptureMouse()
        pos = self.ClientToScreen(evt.GetPosition())
        origin = self.GetPosition()
        self.delta = wx.Point(pos.x - origin.x, pos.y - origin.y)

    def OnMouseMove(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            pos = self.ClientToScreen(evt.GetPosition())
            newPos = (pos.x - self.delta.x, pos.y - self.delta.y)
            self.Move(newPos)

    def OnLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
        #print "before setfocus"
        self.parent.SetFocus()
        #print "after setfocus"
        
ID_CHK_SHOW_IMAGE = 1002
ID_XAXIS_COMBO = 1003
ID_YAXIS_COMBO = 1004

class AnalysisFrame( wx.Frame ):
    def __init__(self, parent ):
        wx.Frame.__init__( self, parent, -1, "PCA", wx.DefaultPosition, wx.Size(1280,1024))
        panel = wx.Panel( self )
        self.panel = panel

        self.xaxis_pc_idx = 0
        self.yaxis_pc_idx = 0
        self.analysis_done = False
        self.selected_category_name = ""

        self.image_width = 320
        self.image_height = 240
        self.data = {}
        self.config = {}

        self.chkShowImage= wx.CheckBox( panel, ID_CHK_SHOW_IMAGE, "Show Image" )
        self.Bind( wx.EVT_CHECKBOX, self.ToggleShowImage, id=ID_CHK_SHOW_IMAGE )
        self.xAxisLabel = wx.StaticText( panel, -1, 'X Axis', style=wx.ALIGN_CENTER )
        self.xAxisCombo = wx.ComboBox( panel, ID_XAXIS_COMBO, "", (15,30),wx.DefaultSize, [], wx.CB_DROPDOWN )
        self.yAxisLabel = wx.StaticText( panel, -1, 'Y Axis', style=wx.ALIGN_CENTER )
        self.yAxisCombo = wx.ComboBox( panel, ID_YAXIS_COMBO, "", (15,30),wx.DefaultSize, [], wx.CB_DROPDOWN )
        self.Bind( wx.EVT_COMBOBOX, self.OnXAxis, id=ID_XAXIS_COMBO )
        self.Bind( wx.EVT_COMBOBOX, self.OnYAxis, id=ID_YAXIS_COMBO )

        self.BivariatePlotter = PlotCanvas(panel)
        self.BivariatePlotter.SetPointLabelFunc(self.DrawPointLabel)
        self.BivariatePlotter.SetMinSize((1024,768))
        self.BivariatePlotter.SetEnablePointLabel(True)
        self.BivariatePlotter.canvas.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.BivariatePlotter.canvas.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind( wx.EVT_SET_FOCUS, self.OnFocus )
        self.ImageViewList = []

        self.mainSizer = wx.BoxSizer( wx.HORIZONTAL )
        self.optionSizer = wx.BoxSizer( wx.VERTICAL)
        self.optionSizer.Add( self.chkShowImage, 0, flag=wx.EXPAND )
        self.optionSizer.Add( self.xAxisLabel, 0, flag=wx.EXPAND )
        self.optionSizer.Add( self.xAxisCombo, 0, flag=wx.EXPAND )
        self.optionSizer.Add( self.yAxisLabel, 0, flag=wx.EXPAND )
        self.optionSizer.Add( self.yAxisCombo, 0, flag=wx.EXPAND )

        self.mainSizer.Add( self.BivariatePlotter, 1, flag=wx.EXPAND )
        self.mainSizer.Add( self.optionSizer, 0, flag=wx.EXPAND )
        panel.SetSizer(self.mainSizer)
        panel.Fit()

        self.images = {}
        self.show_image = False
        #self.PerformPCA()

    def OnXAxis(self,event):
        x = self.xAxisCombo.GetValue()
        #print x
        xaxis = x[2:]
        self.xaxis_idx = int( xaxis ) - 1 
        self.VisualizeResult()
      
    def OnYAxis(self,event):    
        y = self.yAxisCombo.GetValue()
        #print y
        yaxis = y[2:]
        self.yaxis_idx = int( yaxis ) - 1 
        self.VisualizeResult()


    def OnFocus(self,evt):
        pass#print "focus"
    
    def ToggleShowImage(self,evt):
        self.show_image = self.chkShowImage.GetValue()


    def OnTest(self,event):
        self.t = ShapedFrame()
        self.t.Show()
        #print "test"
        #pass
    def DrawPointLabel(self, dc, mDataDict):
        """This is the fuction that defines how the pointLabels are plotted
            dc - DC that will be passed
            mDataDict - Dictionary of data that you want to use for the pointLabel
        
            As an example I have decided I want a box at the curve point
            with some text information about the curve plotted below.
            Any wxDC method can be used.
        """
        # ----------
        dc.SetPen(wx.Pen(wx.BLACK))
        dc.SetBrush(wx.Brush( wx.BLACK, wx.SOLID ) )
        
        sx, sy = mDataDict["scaledXY"] #scaled x,y of closest point
        dc.DrawRectangle( sx-5,sy-5, 10, 10)  #10by10 square centered on point
        px,py = mDataDict["pointXY"]
        cNum = mDataDict["curveNum"]
        pntIn = mDataDict["pIndex"]
        name = mDataDict["legend"]
        #make a string to display
        #s = "Crv# %i, '%s', Pt. (%.2f,%.2f), PtInd %i" %(cNum, legend, px, py, pntIn)
        dc.DrawText(name, sx , sy+1)
        
        if self.show_image:
            # -----------
            img = self.GetImage( name )
            if img != None:
                #print "[", name, img, "]"
                scaled_img = self.ScaleImage( img )
                ( w, h ) = dc.GetSizeTuple()
                img_w = self.image_width
                img_h = self.image_height
                
                img_x = sx - img_w / 2
                img_y = max( sy - img_h, 0 ) 
                if img_x > w - img_w:
                    img_x = w - img_w
                elif img_w < 0:
                    img_x = 0
                
                dc.DrawBitmap( wx.BitmapFromImage( scaled_img ), img_x, img_y, True )

    def GetImage(self, name):
        if name not in self.images.keys():
            image_dir = self.data_config['image_dir']
            image_path = image_dir + "/" + name + ".png"
            #print image_path
            if os.path.isfile( image_path ):
                img = wx.Image( image_path )
                self.images[name] = img
            else:
                self.images[name] = None
            #img.InitAlpha()
            
        return self.images[name]
    def ScaleImage(self, img ):
        win_w = self.image_width
        win_h = self.image_height
        img_w = img.GetWidth()
        img_h = img.GetHeight()
        
        
        #print "1", win_w, win_h, img_w, img_h
        img_rate = float(img_h)/float(img_w)
        win_rate = float(win_h)/float(win_w)
        if img_rate > win_rate:
            #print "img_rate > win_rate"
            new_h = win_h
            new_w = int (img_w * ( float(win_h) / img_h ))
        else:
            #print "img_rate < win_rate"
            new_w = win_w
            new_h = int (img_h * ( float (win_w) / img_w ))
        #print new_w, new_h
        
        img.Rescale( new_w, new_h )
        r = img.GetRed( 0, 0 )
        g = img.GetGreen( 0, 0 )
        b = img.GetBlue( 0, 0 )
        x = self.image_width / 2 - new_w / 2
        y = self.image_height / 2 - new_h / 2
        img.Resize( ( self.image_width, self.image_height ), (x,y), r = r, g = g, b = b )
        img.SetMaskColour(r,g,b)
        img.SetMask(True)
        return img
                
    def OnMouseLeftDown(self,event):
        s= "Left Mouse Down at Point: (%.4f, %.4f)" % self.BivariatePlotter._getXY(event)
        #print s
        dlst= self.BivariatePlotter.GetClosestPoint( self.BivariatePlotter._getXY(event), pointScaled= True)
        if dlst != []:    #returns [] if none

            curveNum, legend, pIndex, pointXY, scaledXY, distance = dlst
            #print legend
            name = legend
            '''img = self.GetImage( name ).Copy()
            scaled_img = self.ScaleImage( img )
            pil = imagetopil( scaled_img )
            draw = ImageDraw.Draw( pil )
            font = ImageFont.truetype( "arial.ttf", 10 )
            draw.text( (5, 5), name, font=font,fill=(255,0,0) )
            del draw
            texted_img = piltoimage( pil )
            r = img.GetRed( 0, 0 )
            g = img.GetGreen( 0, 0 )
            b = img.GetBlue( 0, 0 )
            print "rgb", r, g, b
            img.SetMaskColour(r,g,b)
            img.SetMask(True)
            '''
            
            
            '''
            import ImageFont, ImageDraw
            
            draw = ImageDraw.Draw(image)
            
            # use a bitmap font
            font = ImageFont.load("arial.pil")
            
            draw.text((10, 10), "hello", font=font)
            
            # use a truetype font
            font = ImageFont.truetype("arial.ttf", 15)
            
            draw.text((10, 25), "world", font=font)
            '''            

            img = self.GetImage(name)
            if img:
                scaled_img = self.ScaleImage( img )
                found = False
                for iv in self.ImageViewList:
                    if iv.hasShape:
                        iv.SetImage( scaled_img, name )
                        iv.Show()
                        found = True
                        break
                if not found:
                    iv = ShapedFrame( self, scaled_img, name )
                    iv.Show()
                    self.ImageViewList.append( iv )
                #print "2", rect.x, rect.y, rect.width, rect.height
            #self.Image.Show()

            
            parent = self.GetParent()
            parent.SelectItem( legend )
        #self.SetStatusText(s)
        event.Skip()            #allows plotCanvas OnMouseLeftDown to be called
      
    def OnMotion(self, event):
        #show closest point (when enbled)
        if self.BivariatePlotter.GetEnablePointLabel() == True:
            #make up dict with info for the pointLabel
            #I've decided to mark the closest point on the closest curve
            dlst= self.BivariatePlotter.GetClosestPoint( self.BivariatePlotter._getXY(event), pointScaled= True)
            if dlst != []:    #returns [] if none
                curveNum, legend, pIndex, pointXY, scaledXY, distance = dlst
                #make up dictionary to pass to my user function (see DrawPointLabel) 
                mDataDict= {"curveNum":curveNum, "legend":legend, "pIndex":pIndex,\
                            "pointXY":pointXY, "scaledXY":scaledXY}
                #pass dict to update the pointLabel
                self.BivariatePlotter.UpdatePointLabel(mDataDict)
        event.Skip()           #go to next handler

    def OnChangeCategory(self,event):
        wx.BeginBusyCursor()
        category_name = self.rdCategory.GetStringSelection()
        self.selected_category_name = category_name
        #print self.data
        category_info = [ x.category_data[category_name] for x in self.data ]

        #print category_info
        category_info_set = set( category_info )
        #print category_info_set

        self.category_symbols = {}
        self.category_colors = {}

        symbol_list = [ 'circle', 'square', 'triangle', 'triangle_down', 'cross', 'plus' ]
        color_list = [ 'black', 'blue', 'green', 'red', 'black', 'purple', 'yellow' ]
        i = 0
        for category in category_info_set:
            j = i % len( symbol_list)
            k = i % len( color_list)
            self.category_symbols[category] = symbol_list[j]
            self.category_colors[category] = color_list[k]
            #print category, color_list[k], symbol_list[j]
            i+= 1
        if self.analysis_done:
            self.VisualizeResult()
        wx.EndBusyCursor()
        return

    '''
    def PerformCVA(self):
        self.cva = MdCanonicalVariate()
        #shape_matrix = numpy.zeros( (self.config['data_len'], len( self.data ) ) )
        i = 0
        #print self.data
        actual_data = []
        for obj in self.data:
            actual_data.append( [ float( x ) for x in obj.data ] )
            #shape_matrix[:,i] = obj.data[:]
            #i+= 1
        #self.dataname_list = [ x.name for x in self.data ]
        category_data = [ x.category_data[self.selected_category_name] for x in self.data ]
        #print "category data:", category_data 
        self.cva.SetData( actual_data )
        self.cva.SetCategory( category_data )
        self.cva.Analyze()
        self.loading_listctrl_initialized = False
        self.cva_done = True
        self.VisualizeCVAResult()

    def VisualizeCVAResult(self):
        #print self.pca.raw_eigen_values
        if not self.cva_done:
            return 
        if False:
            self.eigenvalue_listctrl.DeleteAllItems()
            for i in range( len( self.cva.raw_eigen_values ) ):
                #print mo.objname
                self.eigenvalue_listctrl.Append( ( 'CV' + str(i+1), math.floor( self.cva.raw_eigen_values[i] * 100000 + 0.5 ) / 100000, math.floor( self.cva.eigen_value_percentages[i] * 10000 + 0.5 ) / 100 ) )  
        
            if not self.loading_listctrl_initialized:
                self.loading_listctrl.DeleteAllItems()
                self.loading_listctrl.DeleteAllColumns()
                for i in range( len( self.cva.raw_eigen_values ) ):
                    self.loading_listctrl.InsertColumn(i,'CV'+str(i+1), width=60)
                self.loading_listctrl.InsertColumn(0,'Var', width=50)
                self.loading_listctrl_initialized = True
            
            for i in range( len( self.cva.loading[...,0] ) ):
                list = []
                #list[:] = self.pca.loading[i]
                for val in self.cva.loading[i]:
                    #print val, 
                    val = math.floor( val * 1000 + 0.5 ) / 1000
                    #print val
                    list.append( val )
                list.insert( 0, "Var" + str(i+1) )
                self.loading_listctrl.Append( list )
        #print self.pca.loading.shape

        print "CVA result"
        print "-\t" + "\t".join( [ str(pct) for pct in self.cva.eigen_value_percentages[0:10] ] )
        #print pca.eigen_value_percentages[0:10]
        #for 
        m = []
        i = 0
        
        self.xaxis_cv_idx = 0
        self.yaxis_cv_idx = 1
        
        #print self.cva.rotated_matrix
        #print i, self.cva.rotated_matrix[:,i]
        for obj in self.data:
            #print i
            obj.cva_result = self.cva.rotated_matrix[i,:]
            x = obj.cva_result[self.xaxis_cv_idx]
            y = obj.cva_result[self.yaxis_cv_idx]
            m.append( PolyMarker( [ ( x, y ) ], legend = obj.name, colour = self.category_colors[obj.category_data[self.selected_category_name]], marker = self.category_symbols[obj.category_data[self.selected_category_name]] ) )
            i += 1
        
        variance_explained = [ int( x * 10000 ) / 100.0 for x in self.cva.eigen_value_percentages ]
        self.BivariatePlotter.Draw( PlotGraphics( m, "", "CV" + str( self.xaxis_cv_idx + 1) + " (" + str( variance_explained[self.xaxis_cv_idx] ) + "%)", "CV" + str( self.yaxis_cv_idx + 1 ) + " (" + str( variance_explained[self.yaxis_cv_idx] ) + "%)" ) ) 
        #self.BivariatePlotter.SetDataset( self.pca.new_dataset )
        self.BivariatePlotter.Refresh()
        #self.ThreeDViewer.Refresh()
    '''        
    def PrepareData(self, dataset, data_config, analysis_config ):
        self.data_config = data_config
        self.analysis_config = analysis_config
        self.data = dataset
        self.dataname_list = [ x.name for x in self.data ]
        if len( self.data_config['category_list'] ) > 0:
            self.rdCategory= wx.RadioBox( self.panel, wx.NewId(), "Group by", choices=self.data_config['category_list'], style=wx.RA_VERTICAL )
        self.Bind( wx.EVT_RADIOBOX, self.OnChangeCategory, self.rdCategory)
        #self.canvasOptionSizer.Add( )
        self.optionSizer.Add( self.rdCategory, 0, flag=wx.EXPAND)
        
        axis_prefix = self.analysis_config['analysis'][0:2]
        nVariable = len( self.data[0].data )
        for i in range( nVariable ):
            self.xAxisCombo.Append( axis_prefix + str( i + 1) )
            self.yAxisCombo.Append( axis_prefix + str( i + 1) )

        self.xaxis_idx = 0
        self.yaxis_idx = 1

        self.rdCategory.SetStringSelection( self.analysis_config['group_by'] )
        self.OnChangeCategory(None)

        
    def Analyze(self):
        data = []
        filter_by = self.analysis_config['filter_by']
        group_by = self.analysis_config['group_by']
        
        if self.analysis_config['analysis'] == 'PCA':
            self.analyzer = MdPrincipalComponent()
            for obj in self.data:
                if obj.category_data[filter_by] in self.analysis_config['include']:
                    data.append( [ float( x ) for x in obj.data ] )
            self.analyzer.SetData( data )
            self.analyzer.Analyze()
            self.loading_listctrl_initialized = False
            self.analysis_done = True
        elif self.analysis_config['analysis'] == 'CVA':
            self.analyzer = MdCanonicalVariate()
            category_data = []
            for obj in self.data:
                if obj.category_data[filter_by] in self.analysis_config['include']:
                    data.append( [ float( x ) for x in obj.data ] )
                    category_data.append( obj.category_data[group_by] )
            self.analyzer.SetData( data )
            self.analyzer.SetCategory( category_data )
            self.analyzer.Analyze()
            self.loading_listctrl_initialized = False
            self.analysis_done = True
        self.VisualizeResult()

    def VisualizeResult(self):
        #print self.pca.raw_eigen_values
        if not self.analysis_done:
            return 
        if False:
            self.eigenvalue_listctrl.DeleteAllItems()
            for i in range( len( self.analyzer.raw_eigen_values ) ):
                #print mo.objname
                self.eigenvalue_listctrl.Append( ( 'PC' + str(i+1), math.floor( self.analyzer.raw_eigen_values[i] * 100000 + 0.5 ) / 100000, math.floor( self.analyzer.eigen_value_percentages[i] * 10000 + 0.5 ) / 100 ) )  
        
            if not self.loading_listctrl_initialized:
                self.loading_listctrl.DeleteAllItems()
                self.loading_listctrl.DeleteAllColumns()
                for i in range( len( self.analyzer.raw_eigen_values ) ):
                    self.loading_listctrl.InsertColumn(i,'PC'+str(i+1), width=60)
                self.loading_listctrl.InsertColumn(0,'Var', width=50)
                self.loading_listctrl_initialized = True
            
            for i in range( len( self.analyzer.loading[...,0] ) ):
                list = []
                #list[:] = self.pca.loading[i]
                for val in self.analyzer.loading[i]:
                    #print val, 
                    val = math.floor( val * 1000 + 0.5 ) / 1000
                    #print val
                    list.append( val )
                list.insert( 0, "Var" + str(i+1) )
                self.loading_listctrl.Append( list )
        #print self.pca.loading.shape

        #print "PCA result"
        #print "-\t" + "\t".join( [ str(pct) for pct in self.pca.eigen_value_percentages ] )
        #print pca.eigen_value_percentages[0:10]
        #for 
        m = []
        
        
        #print "x, y", self.xaxis_idx, self.yaxis_idx
        axis_prefix = self.analysis_config['analysis'][0:2]

        self.xAxisCombo.SetStringSelection( axis_prefix + str( self.xaxis_idx + 1 ) )
        self.yAxisCombo.SetStringSelection( axis_prefix + str( self.yaxis_idx + 1 ) )

        filter_by = self.analysis_config['filter_by']
        
        i = 0
        
        for obj in self.data:
            if obj.category_data[filter_by] in self.analysis_config['include']:
                obj.analysis_result = [ 0 for x in range( self.analyzer.nVariable ) ]
                for j in range( self.analyzer.nVariable ):
                    obj.analysis_result[j] = self.analyzer.rotated_matrix[i,j]
                #obj.pca_result = self.pca.rotated_matrix[i,]
                #print obj.pca_result
                x = obj.analysis_result[self.xaxis_idx]
                y = obj.analysis_result[self.yaxis_idx]
                m.append( PolyMarker( [ ( x, y ) ], legend = obj.name, colour = self.category_colors[obj.category_data[self.selected_category_name]], marker = self.category_symbols[obj.category_data[self.selected_category_name]] ) )
                i += 1
         
        variance_explained = [ int( x * 10000 ) / 100.0 for x in self.analyzer.eigen_value_percentages ]
        self.BivariatePlotter.Draw( PlotGraphics( m, "", axis_prefix + str( self.xaxis_idx + 1) + " (" + str( variance_explained[self.xaxis_idx] ) + "%)", axis_prefix + str( self.yaxis_idx + 1 ) + " (" + str( variance_explained[self.yaxis_idx] ) + "%)" ) ) 
        #self.BivariatePlotter.SetDataset( self.pca.new_dataset )
        self.BivariatePlotter.Refresh()
        #self.ThreeDViewer.Refresh()


      #m.append( PolyMarker( [ ( x, y ) ], legend = object.objname + " (" + key + ") (" + str(x) + "," + str(y) + ")", colour = self.group_colors[key], marker = self.group_symbols[key] ) )
