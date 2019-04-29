#!/usr/bin/env python3

# Clutter seems like a good choice, which took me a while to figure out.
# However, it is short on human documentation. I've had trouble
# with the bindings, and trouble with how layouts and text work.
# So I havn't got far.

# https://developer.gnome.org/clutter/stable/
# https://developer.gnome.org/clutter/stable/clutterobjecthierarchy.html
# https://github.com/GNOME/clutter/tree/master/examples
import subprocess
from time import sleep
import gi

gi.require_version('Gtk', '3.0')
#gi.require_version('Clutter', '1.0')
# used 1.8
gi.require_version('GtkClutter', '1.0')

#from gi.repository import Gio, GLib

from gi.repository import GtkClutter
GtkClutter.init([])
from gi.repository import Clutter, GObject, Gtk, Pango

# https://wiki.gnome.org/action/show/Projects/PyGObject/IntrospectionPorting?action=show&redirect=PyGObject%2FIntrospectionPorting
# https://developer.gnome.org/clutter/stable/

def label(stage, x, y, width, text):
    r = Clutter.Rectangle()
    r.set_color(Clutter.Color.new(0,255,255,255))
    r.set_size(width, 32)
    r.set_position(x, y)
    r.set_reactive(True)    
    stage.add_actor(r)
    t = Clutter.Text()
    t.set_text(text)
    #t.set_markup('<span foreground="blue" background="red">' + text + '</span>')
    t.set_max_length(width - 8)
    t.set_position(x + 8, y + 6) 
    #t.set_ellipsize = Pango.PangoEllipsizeMode.PANGO_ELLIPSIZE_END   
    t.set_ellipsize(Pango.EllipsizeMode.END)   
    t.set_reactive(True)    
    stage.add_actor(t)

def label2(stage, x, y, width, text):
    bl = Clutter.BinLayout.new(
        Clutter.BinAlignment.CENTER,
        Clutter.BinAlignment.CENTER
    )
    # Aint happening?
    #b.set_position(x, y)
    #stage.add_actor(b)
    
    #container = Clutter.Actor.new()
    #container.set_layout_manager(bl)
    r = Clutter.Rectangle()
    r.set_layout_manager(bl)
    r.set_color(Clutter.Color.new(180,100,0,255))
    r.set_size(width, 32)
    r.set_reactive(True)    
    #stage.add_child(r)

    #bl.add_child(r)
    #label(p, x, y, width, headText)
    #inStage = r.get_stage()
    t = Clutter.Text()
    t.set_text(text)
    t.set_x_expand(True)
    t.set_x_align (Clutter.ActorAlign.CENTER)
    t.set_y_expand(True)
    t.set_y_align (Clutter.ActorAlign.CENTER)
    t.set_background_color(Clutter.Color.new(255,255,200,255))
    t.set_position(0, 0)
    #t.set_markup('<span foreground="blue" background="red">' + text + '</span>')
    #t.set_max_length(width - 8)
    #t.set_ellipsize = Pango.PangoEllipsizeMode.PANGO_ELLIPSIZE_END   
    #t.set_ellipsize = Pango.PangoEllipsizeMode.PANGO_ELLIPSIZE_END      
    #s = r.get_stage()
    #r.add_child(t)
    #r.insert_child_above(t)
    #r.add_child(t)
    #t.margin_top = 5
    #t.margin_left = 15
    stage.add_child(t)

def panel(stage, x, y, width, headText):
    r = Clutter.Rectangle()
    r.set_color(Clutter.Color.new(0,255,255,180))
    r.set_size(width, 200)
    r.set_position(x, y)
    #r.set_reactive(True)
    stage.add_actor(r)
    return r
            
def dropdownPanel(stage, x, y, width, headText):
    #p = panel(stage, x, y, width, headText)
    #label(p, x, y, width, headText)
    #label(stage, x, y, width, headText)
    label2(stage, x, y, width, headText)
    
def vbin(stage, x, y):
    b = Clutter.BinLayout.new(Clutter.BinAlignment.CENTER, Clutter.BinAlignment.START)
    #set_alignment (CLUTTER_BIN_ALIGNMENT_START)
    stage.add_actor(b)
    #b.add_child(label(stage, x, y, width, headText))
    
class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="GUI")
        e = GtkClutter.Embed.new()
        e.set_size_request(500, 500)
        self.add(e)
        stage = e.get_stage()
        stage.set_color(Clutter.Color.new(0,0,255,0))
        stage.set_size(500, 500)
        stage.add_actor(self.rectangle(0, 100))
        dropdownPanel(stage, 50, 0, 200, "dropdown")
        #panel(stage, 50, 0, 300)
        #vbin(stage, 100, 0)
        #label2(stage, 100, 100, 100, "label2")
        
    def rectangle(self, x, y):
        r = Clutter.Rectangle()
        r.set_color(Clutter.Color.new(0,0,255,255))
        r.set_size(200, 40)
        r.set_position(x, y)
        r.set_reactive(True)
        t = Clutter.Text()
        t.set_text('wow')
        t.set_position(x, y)        
        return t

def end(widget, event):
    #widget.saveSettings()
    Gtk.main_quit()

win = MyWindow()
win.connect("delete-event", end)
win.show_all()

Gtk.main()
