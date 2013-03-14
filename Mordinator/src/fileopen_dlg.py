import wx
import yaml

ID_SPECIMENID_ADD_BUTTON = 1001
ID_SPECIMENID_REMOVE_BUTTON = 1002
ID_CATEGORY_ADD_BUTTON = 1003
ID_CATEGORY_REMOVE_BUTTON = 1004
ID_DATA_ADD_BUTTON = 1005
ID_DATA_REMOVE_BUTTON = 1006
ID_OK_BUTTON = 1007
ID_CANCEL_BUTTON = 1008
ID_IMAGE_DIR_BUTTON = 1009
ID_ALLDATA_CHECKBOX = 1010

PREFERENCE_FILENAME = "modrinator.pref"

class FileOpenDialog( wx.Dialog ):
    def __init__(self,parent,id=-1):
        wx.Dialog.__init__(self,parent,id,'File Open', size = (640,480))
        self.panel = panel = wx.Panel( self, -1 )
        self.preference = {}
        pref_string = ''
        
        import os
        from appdirs import user_data_dir
        appname = "Mordinator"
        appauthor = "DiploSoft"
        
        homedir = os.path.expanduser("~")
        #print homedir
        homedir= user_data_dir( appname, appauthor )
        #print homedir
        #ho
        try: 
            os.makedirs(homedir)
        except OSError:
            if not os.path.isdir(homedir):
                raise

        self.pref_filename =os.path.join( homedir, PREFERENCE_FILENAME)

        if os.path.exists( self.pref_filename):
            fh = open( self.pref_filename, 'r')
            pref_string = fh.read()
            fh.close()
        if pref_string != '':
            self.preference = yaml.load( pref_string )
        
        
        mainSizer = wx.BoxSizer( wx.HORIZONTAL )
    
    
        columnLabel = wx.StaticText( panel, -1, 'Columns', style=wx.ALIGN_CENTER )

        specimenIDLabel = wx.StaticText( panel, -1, 'Specimen ID', style=wx.ALIGN_CENTER )
        categoryLabel = wx.StaticText( panel, -1, 'Category', style=wx.ALIGN_CENTER )
        dataLabel = wx.StaticText( panel, -1, 'Data', style=wx.ALIGN_CENTER )
        imageDirLabel = wx.StaticText( panel, -1, 'Image Dir', style=wx.ALIGN_CENTER )

        specimenID = wx.TextCtrl(panel, -1, '')
        imageDir = wx.TextCtrl(panel, -1, '')
        self.specimenID = specimenID
        self.imageDir = imageDir

        columnList = wx.ListBox( panel, -1, choices=(),size=(150,300), style=wx.LB_EXTENDED )
        categoryList = wx.ListBox( panel, -1, choices=(),size=(150,40), style=wx.LB_EXTENDED )
        dataList = wx.ListBox( panel, -1, choices=(),size=(150,200), style=wx.LB_EXTENDED )

        buttonSize = ( 20, 20 )
        addButton = '>'
        removeButton = '<'
        self.allDataCheckbox = wx.CheckBox( panel, ID_ALLDATA_CHECKBOX, "All" )
        self.saveConfigCheckbox = wx.CheckBox( panel, ID_ALLDATA_CHECKBOX, "Save Preferences" )
        specimenIDAddButton = wx.Button( panel, ID_SPECIMENID_ADD_BUTTON, addButton, size= buttonSize )
        specimenIDRemoveButton = wx.Button( panel, ID_SPECIMENID_REMOVE_BUTTON, removeButton, size=buttonSize )
        categoryAddButton = wx.Button( panel, ID_CATEGORY_ADD_BUTTON, addButton, size=buttonSize )
        categoryRemoveButton = wx.Button( panel, ID_CATEGORY_REMOVE_BUTTON, removeButton, size=buttonSize )
        dataAddButton = wx.Button( panel, ID_DATA_ADD_BUTTON, addButton, size=buttonSize )
        dataRemoveButton = wx.Button( panel, ID_DATA_REMOVE_BUTTON, removeButton, size=buttonSize )
        okButton = wx.Button( panel, ID_OK_BUTTON, "OK", size=(100,30))
        cancelButton = wx.Button( panel, ID_CANCEL_BUTTON, "CANCEL", size=(100,30))
        imageDirButton = wx.Button( panel, ID_IMAGE_DIR_BUTTON, "Browse", size=(100,30))

        self.Bind(wx.EVT_BUTTON, self.OnAddSpecimenID, id=ID_SPECIMENID_ADD_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveSpecimenID, id=ID_SPECIMENID_REMOVE_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnAddCategory, id=ID_CATEGORY_ADD_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveCategory, id=ID_CATEGORY_REMOVE_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnAddData, id=ID_DATA_ADD_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveData, id=ID_DATA_REMOVE_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=ID_OK_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=ID_CANCEL_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnImageDir, id=ID_IMAGE_DIR_BUTTON)

        self.columnList = columnList
        self.categoryList = categoryList
        self.dataList = dataList

        leftSizer = wx.BoxSizer( wx.VERTICAL )
        leftSizer.Add( columnLabel )
        leftSizer.Add( columnList )
        
        buttonSizer1 = wx.BoxSizer( wx.VERTICAL )
        buttonSizer2 = wx.BoxSizer( wx.VERTICAL )
        buttonSizer3 = wx.BoxSizer( wx.VERTICAL )
        buttonSizer1.Add( specimenIDAddButton )
        buttonSizer1.Add( specimenIDRemoveButton )
        buttonSizer2.Add( categoryAddButton )
        buttonSizer2.Add( categoryRemoveButton )
        buttonSizer3.Add( self.allDataCheckbox )
        buttonSizer3.Add( dataAddButton )
        buttonSizer3.Add( dataRemoveButton )
   
        specimenSizer = wx.BoxSizer( wx.VERTICAL )
        categorySizer = wx.BoxSizer( wx.VERTICAL )
        dataSizer = wx.BoxSizer( wx.VERTICAL )

        specimenSizer.Add( specimenIDLabel )
        specimenSizer.Add( specimenID )
        categorySizer.Add( categoryLabel )
        categorySizer.Add( categoryList )
        dataSizer.Add( dataLabel )
        dataSizer.Add( dataList )
        
        sizer1 = wx.BoxSizer( wx.HORIZONTAL)
        sizer2 = wx.BoxSizer( wx.HORIZONTAL)
        sizer3 = wx.BoxSizer( wx.HORIZONTAL)
        
        sizer1.Add( buttonSizer1, flag = wx.ALIGN_CENTER_VERTICAL )
        sizer1.Add( specimenSizer )
        sizer2.Add( buttonSizer2, flag = wx.ALIGN_CENTER_VERTICAL )
        sizer2.Add( categorySizer )
        sizer3.Add( buttonSizer3, flag = wx.ALIGN_CENTER_VERTICAL )
        sizer3.Add( dataSizer )
        
        rightSizer = wx.BoxSizer( wx.VERTICAL )
        rightSizer.Add( sizer1 )
        rightSizer.Add( sizer2 )
        rightSizer.Add( sizer3 )
        
        imageDirSizer = wx.BoxSizer( wx.HORIZONTAL )
        imageDirSizer.Add( imageDirLabel )        
        imageDirSizer.Add( imageDir )
        imageDirSizer.Add( imageDirButton )


        topSizer = wx.BoxSizer( wx.HORIZONTAL )
        topSizer.Add( leftSizer )
        topSizer.Add( rightSizer )

        okcancelSizer = wx.BoxSizer( wx.HORIZONTAL )
        okcancelSizer.Add( self.saveConfigCheckbox )
        okcancelSizer.Add( okButton )
        okcancelSizer.Add( cancelButton )
        
        mainSizer = wx.BoxSizer( wx.VERTICAL )
        mainSizer.Add( topSizer )
        mainSizer.Add( imageDirSizer )
        mainSizer.Add( okcancelSizer )
        panel.SetSizer(mainSizer)
        panel.Fit()

        
        self.config = {}
        
        return 

    def SetFilepath(self, filepath):
        self.filepath = filepath
        
        if filepath in self.preference.keys():
            data_config = self.preference[filepath]
            self.columnList.SetStringSelection( data_config['specimenid'] )
            self.OnAddSpecimenID(None)
            for cat in data_config['category_list']:
                self.columnList.SetStringSelection( cat )
            self.OnAddCategory(None)
            for cat in data_config['data_list']:
                self.columnList.SetStringSelection( cat )
            self.OnAddData(None)
            self.imageDir.SetValue( data_config['image_dir'])
            #print self.preference[filepath]
            #print "load saved settings!"

    def OnOK(self,evt):
        self.config['image_dir'] = self.imageDir.GetValue()
        self.config['specimenid'] = self.specimenID.GetValue()
        
        if self.saveConfigCheckbox.GetValue():
            self.preference[self.filepath] = self.config
            preference_str = yaml.dump( self.preference )
            fh = file( self.pref_filename, 'w' )
            fh.write( preference_str )
            fh.close()
        
        
        self.EndModal( wx.ID_OK )
        return

    def OnCancel(self,evt):
        self.EndModal( wx.ID_ERROR )
        return
    
    def OnImageDir(self,evt):
        dlg = wx.DirDialog( self )
        dlg.ShowModal()
        dir = dlg.GetPath()
        self.imageDir.SetValue( dir )
        return

    def OnAddSpecimenID(self, evt):    
        
        #print "add specimen"
        if self.specimenID.GetValue() != "":
            return

        for j in range( self.columnList.GetCount() ):
            if self.columnList.IsSelected( j ):
                specimenID = self.columnList.GetString( j )
                self.columnList.Delete( j )
                break
        
        #idx = self.columnList.GetSelection()
        #specimenID = self.columnList.GetString( idx )
        #self.columnList.Delete( idx )
        self.specimenID.SetValue( specimenID )

        self.config['specimenid'] = specimenID
        
        return
        
    def OnRemoveSpecimenID(self, evt):
        #print "remove specimen"
        specimenID = self.specimenID.GetValue()
        self.columnList.Append( specimenID )
        self.specimenID.SetValue( '' )
        self.config['specimenid'] = ''
        return
    
    def OnAddCategory(self, evt):
        #print "add category"
        category_list = self.MoveItemsBetweenListBox( self.columnList, self.categoryList )
        
        return
        
    def OnRemoveCategory(self, evt):
        #print "remove category"
        self.MoveItemsBetweenListBox( self.categoryList, self.columnList )
        return
    
    def OnAddData(self, evt):
        if self.allDataCheckbox.IsChecked():
            for i in range( self.columnList.GetCount() ):
                self.columnList.Select( i )
        #print "add data"
        self.MoveItemsBetweenListBox( self.columnList, self.dataList )
        return
        
    def OnRemoveData(self, evt):
        #print "remove data"
        if self.allDataCheckbox.IsChecked():
            for i in range( self.dataList.GetCount() ):
                self.dataList.Select( i )
        self.MoveItemsBetweenListBox( self.dataList, self.columnList )
        return

    def MoveItemsBetweenListBox( self, lb_from, lb_to ):
        j = 0
        for i in range( lb_from.GetCount() ):
            if lb_from.IsSelected( j ):
                colname= lb_from.GetString( j )
                lb_from.Delete( j )
                lb_to.Append( colname )
            else:
                j = j + 1
        self.config['data_list'] = []
        self.config['category_list'] = []
        for j in range( self.dataList.GetCount() ):
            data_col = self.dataList.GetString( j )
            #print data_col
            self.config['data_list'].append( data_col )
        for j in range( self.categoryList.GetCount() ):
            category_col = self.categoryList.GetString( j ) 
            #print category_col
            self.config['category_list'].append( category_col )
            
    
    def SetColumns(self, column_list ):
        #print column_list
        self.columnList.InsertItems( column_list, 0 )


    def OK(self,evt):
        
        return wx.OKAY
    def Cancel(self, evt):
        return wx.CANCEL
    