from io import BytesIO
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors

def GetGraph(df):

    df['date'] = pd.to_datetime(df['date'])  
    df_aggregated = df.groupby(['date', 'expensename'])['amount'].sum().reset_index()   
    sns.set_theme(style="whitegrid")   
    unique_expenses = df_aggregated['expensename'].unique()   
    palette = sns.color_palette("Set2", n_colors=len(unique_expenses))
    plt.figure(figsize=(12, 8))    
    bars = []
    for i, expense in enumerate(unique_expenses):
        expense_data = df_aggregated[df_aggregated['expensename'] == expense]
        bar = plt.bar(expense_data['date'].astype(str), expense_data['amount'], 
                    label=expense, color=palette[i % len(palette)], width=0.8)
        bars.append(bar)

    
    plt.xlabel('Date', fontsize=14, weight='bold')
    plt.ylabel('Amount', fontsize=14, weight='bold')
    plt.title('Expenses by Date and Category', fontsize=16, weight='bold')

    
    for bar in bars:
        for rect in bar:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2, height + 2, f'{height}', ha='center', va='bottom', fontsize=10)

    
    plt.xticks(rotation=45, ha='right')   
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)    
    plt.legend(title='Expense Category', title_fontsize='13', loc='upper left')   
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer,format="png")
    buffer.seek(0)
    base64image =  base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    return base64image
