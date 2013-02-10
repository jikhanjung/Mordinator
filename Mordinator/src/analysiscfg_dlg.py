import wx

ID_ANALYSIS_RADIO = 1001
ID_CATEGORY_COMBO = 1002
ID_FILTER_COMBO = 1003
ID_OK_BUTTON = 1011
ID_CANCEL_BUTTON = 1012

class AnalysisConfigDialog( wx.Dialog ):
    def __init__(self,parent,id=-1):
        wx.Dialog.__init__(self,parent,id, 'Analyze Data', size = (640,480))
        self.panel = panel = wx.Panel( self, -1 )
    
        analysisLabel = wx.StaticText(panel, -1, 'Analysis', style=wx.ALIGN_RIGHT)
        self.analysisRadio = wx.RadioBox( panel, ID_ANALYSIS_RADIO, "", choices=["PCA", "CVA"], style=wx.RA_HORIZONTAL)
        
        categoryLabel = wx.StaticText( panel, -1, 'Group by', style=wx.ALIGN_CENTER )
        filterLabel = wx.StaticText( panel, -1, 'Filter by', style=wx.ALIGN_CENTER )
        #filterLabel = wx.StaticText( panel, -1, 'Filter', style=wx.ALIGN_CENTER )
        self.categoryCombo = wx.ComboBox( panel, ID_CATEGORY_COMBO, "", (80,20),wx.DefaultSize, [], wx.CB_DROPDOWN )
        self.filterCombo = wx.ComboBox( panel, ID_FILTER_COMBO, "", (80,20),wx.DefaultSize, [], wx.CB_DROPDOWN )
        self.filterList= wx.ListBox( panel, -1, choices=(),size=(150,300), style=wx.LB_EXTENDED )
        self.Bind( wx.EVT_COMBOBOX, self.OnCategoryChange, id=ID_CATEGORY_COMBO )
        self.Bind( wx.EVT_COMBOBOX, self.OnFilterChange, id=ID_FILTER_COMBO )

        okButton = wx.Button( panel, ID_OK_BUTTON, "OK", size=(100,30))
        cancelButton = wx.Button( panel, ID_CANCEL_BUTTON, "CANCEL", size=(100,30))
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=ID_OK_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=ID_CANCEL_BUTTON)

        sizer1 = wx.BoxSizer( wx.VERTICAL )
        sizer1.Add( analysisLabel )
        sizer1.Add( self.analysisRadio )
        
        sizer2 = wx.BoxSizer( wx.VERTICAL )
        sizer21 = wx.BoxSizer( wx.HORIZONTAL )
        sizer22 = wx.BoxSizer( wx.HORIZONTAL )
        sizer23 = wx.BoxSizer( wx.VERTICAL )
        
        sizer23.Add( self.filterCombo )
        sizer23.Add( self.filterList )
        sizer21.Add( categoryLabel )
        sizer21.Add( self.categoryCombo )
        sizer22.Add( filterLabel )
        sizer22.Add( sizer23 )
        sizer2.Add( sizer21 )
        sizer2.Add( sizer22 )
        
        sizer3 = wx.BoxSizer( wx.HORIZONTAL )
        sizer4 = wx.BoxSizer( wx.HORIZONTAL )
        sizer3.Add( sizer1 )
        sizer3.Add( sizer2 )
        sizer4.Add( okButton )
        sizer4.Add( cancelButton )
        
        mainSizer = wx.BoxSizer( wx.VERTICAL )
        mainSizer.Add( sizer3 )
        mainSizer.Add( sizer4 )
        panel.SetSizer(mainSizer)
        panel.Fit()

        
        self.analysis_config = {}
        
        return
    
    def OnOK(self,evt):
        self.analysis_config['include'] = []
        self.analysis_config['analysis'] = self.analysisRadio.GetStringSelection()
        for idx in range( self.filterList.GetCount() ):
            if self.filterList.IsSelected( idx ):
                category_data = self.filterList.GetString( idx )
                self.analysis_config['include'].append( category_data )
        #print self.analysis_config
        self.EndModal( wx.ID_OK )
        return

    def OnCancel(self,evt):
        self.EndModal( wx.ID_ERROR )
        return
    
    def SetDataset( self, dataset ):
        self.dataset = dataset
        category_list = self.dataset['category_list']
        self.categoryCombo.AppendItems( category_list )
        self.categoryCombo.Select( 0 )
        self.OnCategoryChange( None )
        self.filterCombo.AppendItems( category_list )
        self.filterCombo.Select( 0 )
        self.OnFilterChange( None )

    def OnCategoryChange( self, evt ):
        selected_category = self.categoryCombo.GetValue()
        self.analysis_config['group_by'] = selected_category
        return

    def OnFilterChange( self, evt ):
        #idx = self.categoryCombo.GetStringSelection()
        selected_category = self.filterCombo.GetValue()
        self.analysis_config['filter_by'] = selected_category
        #print "key:", selected_category
        self.filterList.Clear()
        data_list = list( set( [ obj.category_data[selected_category] for obj in self.dataset['data'] ] ) )
        
        self.filterList.AppendItems( data_list )
        for idx in range( self.filterList.GetCount() ):
            self.filterList.Select( idx )
        return

    
