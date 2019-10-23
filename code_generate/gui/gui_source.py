#!/usr/bin/env python3


import subprocess

from time import sleep
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')


from gi.repository import GObject, Gtk, Pango, GtkSource

## Short poke at GTK, sourceView widget, Glade generated GUI
# Not convincing as no visuals easily embeddable. A do-what-you-can
#not what-you-want affair.

# Building from Glade may seem cool, but Glade/Gtk is erratic with late 
# entries to the build code. Which gives us a problem for 
# GtkSourceView. We are getting by. I will not write custom XML for it.

# Basic python-bound Glade example
# https://python-gtk-3-tutorial.readthedocs.io/en/latest/builder.html

class Handler():
    def __init__(self, buff):
        self.buff = buff

    def warning(self, txt):
        print(txt)
        
    def getWordIter(self, it):
        bIt = it.copy()
        while((not bIt.starts_word()) and bIt.backward_char()):
            pass
        while((not it.ends_word()) and it.forward_char()):
            pass            
        return(bIt, it)
        
    def onInfoClicked(self, widget):
        #print('ow')
        off = self.buff.get_property("cursor-position")
        cursorIt = self.buff.get_iter_at_offset(off)
        bIt, fIt = self.getWordIter(cursorIt)
        text = self.buff.get_text(bIt, fIt, False)
        if (not text):
            self.warning('no word under cursor?')
        else:
            print('target: ' + text)
            print('do with word...' + text)
                                   
    def onTopwinDestroy(widget, event):
        #widget.saveSettings()
        Gtk.main_quit()               

    

def addSourceView(container):
    lm = GtkSource.LanguageManager()
    lids = lm.get_language_ids()
    #print(str(lids))
    targetLid = 'python'
    l = lm.get_language(targetLid)
    b = GtkSource.Buffer.new_with_language(l)
    #b.connect("source-mark-updated", onMarkChange)
    w = GtkSource.View.new_with_buffer(b)
    w.set_show_line_numbers(True)
    w.set_size_request(500, 500)
    #print('packed!!!')
    container.pack_start(w, True, True, 0)   
    return b 


b = Gtk.Builder.new()
b.add_from_file("gui.glade")
win = b.get_object("TopWin")
vBox = b.get_object("vBox")
buff = addSourceView(vBox)

b.connect_signals(Handler(buff))

win.show_all()
Gtk.main()
