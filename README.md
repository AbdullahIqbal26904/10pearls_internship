# Air Quality Index (AQI) Prediction Dashboard

A Streamlit dashboard that displays historical Air Quality Index (AQI) data and provides a 3-day forecast of AQI values using machine learning models.

![AQI Dashboard Preview](https://via.placeholder.com/800x400?text=AQI+Dashboard+Preview)

## Features

- Historical AQI trends visualization
- 3-day AQI forecast with detailed hourly predictions
- Health implications based on AQI levels
- Interactive charts and intuitive UI
- Detailed information about AQI categories and health impacts

## Prerequisites

- Python 3.8 or higher
- AWS account with S3 access (for data storage)
- AWS credentials configured

## Installation

1. Clone the repository or download the source code:

```bash
git clone <repository-url>
cd 10pearls_internship
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root directory with the following variables:

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

Make sure your AWS user has permissions to access the required S3 buckets:
- `my-feature-store-data/pipeline-data/data.csv` - Historical AQI data
- `my-feature-store-data/predictions/prediction_results.csv` - Prediction results

## Data Format

The dashboard expects the following data formats:

### Historical Data
CSV file with columns:
- `year`, `month`, `day` (or `date`)
- `Calculated_AQI` - Air Quality Index values

### Prediction Data
CSV file with columns:
- `Date` - Date of prediction
- `Predicted_Calculated_AQI` - Predicted AQI values

## Running the Dashboard

To run the AQI dashboard:

```bash
streamlit run aqi_dashboard.py
```

The dashboard will be accessible in your web browser at `http://localhost:8501`.

## Customization

You can modify various aspects of the dashboard:
- Change the data source in the `load_data()` function
- Adjust visualization parameters in the chart creation sections
- Update AQI category thresholds in the `get_aqi_category()` function

## Troubleshooting

If you encounter issues:

1. Ensure AWS credentials are correctly set up in the `.env` file
2. Check that the S3 bucket and data files exist and are accessible
3. Verify your Python environment has all the required dependencies
4. Check the Streamlit logs for detailed error messages

## License

[Specify license information here]

## Contact

Abdullah Iqbal - [Your Contact Information]
