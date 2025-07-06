import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import json
import seaborn as sns

class FearGreedIndexAnalyzer:
    def __init__(self):
        self.data = None
        self.df = None
        
    def fetch_fear_greed_data_primary(self):
        """
        Primary method to fetch Fear & Greed data from CNN
        """
        try:
            url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Successfully fetched data from CNN")
                return data
            else:
                print(f"Primary source failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Primary source error: {str(e)}")
            return None
    
    def fetch_fear_greed_data_alternative(self):
        """
        Alternative method to fetch Fear & Greed data
        """
        try:
            # Alternative API endpoint
            url = "https://api.alternative.me/fng/?limit=365&format=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Successfully fetched data from Alternative.me")
                return self.convert_alternative_format(data)
            else:
                print(f"Alternative source failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Alternative source error: {str(e)}")
            return None
    
    def convert_alternative_format(self, data):
        """
        Convert alternative API format to standard format
        """
        converted_data = {
            'fear_and_greed_historical': {
                'data': []
            }
        }
        
        if 'data' in data:
            for entry in data['data']:
                try:
                    timestamp = int(entry['timestamp']) * 1000  # Convert to milliseconds
                    value = int(entry['value'])
                    converted_data['fear_and_greed_historical']['data'].append([timestamp, value])
                except (KeyError, ValueError) as e:
                    print(f"Error converting entry: {entry}, error: {e}")
                    continue
        
        return converted_data
    
    def debug_data_structure(self, data):
        """
        Debug function to understand data structure
        """
        print("\n🔍 Debugging data structure:")
        print(f"Data type: {type(data)}")
        print(f"Data keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
        
        if isinstance(data, dict) and 'fear_and_greed_historical' in data:
            historical = data['fear_and_greed_historical']
            print(f"Historical data type: {type(historical)}")
            print(f"Historical keys: {historical.keys() if isinstance(historical, dict) else 'Not a dict'}")
            
            if 'data' in historical:
                sample_data = historical['data'][:3] if len(historical['data']) > 3 else historical['data']
                print(f"Sample data entries: {sample_data}")
                for i, entry in enumerate(sample_data):
                    print(f"Entry {i}: {entry} (type: {type(entry)})")
    
    def generate_mock_data(self):
        """
        Generate mock Fear & Greed data for demonstration purposes
        """
        print("⚠️  Generating mock data for demonstration...")
        
        # Create date range for last year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic Fear & Greed values
        np.random.seed(42)  # For reproducible results
        base_trend = np.sin(np.linspace(0, 4*np.pi, len(date_range))) * 15 + 50
        noise = np.random.normal(0, 10, len(date_range))
        values = np.clip(base_trend + noise, 0, 100)
        
        # Create mock data structure
        mock_data = {
            'fear_and_greed_historical': {
                'data': []
            }
        }
        
        for date, value in zip(date_range, values):
            timestamp = int(date.timestamp() * 1000)
            mock_data['fear_and_greed_historical']['data'].append([timestamp, int(value)])
        
        return mock_data
    
    def process_data(self, data):
        """
        Process raw data into pandas DataFrame with improved error handling
        """
        if not data:
            raise ValueError("No data provided")
        
        # Debug data structure
        self.debug_data_structure(data)
        
        fear_greed_data = []
        
        try:
            # Handle different possible data structures
            if 'fear_and_greed_historical' in data and 'data' in data['fear_and_greed_historical']:
                raw_data = data['fear_and_greed_historical']['data']
            elif 'data' in data:
                raw_data = data['data']
            else:
                raise ValueError("Unexpected data structure")
            
            print(f"📊 Processing {len(raw_data)} data points...")
            
            for i, entry in enumerate(raw_data):
                try:
                    # Handle different entry formats
                    if isinstance(entry, list) and len(entry) >= 2:
                        # Format: [timestamp, value]
                        timestamp = entry[0]
                        value = entry[1]
                    elif isinstance(entry, dict):
                        # Handle dictionary format
                        if 'timestamp' in entry and 'value' in entry:
                            timestamp = int(entry['timestamp']) * 1000  # Convert to milliseconds
                            value = int(entry['value'])
                        elif 'x' in entry and 'y' in entry:
                            timestamp = entry['x']
                            value = entry['y']
                        else:
                            print(f"⚠️  Skipping entry {i}: Unknown dict format: {entry}")
                            continue
                    else:
                        print(f"⚠️  Skipping entry {i}: Unknown format: {entry}")
                        continue
                    
                    # Convert timestamp to datetime
                    if timestamp > 1e12:  # Timestamp in milliseconds
                        date = datetime.fromtimestamp(timestamp / 1000)
                    else:  # Timestamp in seconds
                        date = datetime.fromtimestamp(timestamp)
                    
                    sentiment = self.get_sentiment_label(value)
                    fear_greed_data.append({
                        'date': date, 
                        'value': float(value), 
                        'sentiment': sentiment
                    })
                    
                except Exception as e:
                    print(f"⚠️  Error processing entry {i}: {entry}, error: {e}")
                    continue
            
            if not fear_greed_data:
                raise ValueError("No valid data points found")
            
            df = pd.DataFrame(fear_greed_data)
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
            
            # Filter last year's data
            one_year_ago = datetime.now() - timedelta(days=365)
            df = df[df.index >= one_year_ago]
            
            print(f"✅ Successfully processed {len(df)} data points for the last year")
            return df
            
        except Exception as e:
            print(f"❌ Error processing data: {str(e)}")
            raise
    
    def get_sentiment_label(self, value):
        """
        Convert Fear & Greed value to sentiment label
        """
        value = float(value)
        if value < 25:
            return "Extreme Fear"
        elif value < 45:
            return "Fear"
        elif value < 55:
            return "Neutral"
        elif value < 75:
            return "Greed"
        else:
            return "Extreme Greed"
    
    def get_sentiment_color(self, value):
        """
        Get color based on sentiment value
        """
        value = float(value)
        if value < 25:
            return '#8B0000'  # Dark Red
        elif value < 45:
            return '#FF4500'  # Red Orange
        elif value < 55:
            return '#FFD700'  # Gold
        elif value < 75:
            return '#90EE90'  # Light Green
        else:
            return '#006400'  # Dark Green
    
    def create_main_chart(self):
        """
        Create the main Fear & Greed Index chart
        """
        if self.df is None or len(self.df) == 0:
            print("❌ No data available for charting")
            return
            
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Create color map for the line
        colors = [self.get_sentiment_color(val) for val in self.df['value']]
        
        # Plot the main line
        ax.plot(self.df.index, self.df['value'], color='navy', alpha=0.7, linewidth=2, label='Fear & Greed Index')
        
        # Create scatter plot with color coding
        scatter = ax.scatter(self.df.index, self.df['value'], c=colors, s=20, alpha=0.8, edgecolors='white', linewidth=0.5)
        
        # Add sentiment zone backgrounds
        ax.axhspan(0, 25, alpha=0.1, color='red', label='Extreme Fear Zone')
        ax.axhspan(25, 45, alpha=0.1, color='orange', label='Fear Zone')
        ax.axhspan(45, 55, alpha=0.1, color='yellow', label='Neutral Zone')
        ax.axhspan(55, 75, alpha=0.1, color='lightgreen', label='Greed Zone')
        ax.axhspan(75, 100, alpha=0.1, color='green', label='Extreme Greed Zone')
        
        # Add horizontal reference lines
        for y in [25, 45, 55, 75]:
            ax.axhline(y=y, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        
        # Customize the chart
        ax.set_title('CNN Fear & Greed Index - Last 12 Months', fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax.set_ylabel('Fear & Greed Index (0-100)', fontsize=14, fontweight='bold')
        
        # Set y-axis limits and ticks
        ax.set_ylim(0, 100)
        ax.set_yticks(range(0, 101, 10))
        
        # Add current value annotation
        current_value = self.df['value'].iloc[-1]
        current_sentiment = self.get_sentiment_label(current_value)
        current_date = self.df.index[-1]
        
        ax.annotate(f'Current: {current_value:.0f}\n({current_sentiment})',
                   xy=(current_date, current_value),
                   xytext=(20, 20),
                   textcoords='offset points',
                   ha='left',
                   va='bottom',
                   bbox=dict(boxstyle='round,pad=0.8', fc='yellow', alpha=0.8, edgecolor='black'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1', color='black', lw=2),
                   fontsize=12,
                   fontweight='bold')
        
        # Add sentiment labels on the right
        ax.text(1.02, 0.125, 'Extreme\nFear', transform=ax.transAxes, ha='left', va='center', 
                fontsize=10, fontweight='bold', color='darkred')
        ax.text(1.02, 0.35, 'Fear', transform=ax.transAxes, ha='left', va='center', 
                fontsize=10, fontweight='bold', color='red')
        ax.text(1.02, 0.5, 'Neutral', transform=ax.transAxes, ha='left', va='center', 
                fontsize=10, fontweight='bold', color='orange')
        ax.text(1.02, 0.65, 'Greed', transform=ax.transAxes, ha='left', va='center', 
                fontsize=10, fontweight='bold', color='green')
        ax.text(1.02, 0.875, 'Extreme\nGreed', transform=ax.transAxes, ha='left', va='center', 
                fontsize=10, fontweight='bold', color='darkgreen')
        
        # Format x-axis
        ax.tick_params(axis='x', rotation=45, labelsize=10)
        ax.tick_params(axis='y', labelsize=10)
        
        # Add grid
        ax.grid(True, linestyle=':', alpha=0.6)
        
        # Add legend
        ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
        
        plt.tight_layout()
        #plt.show()

        image_name = 'cnn_fear_greed_chart.png'
        plt.savefig(image_name, format='png')
    
    def create_summary_stats(self):
        """
        Display summary statistics
        """
        if self.df is None or len(self.df) == 0:
            print("❌ No data available for summary")
            return
            
        print("\n" + "="*50)
        print("FEAR & GREED INDEX ANALYSIS SUMMARY")
        print("="*50)
        
        current_value = self.df['value'].iloc[-1]
        current_sentiment = self.get_sentiment_label(current_value)
        
        print(f"📊 Current Index Value: {current_value:.1f}")
        print(f"😱 Current Sentiment: {current_sentiment}")
        print(f"📈 12-Month High: {self.df['value'].max():.1f}")
        print(f"📉 12-Month Low: {self.df['value'].min():.1f}")
        print(f"📊 12-Month Average: {self.df['value'].mean():.1f}")
        print(f"📊 Standard Deviation: {self.df['value'].std():.1f}")
        
        # Sentiment distribution
        sentiment_counts = self.df['sentiment'].value_counts()
        print("\n📋 Sentiment Distribution (Last 12 Months):")
        for sentiment, count in sentiment_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"   {sentiment}: {count} days ({percentage:.1f}%)")
        
        print("="*50)
    
    def run_analysis(self):
        """
        Main method to run the complete analysis
        """
        print("🔍 Fetching Fear & Greed Index data...")
        
        # Try multiple data sources
        self.data = self.fetch_fear_greed_data_primary()
        
        if self.data is None:
            print("🔄 Trying alternative data source...")
            self.data = self.fetch_fear_greed_data_alternative()
        
        if self.data is None:
            print("⚠️  All external sources failed, using mock data...")
            self.data = self.generate_mock_data()
        
        try:
            # Process data
            self.df = self.process_data(self.data)
            
            # Create visualizations
            print("📈 Creating Fear & Greed Index chart...")
            self.create_main_chart()
            
            # Display summary
            self.create_summary_stats()
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            print("🔄 Falling back to mock data...")
            self.data = self.generate_mock_data()
            self.df = self.process_data(self.data)
            self.create_main_chart()
            self.create_summary_stats()

# Usage
if __name__ == "__main__":
    # Install required packages:
    # pip install requests pandas matplotlib seaborn numpy
    
    analyzer = FearGreedIndexAnalyzer()
    analyzer.run_analysis()
