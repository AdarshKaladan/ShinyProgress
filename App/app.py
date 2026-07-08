# General Imports
import sys, time
from pathlib import Path
from shiny import ui, render, reactive, App, run_app

# Importing the task manager package
data_path = Path(__file__).resolve().parent.parent / "Data"
sys.path.append(str(data_path))
from tracker import ProgressTracker

# List of tasks (if any)
tasklist = lambda : ["Create New."] + [i.stem for i in data_path.glob("*.npy")]

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Configuration"),
        ui.input_select("project_select", "Select Project", choices=tasklist()),
        
        # This text input only displays when "Create new..." is selected
        ui.panel_conditional(
            "input.project_select == 'Create New.'",
            ui.input_text("new_proj_name", "New Project Name", value="")
        ),
        
        ui.panel_conditional(
            "input.project_select != 'Create New.'",
            ui.input_switch("time_correct", "Break Time Exclusion", True)
        ),
        
        ui.input_numeric("total_tasks", "Total Tasks", value=10, min=1),
        ui.hr(),
        ui.input_action_button("start_btn", "Start Series", class_="btn-primary w-100"),
        ui.input_dark_mode(id="theme")
    ),
    
    # Main content layout split: 4 columns for interactive controls, 8 columns for plot
    ui.layout_columns(
        ui.card(
            ui.card_header("Series Controls & Status"),
            ui.input_action_button("done_btn", "Task Completed", class_="btn-success w-100 mb-2", disabled=True),
            ui.input_action_button("end_btn", "End Series & Save", class_="btn-danger w-100 mb-3", disabled=True),
            ui.hr(),
            ui.output_ui("status_log"),
            ui.output_ui("timer_display"),
            style="height: 550px; overflow-y: auto;"
        ),
        ui.card(
            ui.card_header("Live Progress Chart"),
            ui.output_plot("progress_plot"),
            style="height: 550px;"
        ),
        col_widths=[4, 8]
    )
)

def server(input, output, session):
    project = ProgressTracker()
    refresh_trigger = reactive.Value(0)
    timer_active = reactive.Value(False)
    last_task_time = reactive.Value(time.time())

    @render.plot
    def progress_plot():
        refresh_trigger.get()
        return project.get_plot(theme = input.theme())
    
    @render.text
    def status_log():
        refresh_trigger.get()
        #return project.logs[-1]
        
        # Fetch only the very last message in the list
        msg = project.logs[-1] if project.logs else ""
        
        # Simple color assignment logic
        color = "lightgreen" if "successfully" in msg and input.theme() == "dark" else \
                "green" if "successfully" in msg else \
                "lightblue" if "Recorded" in msg and input.theme() == "dark" else \
                "darkblue" if "Recorded" in msg else \
                "salmon" if "not found" in msg and input.theme() == "dark" else \
                "red" if "not found" in msg else \
                "lightgray" if input.theme() == "dark" else "#212529"
        
        bgcolor = "#212529" if input.theme() == "dark" else "#ECECEC"
        
        # Return a single formatted text block
        return ui.div(
            ui.span(msg, style=f"color: {color}; font-weight: bold; font-family: monospace; font-size: 1.1em;"),
            style=f"background-color: {bgcolor}; padding: 12px; border-radius: 6px; text-align: center;"
        )
    
    @render.text
    def timer_display():
        color = "lightblue" if input.theme() == "dark" else "darkblue"
        bgcolor = "#212529" if input.theme() == "dark" else "#ECECEC"
        # If a session isn't running, keep it flat at zero
        if not timer_active.get():
            return ui.div(
                ui.span("⏱ Task Timer: 00:00:00", style=f"color: {color}; font-weight: bold; font-family: monospace; font-size: 1.1em;"),
                style=f"background-color: {bgcolor}; padding: 12px; border-radius: 6px; text-align: center;"
            )
        
        # This line forces Shiny to rerun this specific function every 1 second!
        reactive.invalidate_later(1)
        
        # Calculate minutes and seconds elapsed since the last reset
        elapsed_seconds = int(time.time() - last_task_time.get())
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        msg = f"⏱ Task Timer: {hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return ui.div(
            ui.span(msg, style=f"color: {color}; font-weight: bold; font-family: monospace; font-size: 1.1em;"),
            style=f"background-color: {bgcolor}; padding: 12px; border-radius: 6px; text-align: center;"
        )

    @reactive.effect
    @reactive.event(input.start_btn)
    def loading():
        nonlocal project
        if input.project_select() == "Create New.":
            project = ProgressTracker(input.new_proj_name(), input.total_tasks(), str(data_path))
        else:
            project = ProgressTracker(input.project_select(), input.total_tasks(), str(data_path))
        project.load()
        if input.project_select() != "Create New." and not input.time_correct():
            project.relative_start_time = project.original_start_time
        
        if project.mismatch():
            ui.modal_show(
                ui.modal(
                    f"Total task count mismatches with the values and tasks list!\n"
                    f"Found: {(project.tasks[-1]*100/project.values[-1]):.2f}, \nGot:{str(project.total_tasks)}",
                    title="Total Task Count Mismatch",
                    footer=ui.div(
                        ui.input_action_button("mismatch_rescale", "Rescale", class_="btn-warning"),
                        ui.input_action_button("mismatch_dismiss", "Dismiss", class_="btn-light"),
                    ), easy_close=False
                )
            )
        
        ui.update_action_button("start_btn", disabled=True)
        ui.update_action_button("done_btn", disabled=False)
        ui.update_action_button("end_btn", disabled=False)
        refresh_trigger.set(refresh_trigger.get()+1)
        timer_active.set(True)
        last_task_time.set(time.time())

    @reactive.effect
    @reactive.event(input.mismatch_rescale)
    def _():
        project.rescale()
        refresh_trigger.set(refresh_trigger.get()+1)
        ui.modal_remove()
    
    @reactive.effect
    @reactive.event(input.mismatch_dismiss)
    def _():
        ui.modal_remove()

    @reactive.effect
    @reactive.event(input.done_btn)
    def task_done():
        project.task_done()
        if project.tasks[-1] >= project.total_tasks:
            ui.modal_show(
                ui.modal(
                    "Congratulations!! You've completed all the tasks! Take some rest now!",
                    title="Tasks completed",
                    easy_close=True,
                )
            )
            project.save()
            ui.update_action_button("start_btn", disabled=False)
            ui.update_action_button("done_btn", disabled=True)
            ui.update_action_button("end_btn", disabled=True)
            ui.update_select("project_select", choices=tasklist(), selected=project.name)
            timer_active.set(False)
        
        last_task_time.set(time.time())
        refresh_trigger.set(refresh_trigger.get()+1)

    
    @reactive.effect
    @reactive.event(input.end_btn)
    def task_break():
        project.save()
        ui.update_action_button("start_btn", disabled=False)
        ui.update_action_button("done_btn", disabled=True)
        ui.update_action_button("end_btn", disabled=True)
        ui.update_select("project_select", choices=tasklist(), selected=project.name)
        refresh_trigger.set(refresh_trigger.get()+1)
        timer_active.set(False)


app = App(app_ui, server)

if __name__ == "__main__":
    run_app(app, host="0.0.0.0", port=8000)