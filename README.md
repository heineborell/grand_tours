# Erdso 2025 - Grand Tours Project
This branch is to work on the grand_tours.db with regression models and other machine learning models.

## Folder Structure

- `data/`: Contains raw `.db` files from race organizers.
- `plots/`: Output plots organized by type (regression, summaries, EDA).
- `reports/`: Meeting slides, summary notes, references about Grand Tours and Strava segments.
- `grand_tours/`: Code and assets from the online repository.

### `src/` - Core Project Code
- `analysis/`: Exploratory data analysis scripts.
- `models/`: Machine learning models (linear, polynomial, multivariate).
- `plotting/`: Utilities for visualizing model results and data segments.
- `preprocessing/`: Scripts to clean and restructure raw database tables.
- `utils/`: Frequently-used helpers (e.g. time converters, constants).

## To Run Files
```bash
python main.py
