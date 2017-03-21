import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from controller import *
import matplotlib.cm as cm

class Simulation:
    def __init__(self, bus_class=Bus, loggers=[]):

        self.controller = Controller(bus_class, loggers=loggers)
        self.controller.setup()


    def main_loop(self):
        self.controller.step()

    def execute(self, iterations=100, animate=False, save_file=None, interval=100):
        if animate:
            figure, title, bus_plot, station_plot, bus_annotations= self.init_plot()
            self.anim = animation.FuncAnimation(figure, self.animate,
                                           iterations,
                                           fargs=(title, bus_plot, station_plot, bus_annotations, self),
                                           interval=interval,
                                           blit = False)
            if save_file:
                self.anim.save(save_file)
        else:
            for i in range(iterations):
                print('\r %d / %d ' % (i+1, iterations), end='')
                self.main_loop()

        return self.controller.logged_data

    @staticmethod
    def animate(i, title, bus_plot, station_plot, bus_annotations,  self):
        print('\r{}'.format(i), end='')
        bus_plot, station_plot = self.update_plot(title, bus_plot, station_plot, bus_annotations)
        self.main_loop()
        return bus_plot,station_plot, bus_annotations

    def update_plot(self,title, bus_plot, station_plot, bus_annotations):
        buses = [(bus.x, bus.y, bus.bus_id) for bus in self.controller.buses.values()]

        buses_x = [bus[0] for bus in buses]
        buses_y = [bus[1] for bus in buses]

        bus_plot.set_data(buses_x, buses_y)

        for bus in buses:
            if bus[2] in bus_annotations:
                bus_annotations[bus[2]].remove()

            bus_annotations[bus[2]] = plt.annotate('%s #%s' % (bus[2], len(self.controller.buses[bus[2]].bus_passengers)), xy=(bus[0], bus[1]))


        title.set_text('ticks:{}'.format(self.controller.ticks)) # tick counter

        for stop_id, stop in self.controller.bus_stops.items():
            station_plot[stop_id].remove()
            station_plot[stop_id] = plt.annotate('%s,%s\n(# %s)' % (str(stop.stop_id), stop.name[:3], len(stop.passengers_waiting)), xy=(stop.x+0.3, stop.y-0.3))

        return bus_plot, station_plot


    def reset(self, bus_genomes = [], genome_distro= [], add_arrivals_noise=False):
        self.controller.reset(bus_genomes, genome_distro)
        self.controller.setup(add_arrivals_noise)

    def init_plot(self):
        plot_figure = plt.figure(figsize=(10,8))
        ax = plt.axes()
        title = ax.text(0.02,0.95,'', transform=ax.transAxes)

        stop_x = [stop.x for stop in self.controller.bus_stops.values()]
        stop_y = [stop.y for stop in self.controller.bus_stops.values()]

        plt.ylim(-1, 31)
        plt.plot(stop_x, stop_y, 'o')

        station_plot = {}
        bus_annotations = {}

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

        return plot_figure, title, bus_plot, station_plot, bus_annotations
