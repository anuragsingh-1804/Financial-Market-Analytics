import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Menu
import yfinance as yf # type: ignore
import matplotlib.pyplot as plt # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import matplotlib.dates as mdates # type: ignore
from matplotlib.widgets import Cursor # type: ignore
import datetime

# --- Initialize main window ---
root = tk.Tk()
root.title("Financial Institution Market Dashboard")
root.state("zoomed")  # Maximized window

# --- Vibrant Color Theme ---
primary_color = "#4B0082"      # Indigo
secondary_color = "#9370DB"    # Medium Purple
accent_color = "#FF7F50"       # Coral
text_color = "#333333"         # Dark gray for text
bg_color = "#FFFFFF"           # Pure white background
sidebar_bg = "#F0F8FF"         # Light blue background for sidebar
chart_bg_color = "#F8F8FF"     # Ghost white for chart backgrounds

# Colorful chart palette
chart_colors = ["#FF6B6B", "#4ECDC4", "#FFD166", "#6A0572", "#F72585", "#4CC9F0"]

# Apply bg color to root and frames
root.configure(bg=bg_color)

# --- Styling ---
style = ttk.Style()
style.theme_use('clam')  # Use clam theme as base for better styling support
style.configure("TFrame", background=bg_color)
style.configure("TLabel", background=bg_color, foreground=text_color, font=("Segoe UI", 12))
style.configure("TLabel.Heading", background=bg_color, foreground=primary_color, font=("Segoe UI", 16, "bold"))
style.configure("TButton", background=accent_color, foreground="#FFFFFF", font=("Segoe UI", 12, "bold"))
style.map("TButton", foreground=[('pressed', "#FFFFFF"), ('active', "#FFFFFF")], background=[('pressed', '!disabled', secondary_color), ('active', accent_color)])

# Configure colorful sidebar style
style.configure("Sidebar.TFrame", background=sidebar_bg)
style.configure("Sidebar.TLabel", background=sidebar_bg, foreground=text_color, font=("Segoe UI", 12))
style.configure("Sidebar.Heading.TLabel", background=sidebar_bg, foreground=primary_color, font=("Segoe UI", 16, "bold"))

# Configure Entry widget style
style.configure("TEntry", fieldbackground="#FFFFFF", foreground=text_color)

# Configure Checkbutton and Radiobutton with colorful accents
style.map("TCheckbutton", background=[("active", sidebar_bg)], foreground=[("active", text_color)])
style.map("TRadiobutton", background=[("active", sidebar_bg)], foreground=[("active", text_color)])

# --- Main Layout with Sidebar on Left ---
main_container = ttk.Frame(root)
main_container.pack(fill=tk.BOTH, expand=True)

# Create left sidebar with colorful background
left_sidebar = ttk.Frame(main_container, width=300, style="Sidebar.TFrame")
left_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
left_sidebar.pack_propagate(False)  # Prevent the frame from shrinking to fit its contents

# Create a separator between sidebar and main content
separator = ttk.Separator(main_container, orient='vertical')
separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)

# Main content area
content_area = ttk.Frame(main_container)
content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

# --- Sidebar Header ---
sidebar_header = ttk.Frame(left_sidebar, padding=(10, 10, 10, 5), style="Sidebar.TFrame")
sidebar_header.pack(fill=tk.X)

ttk.Label(sidebar_header, text="Dashboard Controls", style="Sidebar.Heading.TLabel").pack(anchor='w')

# --- Stock Symbol Selection ---
symbol_frame = ttk.Frame(left_sidebar, padding=(10, 5, 10, 5), style="Sidebar.TFrame")
symbol_frame.pack(fill=tk.X)

ttk.Label(symbol_frame, text="Select Stock Symbol:", style="Sidebar.TLabel").pack(anchor='w')

# Stock symbols list
stock_symbols = ["BMW.DE", "VOW3.DE", "MBG.DE", "P911.DE", "RACE", "AML.L", "LCID", "RIVN", "MCD", "KO", "NVDA", "NFLX", "TSLA", "META", "GOOGL", "AMZN", "AAPL", "ADANIENT.NS", "WIPRO.NS", "TATAMOTORS.NS", "HINDUNILVR.NS", "SBIN.NS", "ICICIBANK.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS", "RELIANCE.NS"]
symbol_var = tk.StringVar()
symbol_combo = ttk.Combobox(symbol_frame, textvariable=symbol_var, values=stock_symbols, width=15, state="readonly")
symbol_combo.pack(fill=tk.X, pady=(5, 0))

fetch_button = ttk.Button(symbol_frame, text="Fetch Data", command=lambda: fetch_stock_data(symbol_var.get()))
fetch_button.pack(fill=tk.X, pady=10)

# --- View Selection Radiobuttons ---
view_frame = ttk.Frame(left_sidebar, padding=(10, 5, 10, 5), style="Sidebar.TFrame")
view_frame.pack(fill=tk.X)

ttk.Label(view_frame, text="Dashboard View:", style="Sidebar.TLabel").pack(anchor='w')

radio_var = tk.IntVar(value=1)  # Default to Option 1

def radiobutton_selected():
    # Fix for graph resizing issue - recreate figure when view changes
    global fig, axes, canvas_plot
    
    # Remove old canvas
    for widget in graph_frame.winfo_children():
        widget.destroy()
    
    # Create new figure and axes
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.tight_layout(pad=4.0)
    fig.set_facecolor(chart_bg_color)
    
    # Create new canvas
    canvas_plot = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Connect the hover event to new canvas
    canvas_plot.mpl_connect('motion_notify_event', hover)
    
    # Update graph titles
    current_view = radio_var.get()
    for pos, title in graph_titles[current_view].items():
        title_labels[pos].config(text=title)
    
    # Trigger graph update with current stock if one is selected
    if symbol_var.get():
        fetch_stock_data(symbol_var.get())

ttk.Radiobutton(view_frame, text="Standard View", variable=radio_var, value=1, command=radiobutton_selected).pack(anchor='w', pady=2)
ttk.Radiobutton(view_frame, text="Technical View", variable=radio_var, value=2, command=radiobutton_selected).pack(anchor='w', pady=2)

# --- Graph Descriptions Section ---
desc_frame = ttk.Frame(left_sidebar, padding=(10, 5, 10, 5), style="Sidebar.TFrame")
desc_frame.pack(fill=tk.X)

ttk.Label(desc_frame, text="Graph Descriptions:", style="Sidebar.TLabel").pack(anchor='w')

descriptions = tk.Text(desc_frame, height=8, width=30, bg='#F0F8FF', fg=text_color, wrap=tk.WORD)
descriptions.pack(fill=tk.X, pady=5)
descriptions.insert(tk.END, "Standard View:\n")
descriptions.insert(tk.END, "• 7-Day Moving Average: Shows price trend smoothed over 7 days\n")
descriptions.insert(tk.END, "• Volume Traded: Daily trading volume\n")
descriptions.insert(tk.END, "• Sales and Profit by Date: Stock price and percent change\n")
descriptions.insert(tk.END, "• Monthly Volume Change: Volume percent change month to month\n\n")
descriptions.insert(tk.END, "Technical View:\n")
descriptions.insert(tk.END, "• Daily High & Low: Shows daily price ranges\n")
descriptions.insert(tk.END, "• Distribution of Returns: Histogram of daily price changes\n")
descriptions.insert(tk.END, "• Sales by Year: Annual performance\n")
descriptions.insert(tk.END, "• Profit & Loss Distribution: Ratio of up/down days\n")
descriptions.config(state=tk.DISABLED)

# --- Interactive Tips ---
tips_frame = ttk.Frame(left_sidebar, padding=(10, 5, 10, 5), style="Sidebar.TFrame")
tips_frame.pack(fill=tk.X)

ttk.Label(tips_frame, text="Interactive Features:", style="Sidebar.TLabel").pack(anchor='w')

tips = tk.Text(tips_frame, height=4, width=30, bg='#F0F8FF', fg=text_color, wrap=tk.WORD)
tips.pack(fill=tk.X, pady=5)
tips.insert(tk.END, "• Hover over any graph to see detailed data\n")
tips.insert(tk.END, "• Data values appear in the tooltip area\n")
tips.insert(tk.END, "• Switch between views to see different visualizations\n")
tips.insert(tk.END, "• Use mouse wheel to scroll the dashboard\n")
tips.config(state=tk.DISABLED)

# --- DATA VISUALIZATION AREA ---

# --- Header Section ---
header_frame = ttk.Frame(content_area, padding=10)
header_frame.pack(fill=tk.X)

title_label = ttk.Label(header_frame, text="Financial Market Analysis", style="TLabel.Heading")
title_label.pack(side=tk.LEFT)

# --- Tooltip label for displaying hover data ---
tooltip_label = ttk.Label(header_frame, text="", background="#FFFFFF", foreground=text_color, font=("Segoe UI", 12), padding=10, borderwidth=1, relief="solid")
tooltip_label.pack(side=tk.RIGHT)

# --- KPI Section with colorful indicators ---
kpi_frame = ttk.Frame(content_area)
kpi_frame.pack(fill=tk.X, pady=(20, 10))

def create_kpi_card(parent, title, value, color):
    card_frame = ttk.Frame(parent, padding=10)
    card_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
    ttk.Label(card_frame, text=title, style="TLabel.Heading").pack()
    kpi_label = ttk.Label(card_frame, text=value, font=("Segoe UI", 24, "bold"), foreground=color)
    kpi_label.pack(pady=10)
    return kpi_label

# KPI indicators with vibrant colors
kpi_close = create_kpi_card(kpi_frame, "Close", "--", chart_colors[0])  # Red
kpi_high = create_kpi_card(kpi_frame, "High", "--", chart_colors[1])    # Teal
kpi_low = create_kpi_card(kpi_frame, "Low", "--", chart_colors[2])      # Yellow

# --- Graph Title Labels ---
titles_frame = ttk.Frame(content_area)
titles_frame.pack(fill=tk.X, pady=(0, 10))

title_labels = {}
title_frame1 = ttk.Frame(titles_frame)
title_frame1.pack(fill=tk.X, expand=True)
title_frame2 = ttk.Frame(titles_frame)
title_frame2.pack(fill=tk.X, expand=True, pady=(10, 0))

title_labels[(0, 0)] = ttk.Label(title_frame1, text="7-Day Moving Average", font=("Segoe UI", 12, "bold"), foreground=chart_colors[0])
title_labels[(0, 0)].pack(side=tk.LEFT, expand=True)

title_labels[(0, 1)] = ttk.Label(title_frame1, text="Volume Traded", font=("Segoe UI", 12, "bold"), foreground=chart_colors[1])
title_labels[(0, 1)].pack(side=tk.RIGHT, expand=True)

title_labels[(1, 0)] = ttk.Label(title_frame2, text="Sales and Profit by Date", font=("Segoe UI", 12, "bold"), foreground=chart_colors[2])
title_labels[(1, 0)].pack(side=tk.LEFT, expand=True)

title_labels[(1, 1)] = ttk.Label(title_frame2, text="Monthly Volume Change (%)", font=("Segoe UI", 12, "bold"), foreground=chart_colors[3])
title_labels[(1, 1)].pack(side=tk.RIGHT, expand=True)

# --- Graph frame ---
graph_frame = ttk.Frame(content_area)
graph_frame.pack(fill=tk.BOTH, expand=True)

# --- Global variables ---
hover_lines = []  # List to store vertical and horizontal lines for tooltips
stock_data = None  # Global variable to store current stock data
annotations = []   # List to store data point annotations

# Store graph titles for each view
graph_titles = {
    1: {  # Standard View
        (0, 0): "7-Day Moving Average",
        (0, 1): "Volume Traded",
        (1, 0): "Sales and Profit by Date",
        (1, 1): "Monthly Volume Change (%)"
    },
    2: {  # Technical View 
        (0, 0): "Daily High & Low",
        (0, 1): "Distribution of Daily Returns",
        (1, 0): "Sales by Year",
        (1, 1): "Profit & Loss Distribution"
    }
}

# --- Function to fetch real-time data ---
def fetch_stock_data(symbol):
    global stock_data
    symbol = symbol.upper().strip()
    if not symbol:
        messagebox.showerror("Error", "Please select a stock symbol!")
        return

    try:
        # Fetch data from yfinance
        stock = yf.Ticker(symbol)
        df = stock.history(period="1y")  

        if df.empty:
            messagebox.showerror("Error", "Invalid stock symbol or no data found!")
            return

        # Store data globally for tooltips
        stock_data = df

        # Update KPI values with rupee symbol
        kpi_close.config(text=f"₹{df['Close'].iloc[-1]:.2f}")
        kpi_high.config(text=f"₹{df['High'].max():.2f}")
        kpi_low.config(text=f"₹{df['Low'].min():.2f}")

        # Update the charts
        update_graphs(df, symbol)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")

# --- Chart Update Functions ---
def update_sales_by_year(ax, df):
    # Make sure you have actual yearly data to display
    yearly_sales = df.groupby(df.index.year)['Close'].sum()
    
    # Convert index to integers for proper display
    yearly_sales.index = yearly_sales.index.astype(int)
    
    # Use a colormap to create a gradient of colors
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(yearly_sales)))
    
    # Plot the data with proper year formatting
    ax.bar(yearly_sales.index, yearly_sales.values, color=colors)
    ax.set_title("Sales by Year", fontname='Segoe UI', fontweight='bold')
    
    # Make sure x-axis shows all years clearly
    ax.set_xticks(yearly_sales.index)
    ax.set_xticklabels(yearly_sales.index, rotation=45)
    
    # Format y-axis for better readability
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))


def update_profit_by_category(ax, df):
    categories = df['Close'].diff().apply(lambda x: 'Profit' if x > 0 else 'Loss').value_counts()
    ax.pie(categories, labels=categories.index, autopct="%1.1f%%", startangle=140,
           colors=[chart_colors[1], chart_colors[0]])  # Teal for profit, Red for loss
    ax.set_title("Profit & Loss Distribution", fontname='Segoe UI', fontweight='bold', color=text_color)

def update_sales_profit_by_order_date(ax, df):
    ax.plot(df.index, df['Close'], label="Sales", color=chart_colors[2])  # Yellow
    ax.scatter(df.index, df['Close'].pct_change() * 100, label="Profit (%)", s=10, color=chart_colors[4])  # Pink
    ax.set_title("Sales and Profit by Date", fontname='Segoe UI', fontweight='bold', color=text_color)
    ax.legend()
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45)

def update_sales_by_ship_mode(ax, df):
    # Calculate monthly volume changes 
    monthly_volume = df['Volume'].resample('M').sum()
    monthly_volume_change = monthly_volume.pct_change() * 100
    
    # Create a colorful bar chart with gradient colors
    months = monthly_volume_change.index.strftime('%b')
    colors = plt.cm.rainbow(np.linspace(0, 1, len(months)))
    
    ax.bar(months, monthly_volume_change.values, color=colors)
    ax.set_title("Monthly Volume Change (%)", fontname='Segoe UI', fontweight='bold', color=text_color)
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    plt.xticks(rotation=45)

# --- Option 1 Chart Functions ---
def update_option1_chart1(ax, df):
    ax.plot(df.index, df['Close'].rolling(window=7).mean(), label="7-Day MA", color=chart_colors[0], linewidth=2)
    # Add a light area under the curve for visual appeal
    ax.fill_between(df.index, df['Close'].rolling(window=7).mean(), alpha=0.2, color=chart_colors[0])
    ax.set_title("7-Day Moving Average", fontname='Segoe UI', fontweight='bold', color=text_color)
    ax.legend()

def update_option1_chart2(ax, df):
    # Create a colorful gradient volume chart
    dates = mdates.date2num(df.index.to_pydatetime())
    colors = plt.cm.cool(np.linspace(0, 1, len(dates)))
    
    for i in range(len(dates)-1):
        ax.bar(df.index[i], df['Volume'].values[i], color=colors[i], width=1.0)
    
    ax.set_title("Volume Traded", fontname='Segoe UI', fontweight='bold', color=text_color)

# --- Option 2 Chart Functions ---
def update_option2_chart1(ax, df):
    ax.plot(df.index, df['High'], label="Daily High", color=chart_colors[1], linewidth=2)
    ax.plot(df.index, df['Low'], label="Daily Low", color=chart_colors[0], linewidth=2)
    # Fill the area between high and low for a more colorful visual
    ax.fill_between(df.index, df['High'], df['Low'], alpha=0.2, color=chart_colors[5])
    ax.set_title("Daily High & Low", fontname='Segoe UI', fontweight='bold', color=text_color)
    ax.legend()

def update_option2_chart2(ax, df):
    daily_returns = df['Close'].pct_change() * 100
    # Use a gradient colormap for histogram
    n, bins, patches = ax.hist(daily_returns, bins=30, edgecolor='white', alpha=0.8)
    
    # Set color for each bar based on its position
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    col = plt.cm.viridis(np.linspace(0, 1, len(patches)))
    for c, p in zip(col, patches):
        plt.setp(p, 'facecolor', c)
    
    ax.set_title("Distribution of Daily Returns", fontname='Segoe UI', fontweight='bold', color=text_color)

# --- Update graphs function ---
def update_graphs(df, symbol):
    global annotations
    
    # Clear any previous annotations
    for ann in annotations:
        try:
            ann.remove()
        except:
            pass
    annotations = []
    
    for ax in axes.flatten():
        ax.clear()
        ax.set_facecolor(chart_bg_color)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("#CBD5E1")  # Light gray for axes
        ax.spines["left"].set_color("#CBD5E1")
        ax.tick_params(axis='both', colors=text_color, labelsize=10)
        ax.grid(color='#E2E8F0', linestyle='-', linewidth=0.5, alpha=0.7)  # Lighter grid

    # Get current selected view
    current_view = radio_var.get()
    
    # Add graph titles and update content
    if current_view == 1:
        update_option1_chart1(axes[0, 0], df)
        update_option1_chart2(axes[0, 1], df)
        update_sales_profit_by_order_date(axes[1, 0], df) 
        update_sales_by_ship_mode(axes[1, 1], df)    
        
        # Update graph title labels with new colors
        title_labels[(0, 0)].config(foreground=chart_colors[0])
        title_labels[(0, 1)].config(foreground=chart_colors[5])
        title_labels[(1, 0)].config(foreground=chart_colors[2])
        title_labels[(1, 1)].config(foreground=chart_colors[3])
          
    elif current_view == 2:
        update_option2_chart1(axes[0, 0], df)
        update_option2_chart2(axes[0, 1], df)
        update_sales_by_year(axes[1, 0], df)          
        update_profit_by_category(axes[1, 1], df)
        
        # Update graph title labels with new colors
        title_labels[(0, 0)].config(foreground=chart_colors[1])
        title_labels[(0, 1)].config(foreground=chart_colors[4])
        title_labels[(1, 0)].config(foreground=chart_colors[3])
        title_labels[(1, 1)].config(foreground=chart_colors[2])
    
    # Update graph title content
    for pos, title in graph_titles[current_view].items():
        title_labels[pos].config(text=title)
    
    fig.suptitle(f"{symbol} Stock Analysis", fontsize=16, fontweight='bold', color=primary_color, fontname='Segoe UI')
    
    # Fix for graph resizing issue
    fig.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for the suptitle
    plt.subplots_adjust(wspace=0.3, hspace=0.3)  # Add consistent spacing between subplots
    
    canvas_plot.draw()

# --- Matplotlib Setup ---
plt.style.use('default')  # Use light background style
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.tight_layout(pad=4.0)
fig.set_facecolor(chart_bg_color)

canvas_plot = FigureCanvasTkAgg(fig, master=graph_frame)
canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --- Mouse hover event handling ---
def hover(event):
    if event.inaxes is None:
        # Mouse not over any axis
        tooltip_label.config(text="")
        return
    
    if stock_data is None:
        return
        
    # Find which subplot the mouse is over
    for i in range(2):
        for j in range(2):
            if event.inaxes == axes[i, j]:
                current_ax = (i, j)
                break
        else:
            continue
        break
    
    view_mode = radio_var.get()
    chart_title = graph_titles[view_mode][current_ax]
    
    # Get x and y data values
    x, y = event.xdata, event.ydata
    
    # Format the tooltip based on chart type
    if view_mode == 1:  # Standard View
        if current_ax == (0, 0):  # 7-Day Moving Average
            # Find closest date point
            dates = list(stock_data.index)
            closest_date_idx = min(range(len(dates)), key=lambda i: abs(mdates.date2num(dates[i]) - x))
            closest_date = dates[closest_date_idx]
            ma_value = stock_data['Close'].rolling(window=7).mean()[closest_date]
            tooltip_text = f"Date: {closest_date.strftime('%Y-%m-%d')}\nMA(7): ₹{ma_value:.2f}"
            
        elif current_ax == (0, 1):  # Volume Traded
            # Find closest date point
            dates = list(stock_data.index)
            closest_date_idx = min(range(len(dates)), key=lambda i: abs(mdates.date2num(dates[i]) - x))
            closest_date = dates[closest_date_idx]
            volume = stock_data['Volume'][closest_date]
            tooltip_text = f"Date: {closest_date.strftime('%Y-%m-%d')}\nVolume: {volume:,.0f} shares"
            
        elif current_ax == (1, 0):  # Sales and Profit by Date
            # Find closest date point
            dates = list(stock_data.index)
            closest_date_idx = min(range(len(dates)), key=lambda i: abs(mdates.date2num(dates[i]) - x))
            closest_date = dates[closest_date_idx]
            close = stock_data['Close'][closest_date]
            change = stock_data['Close'].pct_change()[closest_date] * 100 if closest_date_idx > 0 else 0
            tooltip_text = f"Date: {closest_date.strftime('%Y-%m-%d')}\nClose: ₹{close:.2f}\nChange: {change:.2f}%"
            
        elif current_ax == (1, 1):  # Monthly Volume Change
            monthly_volume = stock_data['Volume'].resample('M').sum()
            monthly_volume_change = monthly_volume.pct_change() * 100
            
            # Find closest month
            months = list(range(len(monthly_volume_change)))
            closest_month_idx = min(range(len(months)), key=lambda i: abs(i - x) if i < len(monthly_volume_change) else float('inf'))
            
            if closest_month_idx < len(monthly_volume_change):
                month_date = monthly_volume_change.index[closest_month_idx]
                change_value = monthly_volume_change.iloc[closest_month_idx]
                tooltip_text = f"Month: {month_date.strftime('%b %Y')}\nVolume Change: {change_value:.2f}%\nBase Volume: {monthly_volume.iloc[closest_month_idx]:,.0f} shares"
            else:
                tooltip_text = "No data available"
    
    elif view_mode == 2:  # Technical View
        if current_ax == (0, 0):  # Daily High & Low
            # Find closest date point
            dates = list(stock_data.index)
            closest_date_idx = min(range(len(dates)), key=lambda i: abs(mdates.date2num(dates[i]) - x))
            closest_date = dates[closest_date_idx]
            high = stock_data['High'][closest_date]
            low = stock_data['Low'][closest_date]
            tooltip_text = f"Date: {closest_date.strftime('%Y-%m-%d')}\nHigh: ₹{high:.2f}\nLow: ₹{low:.2f}"
            
        elif current_ax == (0, 1):  # Distribution of Daily Returns
            tooltip_text = f"Return: {x:.2f}%\nFrequency: {y:.0f}"
            
        elif current_ax == (1, 0):  # Sales by Year
            # Convert x to int for year
            year = int(x)
            yearly_sales = stock_data['Close'].resample('Y').sum()
            year_values = yearly_sales.index.year
            
            if year in year_values:
                year_idx = list(year_values).index(year)
                value = yearly_sales.iloc[year_idx]
                tooltip_text = f"Year: {year}\nTotal: ₹{value:.2f}"
            else:
                tooltip_text = "No data available"
                
        elif current_ax == (1, 1):  # Profit & Loss Distribution
            # Pie chart has special handling
            tooltip_text = "Profit & Loss Distribution"
            # Getting data for angles
            categories = stock_data['Close'].diff().apply(lambda x: 'Profit' if x > 0 else 'Loss').value_counts()
            profit_pct = (categories.get('Profit', 0) / categories.sum()) * 100
            loss_pct = (categories.get('Loss', 0) / categories.sum()) * 100
            tooltip_text = f"Profit Days: {profit_pct:.1f}%\nLoss Days: {loss_pct:.1f}%"
    
    tooltip_label.config(text=tooltip_text)

# Connect the hover event
canvas_plot.mpl_connect('motion_notify_event', hover)

# --- Menu Bar ---
menubar = Menu(root, bg="#FFFFFF", fg=text_color, activebackground=accent_color, activeforeground="#FFFFFF")
filemenu = Menu(menubar, tearoff=0, bg="#FFFFFF", fg=text_color, 
               activebackground=accent_color, activeforeground="#FFFFFF")
filemenu.add_command(label="New Analysis")
filemenu.add_command(label="Save Report")
filemenu.add_command(label="Export Data")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

viewmenu = Menu(menubar, tearoff=0, bg="#FFFFFF", fg=text_color, 
               activebackground=accent_color, activeforeground="#FFFFFF")
menubar.add_cascade(label="View", menu=viewmenu)

helpmenu = Menu(menubar, tearoff=0, bg="#FFFFFF", fg=text_color, 
               activebackground=accent_color, activeforeground="#FFFFFF")
helpmenu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Banking Analytics Dashboard\nVersion 2.0\nColorful Edition"))
helpmenu.add_command(label="Documentation")
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)

# --- Footer with colorful styling ---
footer_frame = ttk.Frame(content_area, padding=(5, 15, 5, 5))
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

footer_text = ttk.Label(footer_frame, text="© 2025 Financial Analytics Dashboard - Colorful Edition", 
                        font=("Segoe UI", 10), foreground=primary_color)
footer_text.pack(side=tk.RIGHT)

# --- Add color theme selector ---
theme_frame = ttk.Frame(left_sidebar, padding=(10, 5, 10, 5), style="Sidebar.TFrame")
theme_frame.pack(fill=tk.X, pady=10)

ttk.Label(theme_frame, text="Color Theme:", style="Sidebar.TLabel").pack(anchor='w')

# Color themes dictionary
color_themes = {
    "Vibrant": {
        "primary": "#4B0082",  # Indigo
        "accent": "#FF7F50",   # Coral
        "charts": ["#FF6B6B", "#4ECDC4", "#FFD166", "#6A0572", "#F72585", "#4CC9F0"]
    },
    "Ocean": {
        "primary": "#023E8A",  # Deep blue
        "accent": "#0077B6",   # Medium blue
        "charts": ["#03045E", "#0077B6", "#00B4D8", "#90E0EF", "#CAF0F8", "#48CAE4"]
    },
    "Sunset": {
        "primary": "#6A040F",  # Dark burgundy
        "accent": "#D00000",   # Bright red
        "charts": ["#D00000", "#E85D04", "#FAA307", "#FFBA08", "#DC2F02", "#9D0208"]
    },
    "Forest": {
        "primary": "#1B4332",  # Dark green
        "accent": "#40916C",   # Medium green
        "charts": ["#081C15", "#1B4332", "#2D6A4F", "#40916C", "#52B788", "#74C69D"]
    }
}

def change_color_theme():
    selected_theme = theme_var.get()
    theme_colors = color_themes[selected_theme]
    
    # Update global color variables
    global primary_color, accent_color, chart_colors
    primary_color = theme_colors["primary"]
    accent_color = theme_colors["accent"]
    chart_colors = theme_colors["charts"]
    
    # Update styles
    style.configure("TLabel.Heading", foreground=primary_color)
    style.configure("Sidebar.Heading.TLabel", foreground=primary_color)
    style.configure("TButton", background=accent_color)
    style.map("TButton", background=[('pressed', '!disabled', accent_color), ('active', accent_color)])
    
    # Update menu colors
    menubar.config(activebackground=accent_color)
    for menu in [filemenu, viewmenu, helpmenu]:
        menu.config(activebackground=accent_color)
    
    # Update footer
    footer_text.config(foreground=primary_color)
    
    # Update graph title colors
    view_mode = radio_var.get()
    if view_mode == 1:
        title_labels[(0, 0)].config(foreground=chart_colors[0])
        title_labels[(0, 1)].config(foreground=chart_colors[1])
        title_labels[(1, 0)].config(foreground=chart_colors[2])
        title_labels[(1, 1)].config(foreground=chart_colors[3])
    else:
        title_labels[(0, 0)].config(foreground=chart_colors[0])
        title_labels[(0, 1)].config(foreground=chart_colors[1])
        title_labels[(1, 0)].config(foreground=chart_colors[2])
        title_labels[(1, 1)].config(foreground=chart_colors[3])
    
    # Update KPI colors
    kpi_close.config(foreground=chart_colors[0])
    kpi_high.config(foreground=chart_colors[1])
    kpi_low.config(foreground=chart_colors[2])
    
    # Refresh graphs if data is available
    if symbol_var.get() and stock_data is not None:
        fetch_stock_data(symbol_var.get())
    
    # Update main title
    title_label.config(foreground=primary_color)

theme_var = tk.StringVar(value="Vibrant")
theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, values=list(color_themes.keys()), state="readonly")
theme_combo.pack(fill=tk.X, pady=(5, 0))
theme_combo.bind("<<ComboboxSelected>>", lambda _: change_color_theme())

# Initialize the layout without auto-fetching data
root.mainloop()