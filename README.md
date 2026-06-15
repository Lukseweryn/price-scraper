# price-scraper

A Windows tool that monitors product prices on Polish e-commerce sites, stores historical data, and sends a desktop notification when a price changes.

## Features

- Scrapes prices from supported shops using headless Chrome (Selenium)
- Automatically accepts GDPR/RODO cookie consent banners
- Stores price history in a local CSV file with timestamps
- Compares the last two recorded prices per product
- Pops up a Windows notification when a price change is detected

## Supported shops

| Key in config | Shop |
|---|---|
| `cropp` | cropp.com |
| `medicine` | wearmedicine.com |
| `mediaexpert` | mediaexpert.pl |
| `x-kom` | x-kom.pl |
| `empik` | empik.com |

## Requirements

- Windows OS (notifications use the Windows API)
- Python 3.8+
- Google Chrome
- See [requirements.txt](requirements.txt) for Python dependencies

## Setup

### 1. Create a virtual environment

```cmd
py -m venv venv
```

This creates a `venv\` folder inside the project directory with an isolated Python environment.

### 2. Activate the virtual environment

```cmd
venv\Scripts\activate
```

Your prompt will change to show `(venv)` when it is active. To deactivate later, run `deactivate`.

### 3. Install dependencies

```cmd
pip install -r requirements.txt
```

### 4. Generate default config files

Run the script once to create the required JSON and CSV files:

```cmd
python main_script.py
```

This creates:
- `shop_information.json` — list of products to monitor
- `shop_class.json` — CSS class mappings per shop
- `results.csv` — price history log

### 5. Edit `shop_information.json` to add your own products

```json
[
  {
    "url": "https://www.empik.com/product-page-url",
    "shop_name": "empik",
    "product_name": "My Product"
  }
]
```

The `shop_name` must match a key in `shop_class.json`.

### 6. (Optional) Add a new shop to `shop_class.json`

```json
{
  "myshop": ["price-css-class-name"]
}
```

## Running

**Via batch file (recommended):**
```
run_script.bat
```

**Via Python directly:**
```bash
python main_script.py
```

For scheduled monitoring, see the Task Scheduler guide below.

## Scheduling with Windows Task Scheduler

Task Scheduler runs `run_script.bat` automatically on a set interval so prices are checked without manual effort.

### Step-by-step

1. Open **Task Scheduler** — press `Win + S`, type *Task Scheduler*, press Enter.

2. In the right panel click **Create Basic Task...**

3. **Name:** `Price Scraper` (description optional) → click **Next**.

4. **Trigger:** choose how often to check prices (e.g. *Daily*) → click **Next**.
   - Set the start time and recurrence. For multiple checks per day, finish the wizard first, then edit the trigger (see tip below).

5. **Action:** select *Start a program* → click **Next**.

6. Fill in the program details:
   | Field | Value |
   |---|---|
   | Program/script | Full path to `run_script.bat`, e.g. `C:\Users\YourName\price-scraper\run_script.bat` |
   | Start in (optional) | Same folder, e.g. `C:\Users\YourName\price-scraper` |

7. Click **Next** → **Finish**.

### Run every few hours (optional)

To check prices multiple times a day:

1. In Task Scheduler, find **Price Scraper** in the task list, right-click → **Properties**.
2. Go to the **Triggers** tab → select the trigger → click **Edit**.
3. Expand **Advanced settings** → check **Repeat task every**, set an interval (e.g. `4 hours`) and duration (`Indefinitely`).
4. Click **OK**.

### Tips

- **Run only when logged on** is fine for desktop notifications — the popup needs an active user session.
- To test the task immediately: right-click the task → **Run**.
- If the script fails silently, check `run_script.bat` — it prints an error message on failure, which will appear in a cmd window briefly. Extend the pause at the end of the bat file to read it.

## Project structure

```
price-scraper/
├── main_script.py        # Entry point — orchestrates scraping and alerting
├── web_scraper.py        # Selenium-based scraper (ShopScraper class)
├── file_manager.py       # CSV read/write/merge (FileManager class)
├── price_alert.py        # Price comparison and Windows popup notification
├── fixer.py              # Generates default config files on first run
├── run_script.bat        # Windows batch launcher
├── shop_information.json # Products to monitor (auto-created, gitignored)
├── shop_class.json       # CSS class mappings per shop (auto-created, gitignored)
└── results.csv           # Price history log (auto-created, gitignored)
```

> `*.json` and `*.csv` data files are gitignored. Back them up manually if needed.
