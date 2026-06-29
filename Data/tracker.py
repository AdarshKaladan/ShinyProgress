import matplotlib.pyplot as plt
import time
import numpy as np
from shiny import ui, reactive

class ProgressTracker:
    def __init__(self, name="Progress", total_tasks=10): #input, output, session, logs, name):
        """
        Initializes the ProgressTracker with empty lists for values and times.
        """
        # Shiny env related
        #self.input = input
        #self.output = output
        #self.session = session
        #self.logs = logs

        # Task related
        self.values = [0]
        self.tasks = [0]
        self.total_tasks = total_tasks
        self.times = [0]
        self.time_unit = "seconds"
        self.adj_times = [0]
        self.original_start_time = time.time()
        self.relative_start_time = time.time()
        self.name = name
        self.logs = ["Workspace ready. Configure project on the sidebar."]

    def record_value(self, value, tasks):
        """
        Records a numerical value with the current timestamp relative to the start time.

        Args:
            value (float): The numerical percentage value to record.
            tasks (float): The number of tasks done to be recorded.
        """
        current_time = time.time()
        relative_time = current_time - self.relative_start_time
        self.values.append(value)
        self.tasks.append(tasks)
        self.times.append(relative_time)
        if self.times[-1]>8000:    
            self.adj_times = [i/3600 for i in self.times]
            self.time_unit = "hours"
        elif self.times[-1]>300:
            self.adj_times = [i/60 for i in self.times]
            self.time_unit = "minutes"
        else:
            self.adj_times.append(relative_time)

    def log(self, msg=None):
        if msg:
            self.logs.append(msg)
        else:
            self.logs.append(f"Recorded the value {self.values[-1]:.2f}% for task number {str(self.tasks[-1])} at {self.adj_times[-1]:.2f} {self.time_unit}")
    
    def get_plot(self, theme):
        """Builds the plot using the class's current state."""
        if theme == "dark":
            plt.style.use('dark_background')
        else:
            plt.style.use("default")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(self.adj_times, self.values, '-o', color='green', markerfacecolor='#FF5F1F', markersize=3)
        ax.fill_between(self.adj_times, self.values, color='lime', alpha=0.3)
        ax.set_ylabel("Progress (%)")
        ax.set_xlabel(f"Time ({self.time_unit})")
        ax.set_title(f"Dashboard: {self.project_name}")
        ax.set_ylim(-5, 105)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return fig

    def save(self, max_limit=0):
        """
        Plots the recorded values against time.

        Args:
            max_limit (int, optional): Maximum limit for the y-axis. Defaults to 0 (auto-scaling).
        """
        progress_data = {
            'values': self.values,
            'times': self.times,
            'tasks': self.tasks,
            'original_start_time': self.original_start_time
        }
        np.save(self.name + ".npy", progress_data)

        plt.clf()
        plt.style.use('default')
        plt.figure(figsize=(10,6))

        plt.plot(self.adj_time, self.values, color='green')
        plt.fill_between(self.adj_time, self.values, color='lime', alpha=0.5)

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
        plt.savefig(self.name+".png", dpi=300)
        plt.clf()


    def load(self):
        """
        Loads progress (values and times) from a numpy file.
        If the file is not found or data is invalid, it starts fresh.

        Args:
            filename (str, optional): The name of the file to load from. Defaults to "progress.npy".
        """
        try:
            loaded_data = np.load(self.name+".npy", allow_pickle=True).item()
            self.values = loaded_data['values']
            self.tasks = loaded_data['tasks']
            self.times = loaded_data['times']
            self.original_start_time = loaded_data['original_start_time']
            self.relative_start_time = time.time() - self.times[-1]
            return True
        except FileNotFoundError:
            self.values = [0]
            self.times = [0]
            self.tasks = [0]
            self.original_start_time = time.time()
            self.relative_start_time = time.time()
        return False
    
    def mismatch(self):
        return self.values[-1] != (self.tasks[-1]*100/self.total_tasks)
    
    def recalculate(self):
        multiplier = (self.tasks[-1]*100/self.total_tasks)/self.values[-1]
        self.values = [i*multiplier for i in self.values]
            
    def project(self):
        """
        Creates a separate project with predefined amount of tasks. 
        When a task is completed, user enters '1' to report it. or '0' to pause and save progress.
        Args:
            project_name (str): name of the project and the filename to save progress.
            total_tasks (int): number of tasks
        """
        self.load()
        if self.values[-1] != (self.tasks[-1]*100/self.total_tasks):
            print(f"\033[91mTotal task count mismatches with the values and tasks list!\033[0m \n\033[36mFound:{(self.tasks[-1]*100/self.values[-1]):.2f}, Got:{str(self.total_tasks)}\033[0m")
            self.task_flag = int(input("Should we keep the new count and alter the list? [0/1]: "))
            if self.task_flag:
                multiplier = (self.tasks[-1]*100/self.total_tasks)/self.values[-1]
                self.values = [i*multiplier for i in self.values]
                self.update_plot()
                self.status()
        print("Enter '1' when the current task is finished. Type '0' to pause and store progress.")

        while True:
            if self.tasks[-1]>=total_tasks:
                print(f"All tasks ({str(total_tasks)}) in project is now completed.\n\033[92m\033[5mCongratulations on completing the project!\033[0m")
                break
            user_input = input("Status of current task: ")

            if user_input == '0':break
            task_count = self.tasks[-1]+1
            value = 100*task_count/total_tasks
            self.record_value(value, task_count)
            
        if self.tasks[-1]<self.total_tasks:self.status()
        self.save()

