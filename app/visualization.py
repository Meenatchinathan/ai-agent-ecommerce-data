import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np

def generate_plot(data, question):
    """Generate base64-encoded plot image from query results"""
    if not data.get('rows') or not data.get('columns'):
        return None
    
    # Check if we have plottable data
    if len(data['columns']) < 2:
        return None
    
    try:
        # Extract data
        x_values = []
        y_values = []
        
        for row in data['rows']:
            # Use first two columns
            x = list(row.values())[0]
            y = list(row.values())[1]
            
            # Try converting to float if possible
            try:
                y = float(y)
            except (TypeError, ValueError):
                pass
                
            x_values.append(str(x))
            y_values.append(y)
        
        # Create plot
        plt.figure(figsize=(10, 6))
        
        if all(isinstance(y, (int, float)) for y in y_values):
            # Numeric data - bar plot
            plt.bar(x_values, y_values)
            plt.ylabel(data['columns'][1])
        else:
            # Non-numeric - just show labels
            plt.bar(x_values, range(len(x_values)))
            plt.yticks([])
        
        plt.xlabel(data['columns'][0])
        plt.title(question[:50] + ('...' if len(question) > 50 else ''))
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Convert to base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception:
        return None