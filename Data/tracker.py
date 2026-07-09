import matplotlib.pyplot as plt
import time
import numpy as np

class ProgressTracker:
    """
    A lightweight utility to track and plot your progress in completing a task over time. 
    Attributes:
        name (str)                  : Name of the project.
        total_tasks (int)           : No. of tasks in the project.
        data_path (str)             : Path to the directory where the progress needs to be saved.
        tasks (list of int)         : List of tasks completed used to log and mark the milestones.
        values (list of float)      : List of percentage of task completed used to plot and log.
        times (list of float)       : List of raw elapsed timestamps corresponding to tasks and values.
        adj_times (list of float)   : List of elapsed timestamps that are scaled for readability wrt time units.
        time_unit (str)             : The unit of time for which the adj_time is scaled for.
        original_start_time (float) : History timestamp when the project originally started.
        relative_start_time (float) : Starting timestamp adjusted for breaks.
        logs (list of str)          : List of log messages recording different steps in the tracking process
    """
    def __init__(self, name="Progress", total_tasks=10, data_path="../Data"):
        """
        Initializes the ProgressTracker with empty lists or starters for values, times, and whatnot.
        Args:
            name (str)          : Name of the project, which will be used in plots and as filename for saving and loading progress.
            total_tasks (int)   : Total number of tasks the project has.
            data_path (str)     : Path to the directory where the progress needs to be saved.
        """
        self.values = [0]
        self.tasks = [0]
        self.total_tasks = total_tasks
        self.times = [0]
        self.time_unit = "seconds"
        self.adj_times = [0]
        self.original_start_time = time.time()
        self.relative_start_time = time.time()
        self.name = name
        self.data_path = data_path+"/"
        self.logs = ["Workspace ready. Configure project on the sidebar."]

    def task_done(self):
        """
        When called, it adds the next number to the task list, calculate the percentage wrt total tasks and stores it in values 
        list, and also records the time when all of this happened.
        """
        
        self.tasks.append(self.tasks[-1] + 1)
        self.values.append((self.tasks[-1] / self.total_tasks) * 100.0)
        self.times.append(time.time() - self.relative_start_time)
        self.unit_scale()
        
        self.log(f"Recorded the value {self.values[-1]:.2f}% for task number {str(self.tasks[-1])} at {self.adj_times[-1]:.2f} {self.time_unit}")
    
    def unit_scale(self):
        """"
        This function scales the time list with a multiplier depending on the highest number for changing the unit between 
        seconds, minutes, and hours.
        """
        if self.times[-1]>8000:    
            self.adj_times = [i/3600 for i in self.times]
            self.time_unit = "hours"
        elif self.times[-1]>300:
            self.adj_times = [i/60 for i in self.times]
            self.time_unit = "minutes"
        else:
            self.adj_times = self.times

    def log(self, msg):
        """
        Adds a log message into a list of strings of logs
        Args:
            msg (str): the text that needs to be added to the logs
        """
        self.logs.append(msg)
    
    def get_plot(self, theme):
        """
        Returns a plot using the current values.
        Args:
            theme (str): if "dark" the plot will use dark mode
        Returns:
            matplotlib Figure: a matplotlib figure containing the plot that shiny can display as an image
        """
        if theme == "dark":
            plt.style.use('dark_background')
        else:
            plt.style.use("default")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(self.adj_times, self.values, '-o', color='green', markerfacecolor='#FF5F1F', markersize=3)
        ax.fill_between(self.adj_times, self.values, color='lime', alpha=0.3)
        ax.set_ylabel("Progress (%)")
        ax.set_xlabel(f"Time ({self.time_unit})")
        ax.set_title(f"Dashboard: {self.name}")
        ax.set_ylim(-5, 105)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return fig

    def save(self):
        """
        When called, it converts the recorded values into a dictionary and saves it as a numpy file. It also plots the recorded percentage 
        values against their corresponding time taken and saves it in a png file.
        """
        progress_data = {
            'values': self.values,
            'times': self.times,
            'tasks': self.tasks,
            'original_start_time': self.original_start_time
        }
        np.save(self.data_path + self.name + ".npy", progress_data)

        plt.clf()
        plt.style.use('default')
        plt.figure(figsize=(10,6))

        plt.plot(self.adj_times, self.values, color='green')
        plt.fill_between(self.adj_times, self.values, color='lime', alpha=0.5)

        # Marking final state with orange dot
        final_time = self.adj_times[-1]
        final_value = self.values[-1]
        neon_orange = '#FF5F1F'
        plt.plot(final_time, final_value, 'o', color=neon_orange, markersize=8, zorder=5)

        plt.annotate(f"Time: {final_time:.2f} {self.time_unit}\nProgress: {final_value:.2f}%",
            xy=(final_time, final_value),
            xytext=(20, 30), 
            textcoords='offset points',
            arrowprops=dict(arrowstyle="->", color=neon_orange, lw=1.5),
            color=neon_orange,
            fontweight='bold',
            horizontalalignment='right')

        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.ylabel("Progress (%)")
        plt.xlabel(f"Time taken ({self.time_unit})")
        plt.title("Plot of Progress")
        plt.ylim(0, 100)
        plt.savefig(self.data_path + self.name+".png", dpi=300)
        plt.clf()

        self.log(f"The current progress ({str(self.tasks[-1])} tasks in {self.adj_times[-1]:.2f} {self.time_unit}) has been saved at {self.name}.npy and plotted at {self.name}.png successfully. Start new project from the sidebar")


    def load(self):
        """
        The function either loads a previously saved progress with the same name given, or resets the time and values.
        Returns:
            Bool: Boolean value depending on whether the loading was successful or not
        """
        try:
            loaded_data = np.load(self.data_path+self.name+".npy", allow_pickle=True).item()
            self.values = loaded_data['values']
            self.tasks = loaded_data['tasks']
            self.times = loaded_data['times']
            self.original_start_time = loaded_data['original_start_time']
            self.relative_start_time = time.time() - self.times[-1]
            self.unit_scale()
            self.log(f"The file {self.name}.npy has been loaded successfully. Currently sitting at task {str(self.tasks[-1])} using {self.adj_times[-1]:.2f} {self.time_unit}")
            return True
        except FileNotFoundError:
            self.values = [0]
            self.times = [0]
            self.tasks = [0]
            self.original_start_time = time.time()
            self.relative_start_time = time.time()
            self.log(f"A fresh new project is created using zero value and current time as starting time with the name {self.name}")
        return False
    
    def mismatch(self):
        """
        Returns a boolean value after checking if the total task count obtained when the class was initiated matches the total task 
        count that can be calculated from previously recorded progress.
        """
        return self.values[-1] != (self.tasks[-1]*100/self.total_tasks)
    
    def rescale(self, rescale=True):
        """
        if there was a mismatch between the initialised total tasks count and the one from previously recorded progress, this one 
        will rescale the values to make sure the initialised task count is the valid one. If there was no mismatch, it simply rewrites 
        the task count with the previously recorded one.
        Args:
            rescale (Bool): the flag that tell the function whether to rescale or not. by default it's True.
        Returns:
            Int: the total task count, either the initialised one or the calculated one depending on the argument.
        """
        if rescale:
            multiplier = (self.tasks[-1]*100/self.total_tasks)/self.values[-1]
            self.values = [i*multiplier for i in self.values]
            self.log(f"Values has been successfully rescaled for {self.total_tasks}")
            return self.total_tasks
        else:
            self.total_tasks = int(self.tasks[-1]*100/self.values[-1])
            self.log(f"The values are not rescaled, but total task count has been successfully changed to {self.total_tasks}")
            return self.total_tasks
                
