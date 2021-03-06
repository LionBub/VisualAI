# 6/3/2022 Project day 4

import tkinter as tk
from tkinter import ttk
import Placeables
import Constants as Const

rclickCanvasPos = (0, 0)  # global variables like this are discouraged. Make it into a class and save as instance?
lastLeftClickCanvasPos = (0, 0)
inspectorFocus = None
objectsArr = []


def pan_start(event):
    canvas.scan_mark(event.x, event.y)


def pan_move(event):
    canvas.scan_dragto(event.x, event.y, gain=1)


def do_popupMenu(event):
    global rclickCanvasPos
    rclickCanvasPos = (canvas.canvasx(event.x), canvas.canvasy(event.y))
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()


def createGridLines(sizeX, sizeY, gridSpacing):
    for x in range(int(sizeX / gridSpacing)):  # vertical lines
        canvas.create_line(x * gridSpacing, 0, x * gridSpacing, sizeY, width=1, fill=Const.COL_C)
    for y in range(int(sizeY / gridSpacing)):  # vertical lines
        canvas.create_line(0, y * gridSpacing, sizeX, y * gridSpacing, width=1, fill=Const.COL_C)


def createCircle(canv, x, y, r, **kwargs):
    return canv.create_oval(x + r, y + r, x - r, y - r, kwargs)


def addPlaceableToList(placeable):
    objListBox.insert('end', placeable.name)
    if len(objectsArr) % 2 == 1:
        objListBox.itemconfig(objListBox.size() - 1, bg=Const.COL_Bl)


def drawLayerBlockShape(box: Placeables.LayerBlock):  # draws and populates drawing list of inputted LayerBlock object
    box.drawing = [canvas.create_rectangle(box.bound.x0, box.bound.y0, box.bound.x1, box.bound.y1,  # draw box
                                           fill=box.color, outline=box.outlineCol, width=2,
                                           tags=('inspectable', 'draggable'))]
    #  LayerBlock.size setter limits bounding box
    if box.size <= Const.MAX_LAYER_DRAW_LENGTH:
        for n in range(box.size):  # draw nodes
            box.drawing.append(createCircle(canvas, box.nodes[n].x, box.nodes[n].y, Const.NODE_RADIUS,
                                            fill=box.ncolor, width=0, tags=('inspectable', 'linkable')))
    else:
        for n in range(Const.MAX_LAYER_DRAW_LENGTH - 2):
            box.drawing.append(createCircle(canvas, box.nodes[n].x, box.nodes[n].y, Const.NODE_RADIUS,
                                            fill=box.ncolor, width=0, tags=('inspectable', 'linkable')))
        box.drawing.append(canvas.create_text(box.nodes[Const.MAX_LAYER_DRAW_LENGTH - 2].x,
                                              box.nodes[Const.MAX_LAYER_DRAW_LENGTH - 2].y,
                                              text=str(box.size - Const.MAX_LAYER_DRAW_LENGTH + 1), fill='white'))
        box.drawing.append(createCircle(canvas, box.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].x,
                                        box.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].y, Const.NODE_RADIUS,
                                        fill=box.ncolor, width=0, tags=('inspectable', 'linkable')))


def addLayerBlock():
    global objectsArr
    global rclickCanvasPos
    box = Placeables.LayerBlock(rclickCanvasPos[0], rclickCanvasPos[1], 6)
    drawLayerBlockShape(box)
    objectsArr.append(box)
    addPlaceableToList(box)


def selectPlaceable(event):
    # on B1 down # doesn't consistenty register when clicking. Bug might be somewhere else. Boundbox
    # doesnt drag properly?
    global lastLeftClickCanvasPos
    lastLeftClickCanvasPos = (canvas.canvasx(event.x), canvas.canvasy(event.y))


def dragPlaceable(event):  # on B1 motion
    global lastLeftClickCanvasPos
    if not isinstance(inspectorFocus, Placeables.Placeable):
        return
    if isinstance(inspectorFocus.drawing, list):
        for e in inspectorFocus.drawing:
            canvas.move(e, canvas.canvasx(event.x) - lastLeftClickCanvasPos[0],
                        canvas.canvasy(event.y) - lastLeftClickCanvasPos[1])
    else:
        canvas.move(inspectorFocus.drawing, canvas.canvasx(event.x) - lastLeftClickCanvasPos[0],
                    canvas.canvasy(event.y) - lastLeftClickCanvasPos[1])
    inspectorFocus.x = inspectorFocus.x + canvas.canvasx(event.x) - lastLeftClickCanvasPos[0]
    inspectorFocus.y = inspectorFocus.y + canvas.canvasy(event.y) - lastLeftClickCanvasPos[1]
    lastLeftClickCanvasPos = (canvas.canvasx(event.x), canvas.canvasy(event.y))
    refreshCanvas()


def forgetPlaceable(event):  # on B1 up  # May be unnecessary
    refreshInspector()
    refreshCanvas()


def setInspectorFocus(event):
    global inspectorFocus
    if inspectorFocus is not None:  # last inspectorFocus
        canvas.itemconfig(inspectorFocus.drawing[0], outline='white')
    for p in reversed(objectsArr):  # last to first in list
        if isinstance(p, Placeables.LayerBlock) and p.bound.w <= canvas.canvasx(event.x) <= p.bound.e \
                and p.bound.n <= canvas.canvasy(event.y) <= p.bound.s:
            inspectorFocus = p
            canvas.itemconfig(inspectorFocus.drawing[0], outline=Const.COL_HI)
            break
    refreshInspector()


def refreshInspector():
    if len(inspector.winfo_children()) > 1:
        print('multiple windows in inspector')
    inspector.winfo_children()[0].destroy()  # destroys last inspBox

    inspBox = tk.Frame(inspector, bg=Const.COL_A)
    inspBox.place(width=inspector.winfo_width() - 20, x=10, relheight=1)  # width pads text on sides
    if isinstance(inspectorFocus, Placeables.LayerBlock):  # display modifiable variables
        # Name
        tname = tk.StringVar(value=inspectorFocus.name)

        def setName(*args):
            if not isinstance(inspectorFocus, Placeables.LayerBlock):
                return
            inspectorFocus.name = tname.get()

        tname.trace('w', setName)
        lnfr = tk.Frame(inspBox, bg=Const.COL_A, bd=0, relief='sunken')
        lnfr.pack(fill='x')
        lab = tk.Label(lnfr, bg=Const.COL_A, bd=0, fg='white', text='Name :  ', padx=0, pady=5)
        lab.pack(side='left')
        entry = tk.Entry(lnfr, bg=Const.COL_Bl, bd=1, highlightthickness=0, fg='white', textvariable=tname)
        entry.pack(expand=True, side='left', fill='x')

        # Size
        tsize = tk.IntVar(value=inspectorFocus.size)

        def setSize(*args):
            if not isinstance(inspectorFocus, Placeables.LayerBlock):
                return
            try:
                tsize.get()
            except tk.TclError:
                return
            destroyConnectionDrawings(inspectorFocus)
            inspectorFocus.size = tsize.get()
            redrawObj(inspectorFocus)
            if inspectorFocus.pushesTo is not None:
                drawNodeConnections(inspectorFocus)  # push connections
            if inspectorFocus.pullsFrom is not None:
                drawNodeConnections(inspectorFocus.pullsFrom)  # pull connections

        tsize.trace('w', setSize)
        lnfr = tk.Frame(inspBox, bg=Const.COL_A, bd=0, relief='sunken')
        lnfr.pack(fill='x')
        lab = tk.Label(lnfr, bg=Const.COL_A, bd=0, fg='white', text='Size :  ', padx=0, pady=5)
        lab.pack(side='left')
        entry = tk.Entry(lnfr, bg=Const.COL_Bl, bd=1, highlightthickness=0, fg='white', textvariable=tsize)
        entry.pack(expand=True, side='left', fill='x')

        # Node Color
        tncol = tk.StringVar(value=inspectorFocus.ncolor)

        def setNCol(*args):
            if not isinstance(inspectorFocus, Placeables.LayerBlock):
                return
            inspectorFocus.ncolor = tncol.get()
            redrawObj(inspectorFocus)

        tncol.trace('w', setNCol)
        lnfr = tk.Frame(inspBox, bg=Const.COL_A, bd=0, relief='sunken')
        lnfr.pack(fill='x')
        lab = tk.Label(lnfr, bg=Const.COL_A, bd=0, fg='white', text='Node Color :  ', padx=0, pady=5)
        lab.pack(side='left')
        entry = tk.Entry(lnfr, bg=Const.COL_Bl, bd=1, highlightthickness=0, fg='white', textvariable=tncol)
        entry.pack(expand=True, side='left', fill='x')

    lnfr = tk.Frame(inspBox, bg=Const.COL_A, bd=0, relief='sunken')
    lnfr.pack(fill='x')
    tk.Label(lnfr, bg=Const.COL_A, bd=0, fg='white', padx=0, pady=5).pack(side='left')
    ttk.Separator(lnfr, orient='horizontal').pack(fill='x')

    for attr, value in inspectorFocus.__dict__.items():  # display read only variables
        lnfr = tk.Frame(inspBox, bg=Const.COL_A, bd=0, relief='sunken')
        lnfr.pack(fill='x')
        lab = tk.Label(lnfr, bg=Const.COL_A, bd=0, fg='white', text=f'{attr} :  ', padx=0, pady=5)
        lab.pack(side='left')
        entry = tk.Entry(lnfr, bg=Const.COL_Bl, bd=1, highlightthickness=0, fg='white')
        entry.pack(expand=True, side='left', fill='x')
        if value is not None:
            entry.insert('end', value)
        entry.configure(state='disabled', disabledbackground=Const.COL_A, disabledforeground='white')


def setLinkEnd(event):
    if not isinstance(inspectorFocus, Placeables.LayerBlock):
        print(f'inspector focus should be type Placeables.LayerBlock, instead it is {type(inspectorFocus)}')
        return
    for end in reversed(objectsArr):  # last to first in list
        if end != inspectorFocus:
            if end.bound.w <= canvas.canvasx(event.x) <= end.bound.e \
                    and end.bound.n <= canvas.canvasy(event.y) <= end.bound.s:
                inspectorFocus.pushesTo = end
                end.pullsFrom = inspectorFocus
                refreshInspector()
                drawNodeConnections(inspectorFocus)
                break


def drawNodeConnections(pusher: Placeables.LayerBlock):
    # draws pushing connections only
    # makes push connections and stores ids in list per node  # color based on inspObj.weights[s][e]
    # pusher is layer
    def distributeThisNodeToShortened(fnode):  # upper portion only
        for tn in range(Const.MAX_LAYER_DRAW_LENGTH - 2):
            tn = pusher.pushesTo.nodes[tn]
            fnode.pushConnections.append(canvas.create_line(fnode.x, fnode.y, tn.x, tn.y, fill='cyan', arrow='last',
                                                            tags='nodeConnection'))
        fnode.pushConnections.append(
            canvas.create_line(fnode.x, fnode.y,
                               pusher.pushesTo.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].x,
                               pusher.pushesTo.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].y,
                               fill='cyan', arrow='last', tags='nodeConnection'))

    def distributeThisNode(fnode):
        for tn in pusher.pushesTo.nodes:
            fnode.pushConnections.append(canvas.create_line(fnode.x, fnode.y, tn.x, tn.y, fill='cyan', arrow='last',
                                                            tags='nodeConnection'))

    if pusher.size > Const.MAX_LAYER_DRAW_LENGTH and pusher.pushesTo.size > Const.MAX_LAYER_DRAW_LENGTH:  # both short
        for s in range(Const.MAX_LAYER_DRAW_LENGTH - 2):
            s = pusher.nodes[s]
            s.pushConnections = []
            distributeThisNodeToShortened(s)
        pusher.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].pushCoonnections = []
        distributeThisNodeToShortened(pusher.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1])
    elif pusher.size > Const.MAX_LAYER_DRAW_LENGTH:  # Pusher is shortened
        for s in range(Const.MAX_LAYER_DRAW_LENGTH - 2):
            s = pusher.nodes[s]
            s.pushConnections = []
            distributeThisNode(s)
        pusher.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].pushCoonnections = []
        distributeThisNode(pusher.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1])
    elif pusher.pushesTo.size > Const.MAX_LAYER_DRAW_LENGTH:  # Puller is shortened
        for s in pusher.nodes:
            s.pushConnections = []
            distributeThisNodeToShortened(s)
    else:  # neither are shortened
        for s in pusher.nodes:
            s.pushConnections = []
            distributeThisNode(s)


def redrawObj(obj: Placeables.LayerBlock):
    for s in obj.drawing:
        canvas.delete(s)
    drawLayerBlockShape(obj)


def destroyConnectionDrawings(lar: Placeables.LayerBlock):  # deletes all push and pull connections
    if lar.pullsFrom is not None:
        for fn in lar.pullsFrom.nodes:
            for fc in fn.pushConnections:
                canvas.delete(fc)
    for tn in lar.nodes:
        for tc in tn.pushConnections:
            canvas.delete(tc)


def refreshCanvas():
    #  move objects as opposed to redraw.
    for b in objectsArr:
        if b.pushesTo is not None:
            if b.size > Const.MAX_LAYER_DRAW_LENGTH and b.pushesTo.size > Const.MAX_LAYER_DRAW_LENGTH:  # both shortened
                for s in range(Const.MAX_LAYER_DRAW_LENGTH - 2):  # moves pushing connections to top guys
                    s = b.nodes[s]
                    for index in range(Const.MAX_LAYER_DRAW_LENGTH - 2):
                        e = b.pushesTo.nodes[index]
                        canvas.coords(s.pushConnections[index], s.x, s.y, e.x, e.y)
                    canvas.coords(s.pushConnections[Const.MAX_LAYER_DRAW_LENGTH - 2], s.x, s.y,
                                  b.pushesTo.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].x,
                                  b.pushesTo.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].y)
                for index in range(Const.MAX_LAYER_DRAW_LENGTH - 2):
                    e = b.pushesTo.nodes[index]
                    canvas.coords(b.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].pushConnections[index],
                                  b.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].x,
                                  b.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].y, e.x, e.y)
                canvas.coords(b.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].pushConnections[Const.MAX_LAYER_DRAW_LENGTH - 2],
                              b.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].x, b.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].y,
                              b.pushesTo.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].x,
                              b.pushesTo.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].y)

            elif b.size > Const.MAX_LAYER_DRAW_LENGTH:  # if  pusher is shortened
                for s in range(Const.MAX_LAYER_DRAW_LENGTH - 2):  # moves pushing connections to top guys
                    s = b.nodes[s]
                    for index, e in enumerate(b.pushesTo.nodes):
                        canvas.coords(s.pushConnections[index], s.x, s.y, e.x, e.y)
                for index, e in enumerate(b.pushesTo.nodes):  # moves pushing connections to bottom guy
                    canvas.coords(b.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].pushConnections[index],
                                  b.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].x,
                                  b.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].y, e.x, e.y)

            elif b.pushesTo.size > Const.MAX_LAYER_DRAW_LENGTH:  # if puller is shortened
                for s in b.nodes:
                    for index in range(Const.MAX_LAYER_DRAW_LENGTH - 2):
                        e = b.pushesTo.nodes[index]
                        canvas.coords(s.pushConnections[index], s.x, s.y, e.x, e.y)
                    canvas.coords(s.pushConnections[Const.MAX_LAYER_DRAW_LENGTH - 2], s.x, s.y,
                                  b.pushesTo.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].x,
                                  b.pushesTo.nodes[Const.MAX_LAYER_DRAW_LENGTH - 1].y)

            else:  # neither is shortened
                for s in b.nodes:
                    for index, e in enumerate(b.pushesTo.nodes):
                        canvas.coords(s.pushConnections[index], s.x, s.y, e.x, e.y)


# ==========
if __name__ == '__main__':
    root = tk.Tk()
    root.title('Visual AI')
    root.geometry(f"{Const.WIDTH}x{Const.HEIGHT}")
    root.update_idletasks()  # strangely necessary to use winfox

    toolbar = tk.Frame(root, bg=Const.COL_A)
    toolbar.place(relwidth=1, relheight=0.1)

    # panels
    panelA = tk.PanedWindow(root, bd=1, relief='raised', bg=Const.COL_A, sashwidth=2,
                            sashrelief='raised', sashpad=2)
    panelA.place(relheight=0.9, relwidth=1, rely=0.1)
    # inspector = tk.Frame(panelA, bg=Const.COL_A)
    # panelA.add(inspector, width=root.winfo_width() / 3)
    panelB = tk.PanedWindow(panelA, orient='vertical', bd=0, relief='sunken', bg=Const.COL_A, sashwidth=2,
                            sashrelief='raised', sashpad=2)
    panelA.add(panelB, width=root.winfo_width() * 2 / 3)
    canvas = tk.Canvas(panelB, bg=Const.COL_B, highlightthickness=0)
    panelB.add(canvas, height=Const.HEIGHT * 7 / 10)
    shelf = tk.Frame(panelB, bg=Const.COL_A)
    panelB.add(shelf)
    panelC = tk.PanedWindow(panelA, orient='vertical', bd=0, relief='sunken', bg=Const.COL_A, sashwidth=2,
                            sashrelief='raised', sashpad=2)
    panelA.add(panelC)
    hierarchy = tk.Frame(panelA, bg=Const.COL_A)
    panelC.add(hierarchy, height=root.winfo_height() / 3)
    inspector = tk.Frame(panelA, bg=Const.COL_A)
    panelC.add(inspector)

    # ---CANVAS----------------------------------------------------------
    # pan and scroll
    scrollbarX = tk.Scrollbar(canvas, orient='horizontal', command=canvas.xview)
    scrollbarY = tk.Scrollbar(canvas, orient='vertical', command=canvas.yview)
    # scrollbarX.pack(side="bottom", fill="x")
    # scrollbarY.pack(side='right', fill='y')
    canvas.configure(scrollregion=(0, 0, 2000, 1500), xscrollcommand=scrollbarX.set, yscrollcommand=scrollbarY.set)
    canvas.yview_moveto(0.5)
    canvas.xview_moveto(0.5)

    canvas.bind('<Shift-ButtonPress-1>', pan_start)
    canvas.bind('<Shift-B1-Motion>', pan_move)
    # right click menu
    m = tk.Menu(root, tearoff=0, bg=Const.COL_A, fg='white', activebackground=Const.COL_HI)
    addmenu = tk.Menu(root, tearoff=0, bg=Const.COL_A, fg='white', activebackground=Const.COL_HI)
    m.add_cascade(label='Add', menu=addmenu)
    m.add_separator()
    m.add_command(label="Cut")
    m.add_command(label="Copy")
    m.add_command(label="Paste")
    m.add_command(label="Reload")

    addmenu.add_command(label='Layer', command=addLayerBlock)

    canvas.bind("<Button-2>", do_popupMenu)  # Right click is B2 on mac but b3 everywhere else
    canvas.tag_bind('draggable', '<Button-1>', selectPlaceable)
    canvas.tag_bind('draggable', '<B1-Motion>', dragPlaceable)
    canvas.tag_bind('draggable', '<ButtonRelease-1>', forgetPlaceable)
    canvas.tag_bind('inspectable', '<Button-1>', setInspectorFocus)
    canvas.tag_bind('linkable', '<ButtonRelease-1>', setLinkEnd)

    createGridLines(2000, 1500, 50)
    # grid

    # ---HIERARCHY-----------------------------------------------------
    objListBox = tk.Listbox(hierarchy, bg=Const.COL_A, fg='white', relief='sunken', highlightthickness=0)
    olb_scrollbar = tk.Scrollbar(objListBox, width=10, command=objListBox.yview)
    # olb_scrollbar.pack(side='right', fill='y')
    objListBox.configure(yscrollcommand=olb_scrollbar.set)
    objListBox.place(anchor='n', y=30, relx=0.5, relwidth=0.75, relheight=0.8, )
    tk.Label(hierarchy, text='Objects List', fg='white', bg=Const.COL_A).place(anchor='n', y=9, relx=0.25)
    # ---INSPECTOR-------------------------------------------------------

    # label
    toolbar_label = tk.Label(toolbar, text="Toolbar", bg='red')
    toolbar_label.pack()
    inspector_label = tk.Label(inspector, text="Inspector", bg='yellow')
    inspector_label.pack()
    canvas_label = tk.Label(canvas, text="Canvas", bg='green')
    canvas_label.pack()
    shelf_label = tk.Label(shelf, text="Shelf", bg='orange')
    shelf_label.pack()

    root.mainloop()
