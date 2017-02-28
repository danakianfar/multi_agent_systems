import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from controller import *
import matplotlib.cm as cm

class Simulation:
    def __init__(self, bus_class=Bus , iterations=100, show=False, save_file=None, interval=100, debug=False):
        self.debug = debug
        
        self.controller = Controller(bus_class, debug=debug)
        
        self.controller.setup()
        
        if show:
            figure, title, bus_plot, station_plot= self.init_plot()
            self.anim = animation.FuncAnimation(figure, self.animate, 
                                           iterations, 
                                           fargs=(title, bus_plot, station_plot, self), 
                                           interval=interval,
                                           blit = False)
            if save_file:
                anim.save(save_file)
        else:
            for _ in range(iterations):
                self.main_loop()
    
    def main_loop(self):
        self.controller.step()
 
    @staticmethod
    def animate(i, title, bus_plot, station_plot,  self):
        bus_plot, station_plot = self.update_plot(title, bus_plot, station_plot)
        self.main_loop()
        return bus_plot,station_plot

    def update_plot(self,title, bus_plot, station_plot):
        buses = [(bus.x, bus.y, bus.bus_id) for bus in self.controller.buses.values()]
 
        buses_x = [bus[0] for bus in buses]
        buses_y = [bus[1] for bus in buses]
                
        bus_plot.set_data(buses_x, buses_y)

        title.set_text('ticks:{}'.format(self.controller.ticks)) # tick counter

        for stop_id, stop in self.controller.bus_stops.items():
            station_plot[stop_id].remove()
            station_plot[stop_id] = plt.annotate('%s,%s\n(# %s)' % (str(stop.stop_id), stop.name[:3], len(stop.passengers_waiting)), xy=(stop.x+0.3, stop.y-0.3))
        
        return bus_plot, station_plot

    def init_plot(self):
        plot_figure = plt.figure(figsize=(10,8))
        ax = plt.axes()
        title = ax.text(0.02,0.95,'', transform=ax.transAxes)
        
        stop_x = [stop.x for stop in self.controller.bus_stops.values()]
        stop_y = [stop.y for stop in self.controller.bus_stops.values()]
        
        plt.ylim(-1,31)
        plt.plot(stop_x, stop_y, 'o')

        station_plot = {}
        
        for stop_id, station in enumerate(self.controller.connections):
            sx = self.controller.bus_stops[stop_id].x
            sy = self.controller.bus_stops[stop_id].y
            
            stop = self.controller.bus_stops[stop_id]

            station_plot[stop_id] = plt.annotate('{},{}'.format(str(stop.stop_id),stop.name[:3]), xy=(sx+0.3, sy-0.3))
            station_plot[stop_id].set_animated(True)

            
            for destination_id in station:
                dx = self.controller.bus_stops[destination_id].x
                dy = self.controller.bus_stops[destination_id].y
                plt.plot([sx,dx], [sy,dy], color='b', alpha=0.3)

        
        bus_plot, = plt.plot([], [], 'o', color='g', markersize=10, marker=(4,0,0), alpha=0.3)

        return plot_figure, title, bus_plot, station_plot
    