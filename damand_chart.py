import matplotlib.pyplot as plt
import numpy as np

def generate_demand_chart():
    # Days of the week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    # Simulate erratic daily demand from walk-ins/calls (Reactive)
    reactive_demand = [15, 50, 5, 40, 10]
    
    # Simulate smoothed daily demand from a subscription model (Proactive)
    # 120 total gallons per week divided evenly = 24 per day
    subscription_demand = [24, 24, 24, 24, 24]
    
    x = np.arange(len(days))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create the bars
    rects1 = ax.bar(x - width/2, reactive_demand, width, label='Current: Reactive Orders', color='tomato', edgecolor='black')
    rects2 = ax.bar(x + width/2, subscription_demand, width, label='ACA 3: Subscription Orders', color='dodgerblue', edgecolor='black')

    # Add text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Total Gallons Ordered', fontsize=12, fontweight='bold')
    ax.set_title('ACA 3: Demand Leveling (Reactive vs. Subscription Fulfillment)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(days, fontsize=11)
    ax.legend(fontsize=11)
    
    # Add a subtle grid for academic formatting
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Attach a text label above each bar, displaying its height
    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontweight='bold')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    # Save the file
    filename = 'aca3_demand_leveling.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"SUCCESS: '{filename}' has been created! You can now download it and put it in your paper.")

if __name__ == '__main__':
    generate_demand_chart()