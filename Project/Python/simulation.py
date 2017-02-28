import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from controller import *

class Simulation:
    def __init__(self, bus_class=Bus , iterations=100, show=False, save_file=None, interval=100, debug=False):
        self.debug = debug
        
        self.simulation = Controller(bus_class, debug=debug)
        
        self.simulation.setup()
        
        if show:
            figure, title, bus_plot = self.init_plot()
            self.anim = animation.FuncAnimation(figure, self.animate, 
                                           iterations, 
                                           fargs=(title, bus_plot, self), 
                                           interval=interval)
            if save_file:
                anim.save(save_file)
        else:
            for _ in range(iterations):
                self.main_loop()
    
    def main_loop(self):
        self.simulation.step()
 
    @staticmethod
    def animate(i, title, bus_plot, self):
        bus_plot = self.update_plot(title, bus_plot)
        self.main_loop()
        return bus_plot,

    def update_plot(self,title, plot):
        buses_x = [bus.x for bus in self.simulation.buses]
        buses_y = [bus.y for bus in self.simulation.buses]
            
        plot.set_data(buses_x, buses_y)

        title.set_text('ticks:{}'.format(self.simulation.ticks))
        
        return plot

    def init_plot(self):
        plot_figure = plt.figure(figsize=(8,6))
        ax = plt.axes()
        title = ax.text(0.02,0.95,'', transform=ax.transAxes)
        
        stop_x = [stop.x for stop in self.simulation.bus_stops.values()]
        stop_y = [stop.y for stop in self.simulation.bus_stops.values()]
        
        plt.ylim(-1,31)
        plt.plot(stop_x, stop_y, 'o')
        
        for stop_id, station in enumerate(self.simulation.connections):
            sx = self.simulation.bus_stops[stop_id].x
            sy = self.simulation.bus_stops[stop_id].y
            
            stop_name = self.simulation.bus_stops[stop_id].name
            
            plt.annotate('{},{}'.format(str(stop_id),stop_name[:3]), xy=(sx+0.3, sy-0.3))

            
            for destination_id in station:
                dx = self.simulation.bus_stops[destination_id].x
                dy = self.simulation.bus_stops[destination_id].y
                plt.plot([sx,dx], [sy,dy], color='b', alpha=0.3)

        
        bus_plot, = plt.plot([], [], 'o', color='g', markersize=10, marker=(4,0,0), alpha=0.3)

        return plot_figure, title, bus_plot
    