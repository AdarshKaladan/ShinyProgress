# Progress Tracker (Shiny Web App)

A simple, lightweight web application built with Shiny for Python to help track task completion over time. It's nothing too fancy—just a handy tool to keep track of your workflow, save your sessions, and visualize your momentum.

## Features

![App Screenshot](Data/screenshot.png)
*(Note: Ensure your image is saved as `screenshot.png` in the `Data` folder for this to display correctly on GitHub)*

* **Interactive Web UI:** Built with Shiny for Python, providing a clean dashboard accessible from your browser (even on your phone via your local network).

* **Live Visualization:** Automatically generates and updates a progress chart using Matplotlib as you complete tasks.

* **Session Management:** Saves your progress locally as `.npy` binary files. You can close the app, come back later, and pick up exactly where you left off.

* **Smart Time Tracking:** When resuming a saved project, it politely asks if you want to include your break time in the total elapsed time or exclude it.

* **Dynamic Rescaling:** If you load an old project but decide to change the total number of tasks, the app will detect the mismatch and offer to rescale your previous progress to fit the new goal.

* **Color-Coded Logging:** A minimal terminal window in the UI highlights important numbers and percentages automatically so you can easily spot them.

## Folder Structure

To keep things organized, the project is split into two main directories:

```text
ProgressTracker/
│
├── App/
│   └── app.py         # The Shiny web app, UI layout, and reactive server logic.
│
└── Data/
    ├── tracker.py     # The core Python class handling math, plots, and file saving.
    ├── screenshot.png # Image used in this README.
    └── *.npy          # Your saved session files will appear here automatically.
```