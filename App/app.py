# General Imports
import os, sys, glob
from pathlib import Path
from shiny import ui, render, reactive, App

# Importing the task manager package
data_path = Path(__file__).resolve().parent.parent / "Data"
sys.path.append(str(data_path))
from tracker import ProgressTracker

# List of tasks (if any)
tasklist = lambda : ["Create New."] + [os.path.basename(i).split(".")[0] for i in glob.glob(str(data_path / "*.npy"))]

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
            ui.output_text_verbatim("status_log"),
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
    @reactive.effect
    @reactive.event(input.start_btn)
    def loading():
        project = ProgressTracker(input.new_proj_name(), input.total_tasks()) if input.project_select() == "Create New." else ProgressTracker(input.project_select(), input.total_tasks())
        project.load()
        if input.project_select() != "Create New." and not input.time_correct():
            project.relative_start_time = project.original_start_time
        
        if project.mismatch():
            ui.modal_show(
                ui.modal(
                    f"Total task count mismatches with the values and tasks list!"
                    f"Found:{(project.tasks[-1]*100/project.values[-1]):.2f}, Got:{str(project.total_tasks)}",
                    title="Total Task Count Mismatch",
                    footer=ui.div(
                        ui.input_action_button("mismatch_rescale", "Rescale", class_="btn-warning"),
                        ui.input_action_button("mismatch_dismiss", "Dismiss", class_="btn-light"),
                    ), easy_close=False
                )
            )
        
        ui.update_action_button("start_btn", disabled=True)

    @reactive.effect
    @reactive.event(input.mismatch_rescale)
    def _():
        project.rescale()
        ui.modal_remove()
    
    @reactive.effect
    @reactive.event(input.mismatch_dismiss)
    def _():
        ui.modal_remove()
        
            

    pass