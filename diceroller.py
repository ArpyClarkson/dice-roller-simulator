import random
import statistics
from collections import Counter
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import mplcursors  # For interactive tooltips on the graph

# This function simulates rolling dice.
# It returns a list where each element is the sum of rolling 'num_dice' dice (each with 'sides' sides) for one roll.
def roll_dice(sides, num_dice, num_rolls):
    return [sum(random.randint(1, sides) for _ in range(num_dice)) for _ in range(num_rolls)]

# This function updates all statistics, the graph, and the output areas in the UI when the user clicks "Roll!" or changes input.
def update_stats():
    try:
        # Get user input from the UI and convert to integers
        sides = int(sides_var.get())
        num_dice = int(num_dice_var.get())
        num_rolls = int(num_rolls_var.get())
        # Validate input: all values must be positive integers
        if sides < 1 or num_dice < 1 or num_rolls < 1:
            raise ValueError
    except ValueError:
        # If input is invalid, show an error and clear outputs
        stats_var.set("Please enter positive integers for all fields.")
        roll_totals_text.delete(1.0, tk.END)
        roll_totals_text.insert(tk.END, "")
        return

    # Simulate the dice rolls
    roll_totals = roll_dice(sides, num_dice, num_rolls)
    min_total = num_dice * 1  # Minimum possible roll total
    max_total = num_dice * sides  # Maximum possible roll total
    tally = Counter(roll_totals)  # Count how many times each total occurred
    values = list(range(min_total, max_total + 1))  # All possible totals
    frequencies = [tally.get(value, 0) for value in values]  # Frequency for each possible total

    # Update the text area showing roll results (limit to first 100 for performance)
    roll_totals_text.delete(1.0, tk.END)
    max_display = 250
    if len(roll_totals) > max_display:
        shown = ', '.join(map(str, roll_totals[:max_display]))
        roll_totals_text.insert(
            tk.END,
            f"{shown}, ...\n({len(roll_totals)-max_display} more not shown)"
        )
    else:
        roll_totals_text.insert(tk.END, ', '.join(map(str, roll_totals)))

    # Calculate and display summary statistics
    stats = [
        f"Count: {len(roll_totals)}",  # Total number of rolls
        f"Minimum: {min(roll_totals)}",  # Smallest roll total
        f"Maximum: {max(roll_totals)}",  # Largest roll total
        f"Mean: {statistics.mean(roll_totals):.2f}",  # Average roll total
        f"Median: {statistics.median(roll_totals):.2f}",  # Middle value
        f"Standard Deviation: {statistics.stdev(roll_totals):.2f}" if len(roll_totals) > 1 else "Standard Deviation: N/A"  # Spread of results
    ]
    stats_var.set('\n'.join(stats))

    # Draw/update the bar graph showing the frequency of each roll total
    ax.clear()
    bars = ax.bar(values, frequencies, color='skyblue')
    ax.set_xlabel('Roll Total')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Tally of {num_rolls} Roll Totals ({num_rolls}x{num_dice} d{sides})')
    ax.set_xticks(values)
    fig.tight_layout()

    # Add interactive tooltips to the bars in the graph
    # When you hover over a bar, it shows the total, count, and chance of that total
    if hasattr(ax, 'mplcursors_cursor'):
        try:
            ax.mplcursors_cursor.remove()
        except Exception:
            pass
    cursor = mplcursors.cursor(bars, hover=True)
    @cursor.connect("add")
    def on_add(sel):
        idx = sel.index  # Which bar is hovered
        value = values[idx]  # The roll total for this bar
        freq = frequencies[idx]  # How many times this total occurred
        # Calculate the chance as "1 in X" or "N/A" if not possible
        if freq > 0:
            chance = f"1 in {num_rolls // freq}" if num_rolls // freq > 0 else f"{freq} in {num_rolls}"
        else:
            chance = "N/A"
        sel.annotation.set_text(
            f"Total: {value}\nCount: {freq}\nChance: {chance}"
        )
    ax.mplcursors_cursor = cursor

    canvas.draw()

# --- Tkinter UI setup (the window and all widgets) ---

root = tk.Tk()
root.title("Dice Roller Simulator")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Input for number of sides on the dice
ttk.Label(mainframe, text="Sides on dice:").grid(row=0, column=0, sticky=tk.W)
sides_var = tk.StringVar(value="6")
sides_entry = ttk.Entry(mainframe, width=7, textvariable=sides_var)
sides_entry.grid(row=0, column=1, sticky=tk.W)

# Input for number of dice to roll each time
ttk.Label(mainframe, text="Number of dice:").grid(row=1, column=0, sticky=tk.W)
num_dice_var = tk.StringVar(value="2")
num_dice_entry = ttk.Entry(mainframe, width=7, textvariable=num_dice_var)
num_dice_entry.grid(row=1, column=1, sticky=tk.W)

# Input for number of rolls to perform
ttk.Label(mainframe, text="Number of rolls:").grid(row=2, column=0, sticky=tk.W)
num_rolls_var = tk.StringVar(value="100")
num_rolls_entry = ttk.Entry(mainframe, width=7, textvariable=num_rolls_var)
num_rolls_entry.grid(row=2, column=1, sticky=tk.W)

# Button to trigger rolling and updating the stats/graph
reroll_button = ttk.Button(mainframe, text="Roll!", command=update_stats)
reroll_button.grid(row=3, column=0, columnspan=2, pady=5)

# Text area to display the roll totals (first 100 shown)
ttk.Label(mainframe, text="All roll totals:").grid(row=4, column=0, sticky=tk.W)
roll_totals_text = tk.Text(mainframe, width=40, height=4, wrap=tk.WORD)
roll_totals_text.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

# Label to display summary statistics
stats_var = tk.StringVar()
stats_label = ttk.Label(mainframe, textvariable=stats_var, justify=tk.LEFT)
stats_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)

# Create the matplotlib figure and embed it in the Tkinter window
fig, ax = plt.subplots(figsize=(6, 3))
canvas = FigureCanvasTkAgg(fig, master=mainframe)
canvas.get_tk_widget().grid(row=0, column=2, rowspan=10, padx=10, pady=5)

# Run the initial roll and show the UI
update_stats()
root.mainloop()