'''
Created on Dec 21, 2012

@author: itpp
'''

import datetime

import numpy as np

import matplotlib.pyplot as plt

#import iris
#import iris.plot as iplt
#import iris.quickplot as qplt
import cartopy.crs as ccrs
from mpl_toolkits.axisartist.clip_path import clip

def dbg(name):
    print name,' = ',eval(name)

_proj_cyl = ccrs.PlateCarree()


def _gridline_values(start=None, stop=None, n=None, step=None):
    # Possible usages ...
    # [start=0], plus one of ...
    # n, [step=1]
    # stop, [step=1]
    # stop, n
    if start is None:
        start = 0.0
    if stop is not None:
        if n is not None:
            if step is not None:
                raise ValueError("cannot specify all of 'stop', 'n', and 'step'.")
            return np.linspace(start, stop, n)
        else:
            if step is None:
                return np.arange(start, stop)
    else:
        if n is None:
            raise ValueError("in absence of 'stop', must specify 'n'.")
        if step is None:
            step = 1.0
        stop = start + n*step
        return np.arange (start, stop, step)

def draw_gridlines(n_meridians=12, n_parallels=8, lon_color='#180000', lat_color='#000018', lon_offset=0.0):
    line_artists = []
    for longitude in np.linspace(-180.0, +180.0, n_meridians, endpoint=False):
        line_artists += [
            plt.plot([longitude, longitude], [-90.0, 90.0],
                     color=lon_color, transform=_proj_cyl)]
    for latitude in np.linspace(-90.0, +90.0, n_parallels, endpoint=False):
        line_artists += [
            plt.plot([-180.0, -90.0], [latitude, latitude],
                     color=lat_color, transform=_proj_cyl)]
        line_artists += [
            plt.plot([-90.0, 0.0], [latitude, latitude],
                     color=lat_color, transform=_proj_cyl)]
        line_artists += [
            plt.plot([0.0, 90.0], [latitude, latitude],
                     color=lat_color, transform=_proj_cyl)]
        line_artists += [
            plt.plot([90.0, 180.0], [latitude, latitude],
                     color=lat_color, transform=_proj_cyl)]
    return line_artists

#def draw_gridlines(
#        lons_n=12, lats_n=8,
#        lons_start=0.0, lats_start=0.0,
#        lons_lims=[-180.0, 180.0], lats_lims=[-90.0, 90.0],
#        lon_color='#180000', lat_color='#000018'
#    ):
#    line_artists = []
#    for longitude in np.linspace(*[x+lons_startlons_lims, lons_n, endpoint=False):
#        line_artists += [
#            plt.plot([longitude, longitude], [-90.0, 90.0],
#                     color=lon_color, transform=_proj_cyl)]
#    for latitude in np.linspace(*lats_lims, -90.0, +90.0, lats_n, endpoint=False):
#        line_artists += [
#            plt.plot([-180.0, 180.0], [latitude, latitude],
#                     color=lat_color, transform=_proj_cyl)]
#    return line_artists

class xOrtho(ccrs.Orthographic):
    """ Orthographic projection with enhanced line precision. """
#    def __init__(self, zoom=1.0, *args, **kwargs):
#        super(xOrtho, self).__init__(*args, **kwargs)
#        self._zoom = zoom

    @property
    def threshold(self):
        return 1e3

#    @property
#    def x_limits(self):
#        z = self._max / self._zoom
#        return (-z, z)
#
#    @property
#    def y_limits(self):
#        z = self._max / self._zoom
#        return (-z, z)
#
#    def set_zoom(self, z):
#        self._zoom = z

_r_globe = xOrtho()._max
_d_globe = 2.0 * _r_globe

_mouse_is_down = False
_min_update_secs = 0.5
_last_update_time = datetime.datetime.now()

_globe_xpos = 35.0
_globe_ypos = 17.5
_globe_start_pos = (_globe_xpos, _globe_ypos)
_globe_zoom = 1.0

_show_details = True
figure = None
def redraw_globe():
    if figure is not None:
        plt.clf()
        ax=plt.axes(projection=xOrtho(central_longitude=_globe_xpos, central_latitude=_globe_ypos));
        ax.set_autoscale_on(False)
        r = _r_globe / _globe_zoom
        ax.set_xlim(-r,r)
        ax.set_ylim(-r,r)
        if _show_details:
            ax.stock_img()
        ax.coastlines()
        t=draw_gridlines(8,4);
        plt.draw(); plt.show(block=False)

def globe_drag_start():
    global _show_details
    print '[simplify]'
    _show_details = False
    redraw_globe()

def clip_to_lims(x, lims):
    range = lims[1]-lims[0]
    x = x - lims[0] + 2*range
    x = x - range*int(x/range)
    return x + lims[0]

def globe_drag_fromto(start_pos, stop_pos):
    global _globe_start_pos, _globe_xpos, _globe_ypos
    print '[simplify]'
    deltas = [(stop_pos[i]-start_pos[i])/_d_globe for i in range(2)]
    _globe_xpos = clip_to_lims(_globe_start_pos[0] - deltas[0]*180.0, [-180.0, 180.0])
    _globe_ypos = clip_to_lims(_globe_start_pos[1] - deltas[1]*180.0, [-90.0, 90.0])
    redraw_globe()

def globe_drag_stop():
    global _show_details
    print '[full-draw]'
    _show_details = True
    redraw_globe()

def _mouse_udm(ev):
    global _mouse_is_down, _start_pos, _stop_pos, _r_globe, _last_update_time
#    print 'mouse event : ',ev.name,', button=',ev.button
    if ev.name == 'button_press_event':
        if not _mouse_is_down and ev.inaxes:
            print 'START  in ',ev.inaxes,'  --> ',
            print '@({},{})'.format(ev.xdata,ev.ydata)
            print
            _mouse_is_down = True
            _globe_start_pos = (_globe_xpos, _globe_ypos)
            _start_pos = (ev.xdata, ev.ydata)
            globe_drag_start()

    elif ev.name == 'motion_notify_event':
        if _mouse_is_down and ev.inaxes:
            _stop_pos = (ev.xdata, ev.ydata)
            new_update_time = datetime.datetime.now()
            secs_since = (new_update_time - _last_update_time).total_seconds()
            if secs_since > _min_update_secs:
                _last_update_time = new_update_time
                print ' .. move to ',_stop_pos
            globe_drag_fromto(_start_pos, _stop_pos)

    elif ev.name == 'button_release_event':
        _mouse_is_down = False
        if ev.inaxes:
            _stop_pos = (ev.xdata, ev.ydata)
            globe_drag_fromto(_start_pos, _stop_pos)
            print 'moved to : ',_stop_pos
        print 'STOPPED.'
        globe_drag_stop()

    else:
        raise Exception('unexpected event : ', ev)


plt.interactive(False)
figure = plt.figure()
globe_drag_stop()

def _mouse_scroll(ev):
    global _globe_zoom
    if ev.step > 0:
        _globe_zoom *= 1.4
    elif ev.step < 0: 
        _globe_zoom /= 1.4
    redraw_globe()

figure.canvas.mpl_connect('button_press_event', _mouse_udm)
figure.canvas.mpl_connect('button_release_event', _mouse_udm)
figure.canvas.mpl_connect('motion_notify_event', _mouse_udm)
figure.canvas.mpl_connect('scroll_event', _mouse_scroll)
plt.show()

#for x in np.arange(0.0,360,step=20):
#  plt.clf()
#  ax=plt.axes(projection=xOrtho(central_latitude=x+35.0, central_longitude=2*x+17.5));
#  t=draw_gridlines(lon_offset=-x);
#  plt.draw(); plt.show(block=False)

