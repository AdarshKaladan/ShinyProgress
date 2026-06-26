import matplotlib.pyplot as plt
import time
import numpy as np

class ProgressTracker:
    def __init__(self):
        """
        Initializes the ProgressTracker with empty lists for values and times.
        """
        self.values = [0]
        self.tasks = [0]
        self.total_tasks = 0
        self.times = [0]
        self.original_start_time = time.time()
        self.relative_start_time = time.time()

        # Initialize the plot for real-time updates
        plt.ion()
        with plt.style.context('dark_background'): # to use it globally, use .use instead of .context
            self.fig, self.ax = plt.subplots(figsize=(8, 5))
            self.line, = self.ax.plot(self.times, self.values, '-o', color='green', markerfacecolor='#FF5F1F', markersize=3)
        self.fill = None # Placeholder for the fill_between
        
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Progress (%)")
        self.ax.set_title("Live Progress Tracker")
    
    def update_plot(self):
        """Updates the existing plot window with new data."""
        self.line.set_data(self.times, self.values)
        
        # Update the filling (requires removing the old one first)
        if self.fill:
            self.fill.remove()
        self.fill = self.ax.fill_between(self.times, self.values, color='lime', alpha=0.3)
        
        # Rescale axes to fit new data
        self.ax.relim()
        self.ax.autoscale_view()
        
        # Draw and pause briefly to allow the UI to refresh
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.1)

    def record_value(self, value, tasks=None):
        """
        Records a numerical value with the current timestamp relative to the start time.

        Args:
            value (float): The numerical percentage value to record.
            value (float): If number of tasks done is available, that can also be recorded
        """
        current_time = time.time()
        relative_time = current_time - self.relative_start_time
        self.values.append(value)
        if tasks:self.tasks.append(tasks)
        self.times.append(relative_time)
        print(f"Value \033[92m{value:.2f}%\033[0m", end='')
        if self.total_tasks:print(f" and tasks \033[92m{tasks}\033[0m", end='')
        print(f" recorded at time \033[92m{relative_time:.2f}\033[0m seconds.")
        self.update_plot()

    def status(self):
        print(f"So far, \033[92m{str(round(self.values[-1],2))}%\033[0m", end='')
        if self.total_tasks:print(f" or \033[92m{str(self.tasks[-1])} out of {str(self.total_tasks)}\033[0m ", end='')
        print(f" tasks completed in \033[92m{str(round(self.times[-1],2))} Sec\033[0m")

    def plot_progress(self, filename='progress.png', max_limit=0):
        """
        Plots the recorded values against time.

        Args:
            max_limit (int, optional): Maximum limit for the y-axis. Defaults to 0 (auto-scaling).
        """
        if self.values:
            plt.close(self.fig) #plt.clf()
            plt.style.use('default')
            plt.figure(figsize=(10,6))
            if self.times[-1]>4000:    
                x_data = [i/3600 for i in self.times]
                time_unit = "hours"
            else:
                x_data = self.times
                time_unit = "seconds"

            plt.plot(x_data, self.values, color='green')
            plt.fill_between(x_data, self.values, color='lime', alpha=0.5)

            # Marking final state with orange dot
            final_time = x_data[-1]
            final_value = self.values[-1]
            neon_orange = '#FF5F1F'
            plt.plot(final_time, final_value, 'o', color=neon_orange, markersize=8, zorder=5)

            plt.annotate(f"Time: {final_time:.2f} {time_unit}\nProgress: {final_value:.2f}%",
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
            plt.xlabel(f"Time taken ({time_unit})")
            plt.title("Plot of Progress")
            if max_limit:
                plt.ylim(0, max_limit)
            plt.savefig(filename, dpi=300)
            plt.ioff()
            plt.show()
        else:
            print("No values recorded, nothing to plot.")
    
    def run(self):
            print("Enter the percentage of work done to plot. Type 'done' when finished.")

            while True:
                user_input = input("Enter a value (or 'done'): ")

                if user_input.lower() == 'done':
                    break

                try:
                    value = float(user_input)
                    self.record_value(value)

                except ValueError:
                    print("Invalid input. Please enter a number or 'done'.")

    def save(self, filename="progress.npy"):
        """
        Saves the current progress (values and times) to a numpy file.

        Args:
            filename (str, optional): The name of the file to save to. Defaults to "progress.npy".
        """
        progress_data = {
            'values': self.values,
            'times': self.times,
            'tasks': self.tasks,
            'original_start_time': self.original_start_time
        }
        np.save(filename, progress_data)
        print(f"Progress saved to {filename}")

    def load(self, filename="progress.npy"):
        """
        Loads progress (values and times) from a numpy file.
        If the file is not found or data is invalid, it starts fresh.

        Args:
            filename (str, optional): The name of the file to load from. Defaults to "progress.npy".
        """
        try:
            loaded_data = np.load(filename, allow_pickle=True).item()
            self.values = loaded_data['values']
            self.tasks = loaded_data['tasks']
            self.times = loaded_data['times']
            self.original_start_time = loaded_data['original_start_time']
            current_time = time.time()
            print("\nPrevious session found!")
            print("1: Resume (Ignore the break time)")
            print("2: Continuous (Include the break time)")
            
            while True:
                choice = input("Select mode (1/2): ")
                current_time = time.time()
                if choice == '1':
                    self.relative_start_time = current_time - self.times[-1]
                    break
                elif choice == '2':
                    self.relative_start_time = self.original_start_time
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")
            self.status()
            self.update_plot()
        except FileNotFoundError:
            print(f"File {filename} not found. Starting fresh.")
            self.values = [0]
            self.times = [0]
            self.tasks = [0]
            self.original_start_time = time.time()
            self.relative_start_time = time.time()
            
            
    def project(self, project_name, total_tasks):
        """
        Creates a separate project with predefined amount of tasks. 
        When a task is completed, user enters '1' to report it. or '0' to pause and save progress.
        Args:
            project_name (str): name of the project and the filename to save progress.
            total_tasks (int): number of tasks
        """
        self.total_tasks = total_tasks
        self.load(filename=project_name+'.npy')
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
        self.save(project_name+'.npy')
        self.plot_progress(filename = project_name+'.png', max_limit = 100)

    def help(self):
        print("Progress tracker is a tool used to track and save progress in completing any task. There are a few functions you can use here such as:")
        print("\033[92m \t load(\"filename.npy\")\033[0m: Loads progress (percentage values, tasks and times) from a numpy file. If the file is not found or data is invalid, it starts fresh.")
        print("\033[92m\t save(filename=\"progress.npy\")\033[0m: It saves the current progress as a numpy file. By default the name is \"progress.npy\"")
        print("\033[92m\t run()\033[0m: This the part where you record the progress. You run it and it\'ll record the percentage of work done (manual calculation) and the time. When you\'re done with it, just type \"done\"")
        print("\033[92m\t plot_progress(filename=\"progress.png\", max_limit=0)\033[0m: This will plot the current progress and save with the given filename or the default if not mentioned. The other argument is to set y-axis limit. 0 means autoscale")

        print("\033[36m\t project(project_name, total_tasks)\033[0m: This eases the whole process. You just have to call the function with name number of tasks. And above mentioned methods will be done for you.")

print("use help() for function usage details.")
if __name__ == "__main__":
    tracker = ProgressTracker()
    tracker.load("progress.npy") # Load previous progress if available
    tracker.run()
    tracker.plot_progress()
    tracker.save("progress.npy")