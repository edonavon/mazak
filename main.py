from OCC import VERSION
# First check which GUI library to use
# Check wxPython
import wx
import sys, time, math, os, os.path
import struct
import xml.etree.ElementTree as ET
_ = wx.GetTranslation
import wx.propgrid as wxpg
from wx.lib.agw import ultimatelistctrl as ULC

from OCC.BRepPrimAPI import *
from OCC.BRepAlgoAPI import *
from OCC.gp import *

import math
    
import wx.lib.mixins.listctrl  as  listmix
HAVE_WX = True
USED_BACKEND = 'wx'

########################################################################
class SecondFrame(wx.Frame):
  """"""

  #----------------------------------------------------------------------
  def __init__(self, message):
       """Constructor"""
       wx.Frame.__init__(self, None, title="Error")
       panel = wx.Panel(self)
       txt = wx.StaticText(panel, label=message)

########################################################################

########################################################################
class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    ''' TextEditMixin allows any column to be edited. '''
 
    #----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)
 
########################################################################

class MyPopupMenu(wx.Menu):
    def __init__(self, WinName):
        wx.Menu.__init__(self)

        self.WinName = WinName

        item = wx.MenuItem(self, wx.NewId(), "Delete Unit")
        self.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnItem1, item)

        item = wx.MenuItem(self, wx.NewId(),"Duplicate Unit")
        self.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnItem2, item)

        item = wx.MenuItem(self, wx.NewId(),"Export Unit")
        self.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnItem3, item)

        item = wx.MenuItem(self, wx.NewId(),"Insert Unit")
        submenu = wx.Menu()
       
        sitem = wx.MenuItem(self, wx.NewId(), "LIN")
        submenu.AppendItem(sitem)
        self.Bind(wx.EVT_MENU, self.OnItem4, sitem)

        sitem = wx.MenuItem(self, wx.NewId(), "TPR")
        submenu.AppendItem(sitem)
        self.Bind(wx.EVT_MENU, self.OnItem5, sitem)
        
        sitem = wx.MenuItem(self, wx.NewId(), "FACING")
        submenu.AppendItem(sitem)
        self.Bind(wx.EVT_MENU, self.OnItem6, sitem)

        item.SetSubMenu(submenu)
          
        self.AppendItem(item)
        
        
    def OnItem1(self, event):
        global prgLineAction
        prgLineAction = "deleteUnit"

    def OnItem2(self, event):
        global prgLineAction
        prgLineAction = "duplicateUnit"

    def OnItem3(self, event):
        global prgLineAction
        prgLineAction = "exportUnit"

    def OnItem4(self, event):
        global prgLineAction
        prgLineAction = "insertUnit_LIN"

    def OnItem5(self, event):
        global prgLineAction
        prgLineAction = "insertUnit_TPR"

    def OnItem6(self, event):
        global prgLineAction
        prgLineAction = "insertUnit_FACING"
        
class Page(wx.Panel):

    def loadProgram(self, fileName):
        self.fileName = fileName
        self.mazakPrg = self.getCommands(self.fileName)
        self.list_ctrl_info = []
        self.list_ctrl.DeleteAllItems()
        self.list_ctrl.DeleteAllColumns()
        for i in range(1,21):
            self.list_ctrl.InsertColumn(i, '')
            self.list_ctrl.SetColumnWidth(i, 50)
        self.printProgram()
        
    def refreshProgram(self, evt):
        self.mazakPrg = self.getCommands(self.fileName)
        self.list_ctrl_info = []
        self.list_ctrl.DeleteAllItems()
        self.list_ctrl.DeleteAllColumns()
        for i in range(1,21):
            self.list_ctrl.InsertColumn(i, '')
            self.list_ctrl.SetColumnWidth(i, 50)
        self.printProgram()
    
    def playProgram(self, evt):
        unitState = ""
        subUnitState =""
        XZ = []
        FACE_SPT_X = 0
        for i in range(1,self.list_ctrl.GetItemCount()):
            if self.list_ctrl.GetItemText(i,2) == "":
                subUnitState = ""
                
            if self.list_ctrl.GetItemText(i,2) == "UNIT":
                subUnitState = ""
                if self.list_ctrl.GetItemText(i+1,2) == "MAT":
                    OD = float(self.list_ctrl.GetItemText(i+1,4))
                    ID = float(self.list_ctrl.GetItemText(i+1,5))
                    LEN = float(self.list_ctrl.GetItemText(i+1,6))
                    WORKFACE = float(self.list_ctrl.GetItemText(i+1,7))
                    unitState = "MAT"
                elif self.list_ctrl.GetItemText(i+1,2) == "FACING":
                    U_SPT_X = self.list_ctrl.GetItemText(i+1,4)
                    U_SPT_Z = self.list_ctrl.GetItemText(i+1,5)
                    unitState = "FACING"
                elif self.list_ctrl.GetItemText(i+1,2) == "BAR":
                    U_SPT_X = self.list_ctrl.GetItemText(i+1,4)
                    U_SPT_Z = self.list_ctrl.GetItemText(i+1,5)
                    unitState = "BAR"
                else:
                    unitState = "OTHER"

            print unitState, subUnitState
            if subUnitState == "FIG" and unitState == "FACING":
                lineNo = int(self.list_ctrl.GetItemText(i,1))
                SPT_X = float(self.list_ctrl.GetItemText(i,2))
                SPT_Z = float(self.list_ctrl.GetItemText(i,3))
                FPT_X = float(self.list_ctrl.GetItemText(i,4))
                FPT_Z = float(self.list_ctrl.GetItemText(i,5))
                
                FACE_SPT_X = float(SPT_X)
                FACE_SPT_Z = float(SPT_Z)
                FACE_FPT_X = float(FPT_X)
                FACE_FPT_Z = float(FPT_Z)
                
                    
            if subUnitState == "FIG" and unitState == "BAR":
                
                lineNo = int(self.list_ctrl.GetItemText(i,1))
                FPT_X = float(self.list_ctrl.GetItemText(i,6))
                FPT_Z = float(self.list_ctrl.GetItemText(i,7))
                SPT_X = -1
                SPT_Z = -1
                
                S_CNR = float(self.list_ctrl.GetItemText(i,3))
                F_CNR = float(self.list_ctrl.GetItemText(i,8))
                if lineNo == 1:
                    if(self.list_ctrl.GetItemText(i,4) != "*"):
                        SPT_X = float(self.list_ctrl.GetItemText(i,4))
                        SPT_Z = float(self.list_ctrl.GetItemText(i,5))
                    else:
                        SPT_X = FPT_X
                        SPT_Z = U_SPT_Z
                else:
                    if(self.list_ctrl.GetItemText(i,4) != "*"):
                        SPT_X = float(self.list_ctrl.GetItemText(i,4))
                        SPT_Z = float(self.list_ctrl.GetItemText(i,5))
                    else:
                        SPT_X = FPT_X
                        SPT_Z = U_SPT_Z
                    
                
                #print "line ", SPT_X, SPT_Z, FPT_X, FPT_Z
                
                XZ.append([float(SPT_X), float(SPT_Z), float(FPT_X), float(FPT_Z), float(S_CNR), float(F_CNR)])

                U_SPT_X = FPT_X
                U_SPT_Z = FPT_Z
                
            if self.list_ctrl.GetItemText(i,1) == "FIG":
                subUnitState = "FIG"
        
        
        display.EraseAll()
        #display.SetBackgroundImage("eureka.bmp")
        
        
        #pos1 = gp_Ax2(gp_Pnt(gp_XYZ(-LEN,0,0)), gp_Dir(1,0,0))
        #display.DisplayMessage(gp_Pnt(gp_XYZ(-LEN,0,0)), "fdsfdsfdsfdsfdsf",height=None, message_color=None, update=False)
        #display.DisplayShape(BRepPrimAPI_MakeCylinder(pos1, OD/2, LEN).Shape(),update=True , color=0x000055, transparency=0.7)
        
        #display.DisplayShape(shapeStock, update=True, color=0x000055, transparency=0.7)
        
        removedSolids = []
        
        XZ[0]
        for line in XZ:
            Length = line[3]-line[1]
            print "Z0=%s, X0=%s, X=%s, Z=%s, S_CNR=%s, F_CNR=%s"%(line[1], line[0]/2, line[2]/2, Length, line[4], line[5])
            
            F_CNR = line[5]
            
            S_CNR = line[4]
            Length = Length - S_CNR - F_CNR
            
            pos1 = gp_Ax2(gp_Pnt(gp_XYZ(-line[3]+F_CNR,0,0)), gp_Dir(1,0,0))
            pos2 = gp_Ax2(gp_Pnt(gp_XYZ(-line[1]-S_CNR,0,0)), gp_Dir(1,0,0))         
            pos3 = gp_Ax2(gp_Pnt(gp_XYZ(-line[3]+F_CNR,0,0)), gp_Dir(1,0,0))     
            
            pi = math.pi

            if S_CNR != 0:
                a1 = -2*pi*0
                a2 = 2*pi*0.25; 
                restScnrMaterial = BRepPrimAPI_MakeTorus(pos2,line[0]/2-S_CNR,S_CNR,a1,a2).Shape()
                tmpShape = BRepPrimAPI_MakeCylinder(pos2, OD/2, S_CNR).Shape()
                removedScnrMaterial = BRepAlgoAPI_Cut(tmpShape, restScnrMaterial).Shape()
                #display.DisplayShape(restScnrMaterial)
                #display.DisplayShape(removedScnrMaterial, color=0x000055, transparency=0.3)
                removedSolids.append(removedScnrMaterial)

            if F_CNR != 0:
                a1 = -2*pi*0.25
                a2 = 2*pi*0; 
                restFcnrMaterial = BRepPrimAPI_MakeTorus(pos3,line[0]/2-F_CNR,F_CNR,a1,a2).Shape()
                tmpShape = BRepPrimAPI_MakeCylinder(pos3, OD/2, F_CNR).Shape()
                removedFcnrMaterial = BRepAlgoAPI_Cut(tmpShape, restFcnrMaterial).Shape()
                #display.DisplayShape(restFcnrMaterial)
                #display.DisplayShape(removedFcnrMaterial, color=0x000055, transparency=0.3)
                removedSolids.append(removedFcnrMaterial)

            tmpShape = BRepPrimAPI_MakeCylinder(pos1, OD/2, Length).Shape()
            if line[0] == line [2] :
                restMaterial = BRepPrimAPI_MakeCylinder(pos1, line[0]/2, Length).Shape()
            else:
                restMaterial = BRepPrimAPI_MakeCone(pos1, line[2]/2, line[0]/2, Length).Shape()
            
            removedMaterial = BRepAlgoAPI_Cut(tmpShape, restMaterial).Shape()
            #display.DisplayShape(restMaterial)
            #display.DisplayShape(removedMaterial, color=0x000055, transparency=0.3)
            removedSolids.append(removedMaterial)

        # Add Shape
        pos1 = gp_Ax2(gp_Pnt(gp_XYZ(-LEN,0,0)), gp_Dir(1,0,0))
        shape = BRepPrimAPI_MakeCylinder(pos1, OD/2, LEN+WORKFACE).Shape()
        
        # Remove Face
        if FACE_SPT_X > 0:
            pos1 = gp_Ax2(gp_Pnt(gp_XYZ(WORKFACE-float(FACE_SPT_Z),0,0)), gp_Dir(1,0,0))
            face = BRepPrimAPI_MakeCylinder(pos1, float(FACE_SPT_X)/2, float(FACE_SPT_Z)).Shape()
            print FACE_SPT_X, FACE_SPT_Z
            #FACE_FPT_X 
            #FACE_FPT_Z 

            shape = BRepAlgoAPI_Cut(shape, face).Shape()
            

        # Remove Bar (and more later...)
        for removedSolid in removedSolids:
            shape = BRepAlgoAPI_Cut(shape, removedSolid).Shape()
        
        display.EraseAll()
        display.DisplayShape(shape)
            
    
                
    def OnFileSelect(self, evt):
        item = evt.GetSelection()
        self.loadProgram("programs/"+self.fileNames[item])
                
    def OnPrgLineClick(self, evt):
        global prgLineAction
        lineNumber = int(evt.GetText())
        
        unitAddr = int(self.list_ctrl.GetItemText(lineNumber-1,18))
        unitName = self.list_ctrl.GetItemText(lineNumber-1,2)
        
        fR = open(self.fileName, "rb")       
        before = fR.read(unitAddr)
        copy   = fR.read(100)
        after = fR.read()
        fR.close()
        
        self.PopupMenu(MyPopupMenu(wx.RED))
        print prgLineAction
        
        if prgLineAction == "deleteUnit":
            fW = open(self.fileName, "wb")
            fW.write(before)
            fW.write(after)
            fW.close()
        elif prgLineAction == "duplicateUnit":
            fW = open(self.fileName, "wb")
            fW.write(before)
            fW.write(copy)
            fW.write(copy)
            fW.write(after)
            fW.close()
        elif prgLineAction == "exportUnit":
            fName = self.fileName+"_"+unitName+".unit"
            fW = open(fName, "wb")
            fW.write(copy)
            fW.close()
        elif prgLineAction == "insertUnit_LIN":
            fR = open("units/LIN.unit", "rb")       
            unit   = fR.read(100)
            fR.close()
            fW = open(self.fileName, "wb")
            fW.write(before)
            fW.write(copy)
            fW.write(unit)
            fW.write(after)
            fW.close()
        elif prgLineAction == "insertUnit_TPR":
            fR = open("units/TPR.unit", "rb")       
            unit   = fR.read(100)
            fR.close()
            fW = open(self.fileName, "wb")
            fW.write(before)
            fW.write(copy)
            fW.write(unit)
            fW.write(after)
            fW.close()           
        elif prgLineAction == "insertUnit_FACING":
            fR = open("units/FACING.unit", "rb")       
            unit   = fR.read(400)
            fR.close()
            fW = open(self.fileName, "wb")
            fW.write(before)
            fW.write(copy)
            fW.write(unit)
            fW.write(after)
            fW.close() 
        else:
            pass
            
        prgLineAction = ""
        
        self.loadProgram(self.fileName)
        
        
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=(0,0))
        
        self.fileName = "programs/VILLA.PBG"

        self.mazakPrg = self.getCommands(self.fileName)

        #self.paint = wx.Panel(self, wx.ID_ANY, pos=(0,550), size=(1100,400))
        #self.on_paint(self.paint)
        
        panel = wx.Panel(self, wx.ID_ANY)
        
        wx.Button(panel, 1, "Refresh", pos=(5, 5), size=(100,25))
        self.Bind(wx.EVT_BUTTON, self.refreshProgram, id=1)

        wx.Button(panel, 2, "Play", pos=(120, 5), size=(100,25))
        self.Bind(wx.EVT_BUTTON, self.playProgram, id=2)
        
        self.fileNames = ['AXIS28X140_CPY.PBG' , 'VILLA.PBG' , 'CONUS.PBG' , 'TEST1.PBG', 'T+.MZK', 'T2.MZK', 'T32.MZK' ]
        wx.ComboBox(panel, -1, pos=(220, 5), size=(150, -1), choices=self.fileNames, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.OnFileSelect)

        self.list_ctrl = EditableListCtrl(panel, style=wx.LC_REPORT, pos=(0,30), size=(1000, 500))
        #self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list_ctrl)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.updateProgramParameter, self.list_ctrl)

        self.list_ctrl_info = []
        
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnPrgLineClick, self.list_ctrl)
        
        self.list_ctrl.SetBackgroundColour(wx.BLACK) 
        
        for i in range(1,21):
            self.list_ctrl.InsertColumn(i, '')
            self.list_ctrl.SetColumnWidth(i, 50)

        self.sizer = wx.BoxSizer()
        #self.sizer.Add(self.list_ctrl, proportion=0, flag=wx.EXPAND)
        self.sizer.Add(panel, proportion=1, flag=wx.EXPAND)

        self.SetSizerAndFit(self.sizer)
        self.SetSize((1400, 900))   
        
        self.printProgram()
        
    def updateProgramParameter(self,event):
        if self.list_ctrl_info[event.m_itemIndex][event.m_col][4] == "readData":
            fW = open(self.fileName, "r+b")
            fW.seek(self.list_ctrl_info[event.m_itemIndex][event.m_col][3])
            newValue = event.GetText()
            data = struct.pack('<I',float(newValue)*10000)
            fW.write(data)
            fW.close()
        else:
            frame = SecondFrame("This value canont be changed")
            frame.Show()
            print self.list_ctrl.GetItemText(event.m_itemIndex,event.m_col)
            
        #print event.m_itemIndex, event.m_col
        #print self.list_ctrl_info[event.m_itemIndex][event.m_col]

    def getCommands( self, fileName ):

        tree = ET.parse('qts200m.xml')
        root = tree.getroot()

        unitType = []
        for i in range(1,257):
            unitType.append("TBD")
            
        for unit in root:
            tmpArr = []
            for param in unit:
                
                if param.get('type') == "readPattern":
                    tmpPtn = []
                    for ff in param:
                        tmpPtn.append([ff.get('name'), ff.get('value'), ff.get('type')])
                    tmpArr.append([param.get('name'), param.get('pos'), param.get('type'),tmpPtn])
                else:
                    visArr = []
                    if param.get('visible'):
                        visArr = param.get('visible').split(',')

                    tmpArr.append([param.get('name'), param.get('pos'), param.get('type'),visArr])
                    
            unitType[int(unit.get('id'))] = ([[unit.get('name')],tmpArr])                      
        
        def readPattern(addr, param, fid):
            fid.seek(addr)
            word = struct.unpack('B', fid.read(1))[0]
            
            retVal = "ERR"
            for pat in param[3]:
                if int(word) == int(pat[1]):
                    retVal = pat[0]
                            
            return retVal
                    
        def readLetter(addr, fid):
            tmp = readFullNumber1B(addr, fid)
            return chr(97+int(tmp)-10)

        def readFullNumber1B(address, fid):
            fid.seek(address)
            word = struct.unpack('B', fid.read(1))[0]
            return int(word)
            
        def readFullNumber2B(address, fid):
            fid.seek(address)
            word = struct.unpack('<H', fid.read(2))[0]
            return int(word)
            
        def readFullNumber(address, fid):
            fid.seek(address)
            word = struct.unpack('<I', fid.read(4))[0]
            return (float(word)/pow(2,16))

        def readData(address, fid):
            fid.seek(address)
            word = struct.unpack('<i', fid.read(4))[0]
            return (float(word)/10000)

        def writeData(number, address, fid):
            t= struct.pack('<I', number*10000*10)
            #print str(address) + " = " + t
            fid.seek(address)
            fid.write(t)

        def writeCommand(number, address, fid):
            t= struct.pack('<I', number)
            #print str(address) + " = " + t
            fid.seek(address)
            fid.write(t)

        fR = open(fileName, "rb")
        
        startUnit = int("fc", 16)
        prg = []
        self.unitAddr = []
        unitTypeId = -1
        i = 0
        while unitTypeId !=4: #4 is END Unit
            cmd = []
            unitAddr = startUnit + i * 100
            i = i + 1
            fR.seek(unitAddr)
            unitTypeId = struct.unpack('B', fR.read(1))[0]
            fR.seek(unitAddr+2)
            unitProgNumber = int(struct.unpack('B', fR.read(1))[0])
            #print "addr=%x, unitTypeId=%s, unitProgNumber=%s"%(unitAddr+2,unitTypeId,unitProgNumber)
            
            blockIsSubUnit = 0
            blockIsUnit = 1
            if unitType[unitTypeId][0][0] == "SNo" or unitType[unitTypeId][0][0] == "FIG":
                blockIsUnit = 0
                blockIsSubUnit = 1

            if (unitTypeId == 52 or unitTypeId == 51 or unitTypeId == 4 or unitTypeId == 170 or unitTypeId == 171 or unitTypeId == 172 or unitTypeId == 168 or unitTypeId == 53 or unitTypeId == 180 or unitTypeId == 173 or unitTypeId == 48 or unitTypeId == 1 or unitTypeId == 6 or unitTypeId == 54 or unitTypeId == 161 or unitTypeId == 180):
                                
                if blockIsUnit == 1:
                    cmd.append(["UNo",unitProgNumber,unitAddr+2,""])
                    cmd.append(["UNIT",unitType[unitTypeId][0][0],unitAddr,""])
                else:
                    cmd.append([unitType[unitTypeId][0][0],unitProgNumber,unitAddr+2,""])

                visibileParam = []
                ignoreNextParam = 0
                for param in unitType[unitTypeId][1]:
                    if param[2] == "NA":
                        dataParam = "*"
                    elif int(param[1]) == 0:
                        dataParam = "?"
                    elif param[2] == "wholeNumber":
                        dataParam = readFullNumber(unitAddr+int(param[1]), fR)
                    elif param[2] == "readData":
                        dataParam = readData(unitAddr+int(param[1]), fR)
                    elif param[2] == "text":
                        fR.seek(unitAddr+int(param[1]))
                        dataParam = struct.unpack("cccccccccccccccc", fR.read(16))
                    elif param[2] == "readFullNumber2B":
                        dataParam = readFullNumber2B(unitAddr+int(param[1]), fR)
                    elif param[2] == "readFullNumber1B":
                        dataParam = readFullNumber1B(unitAddr+int(param[1]), fR)
                    elif param[2] == "readLetter":
                        dataParam = readLetter(unitAddr+int(param[1]), fR)
                    elif param[2] == "readPattern":
                        dataParam = readPattern(unitAddr+int(param[1]), param, fR)
                        visibileParam = dataParam
                    else:
                        dataParam = "ERROR"
                                          
                    if param[2] != "readPattern":
                        if param[3] == []:
                            pass
                        elif visibileParam in param[3]:
                            pass
                        else:
                            dataParam = "*"
                                            
                    if ignoreNextParam == 1:
                        cmd.append([str(param[0]),"",unitAddr+int(param[1]),param[2]])
                        ignoreNextParam = 0
                    elif (unitTypeId==161 and dataParam=='W'):
                        cmd.append([str(param[0]),"",unitAddr+int(param[1]),param[2]])
                        ignoreNextParam = 1
                    else:
                        cmd.append([str(param[0]),dataParam,unitAddr+int(param[1]),param[2]])

                for k in range(len(cmd),17):
                    cmd.append(["", "", "", ""])
                cmd.append(["addr", unitAddr,unitAddr,""])
                prg.append(cmd)
                
                unitAddr
                
                print "Addr=0x%X, unitTypeId=%d, unitProgNumber=%d, unitName=%s"%(unitAddr,int(unitTypeId),unitProgNumber,unitType[unitTypeId][0])
            else:
                print "\n%d"%(int(unitTypeId)), "%x"%(unitProgNumber), unitType[unitTypeId][0]
                
        fR.close()

        return prg
       
 
    def printProgram(self):
    
        i = 0
        lastCmd = ""
        self.list_ctrl_info = []
        for cmd in self.mazakPrg:
            infoTitle = []
            infoData = []                
            if cmd[0][0] == "UNo":
                i=i+1
                self.list_ctrl.InsertStringItem(i,str(i))
                self.list_ctrl_info.append([])
 
            if cmd[0][0] == "UNo" or cmd[0][0]!=lastCmd:
                showTitle = 1
                i=i+1
                posTitle = self.list_ctrl.InsertStringItem(i,str(i))
                infoTitle.append([i,0,i,0,0])
                self.list_ctrl.SetItemTextColour(posTitle, wx.GREEN)
            else:
                showTitle = 0
            lastCmd = cmd[0][0]
                

            i=i+1
            posData = self.list_ctrl.InsertStringItem(i,str(i))
            infoData.append([i,0,i,0,0])
            self.list_ctrl.SetItemTextColour(posData, wx.YELLOW)
            
            colIdx = 1
            for param in cmd:
                if showTitle == 1:
                    self.list_ctrl.SetStringItem(posTitle,colIdx,str(param[0]))
                    infoTitle.append([i,colIdx,str(param[0]),param[2],param[3]])
                    
                self.list_ctrl.SetStringItem(posData,colIdx, str(param[1]))
                infoData.append([i,colIdx, str(param[1]),param[2],param[3]])
                colIdx = colIdx + 1
            
            if showTitle == 1:            
                self.list_ctrl_info.append(infoTitle)
            self.list_ctrl_info.append(infoData)

def get_bg_abs_filename():
    '''
    returns the absolute file name for the file default_background.bmp
    :raises: NameError when the file is not found
    '''
    occ_package = sys.modules['OCC']
    #bg_abs_filename = os.path.join(occ_package.__path__[0],'Display','default_background.bmp')
    bg_abs_filename = "eureka.bmp"
    if not os.path.isfile(bg_abs_filename):
        raise NameError('No image background file found.')
    else:
        return bg_abs_filename

            
def init_display(screenX=1024, screenY=768):
    """
    initializes the display
    
    :param screenX: screen resolution y axis
    :param screenY: screen resolution y axis
    :return: OCCViewer.Viewer3d instance
    """
    global display, add_menu, add_function_to_menu, start_display, app, win

    from OCC.Display.wxDisplay import wxViewer3d
    
    class AppFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, "pythonOCC-%s 3d viewer ('wx' backend)"%VERSION, style=wx.DEFAULT_FRAME_STYLE,size = (640,480))

            panel1 = wx.Panel(self, -1,pos=(1000,0),size=(600,700))
            self.canva = wxViewer3d(panel1)
            self.canva.SetSizeWH(600,600)
            self.menuBar = wx.MenuBar()
            self._menus = {}
            self._menu_methods = {}                
            
            panel2 = Page(wx.Panel(self, -1,pos=(0,0),size=(1000,530)))
            panel2.SetSizeWH(1000,530)
            
            wx.Button(panel1, 1, "ISO", pos=(10, 620), size=(50,25))
            self.Bind(wx.EVT_BUTTON, self.viewPoint)
            wx.Button(panel1, 2, "Front", pos=(10+50, 620), size=(50,25))
            self.Bind(wx.EVT_BUTTON, self.viewPoint)
            wx.Button(panel1, 3, "Side", pos=(10+100, 620), size=(50,25))
            self.Bind(wx.EVT_BUTTON, self.viewPoint)
            wx.Button(panel1, 4, "Up", pos=(10+150, 620), size=(50,25))
            self.Bind(wx.EVT_BUTTON, self.viewPoint)

        def viewPoint(self, evt):
            id = evt.GetId()
            print id
            
            if id==1:
                display.View_Iso()
            if id==2:
                display.View.SetProj(OCC.V3d.V3d_Xpos)
            if id==3:
                display.View.SetProj(OCC.V3d.V3d_Yneg)
            if id==4:
                display.View.SetProj(OCC.V3d.V3d_Zpos)

            
        def add_menu(self, menu_name):
            _menu = wx.Menu()
            self.menuBar.Append(_menu, "&"+menu_name)
            self.SetMenuBar(self.menuBar)
            self._menus[menu_name]=_menu

        def add_function_to_menu(self, menu_name, _callable):
            # point on curve
            _id = wx.NewId()
            assert callable(_callable), 'the function supplied is not callable'
            try:
                self._menus[menu_name].Append(_id, _callable.__name__.replace('_', ' ').lower())
            except KeyError:
                raise ValueError('the menu item %s does not exist' % (menu_name))
            self.Bind(wx.EVT_MENU, _callable, id=_id)
            
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    win = AppFrame(None)
    win.Show(True)
    wx.SafeYield()
    win.canva.InitDriver()
    app.SetTopWindow(win)
    #http://api.pythonocc.org/OCC.Display.OCCViewer.html
    display = win.canva._display
    display.SetBackgroundImage("eureka.bmp")
    #display.View_Iso()
    #display.View.SetProj(OCC.V3d.V3d_XposYnegZneg)
    #display.View.Rotation(-100,0)

    def add_menu(*args, **kwargs):
        win.add_menu(*args, **kwargs)
    def add_function_to_menu(*args, **kwargs):
        win.add_function_to_menu(*args, **kwargs)
    def start_display():
        app.MainLoop()
        
    #pos1 = gp_Ax2(gp_Pnt(gp_XYZ(0,0,0)), gp_Dir(1,0,0))
    #my_box1 = display.DisplayShape(BRepPrimAPI_MakeCylinder(pos1, 20., 50.).Shape())        
            
    return display, start_display, add_menu, add_function_to_menu
    
if __name__ == '__main__':
    init_display()


    def sphere(event=None):
        pos1 = gp_Ax2(gp_Pnt(gp_XYZ(0,0,0)), gp_Dir(1,0,0))
        my_box1 = display.DisplayShape(BRepPrimAPI_MakeCylinder(pos1, 20., 50.).Shape())
    def cube(event=None):
        pos3 = gp_Ax2(gp_Pnt(gp_XYZ(-100,0,0)), gp_Dir(1,0,0))
        display.DisplayShape(BRepPrimAPI_MakeCone(pos3, 40, 30, 50,).Shape())        
    def exit(event=None):
        sys.exit()    
    add_menu('primitives')
    add_function_to_menu('primitives',  sphere)
    add_function_to_menu('primitives',  cube)
    add_function_to_menu('primitives',  exit)
    start_display()