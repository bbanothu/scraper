# Ziggi Bot - Pokémon TCG Drop Tracker 🤖

Ultimate Pokémon TCG order tracking bot that monitors your email for order confirmations, tracks order status, and calculates profit projections based on eBay sold listings.

## Features

- 📧 **Email Integration**: Automatically fetches order emails from Gmail
- 📊 **Order Tracking**: Tracks orders across multiple retailers (Pokemon Center, Target, Walmart, Best Buy)
- 📈 **Analytics Dashboard**: Visual stats, charts, and metrics
- 💰 **Profit Calculator**: Projects profits based on eBay sold listings
- 🎨 **Pokémon Themed UI**: Beautiful Streamlit interface with Pokémon GIFs

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Gmail account with 2-factor authentication enabled
- Gmail App Password (see below)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Gmail App Password

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Enable **2-Factor Authentication** if not already enabled
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate a new app password for "Mail"
5. Copy the 16-character password

### 4. Set Environment Variables

Create a `.env` file in the root directory:

```bash
# .env
EMAIL=yourgmail@gmail.com
PASSWORD=your_16_character_app_password
```

**Important**: Never commit your `.env` file to git! It's already in `.gitignore`.

### 5. Run the Application

**Option 1: Using the run script (recommended)**
```bash
./run.sh
```

**Option 2: Manual run**
```bash
streamlit run scraper/app.py
```

The app will open in your browser at `http://localhost:8501`

## Configuration

### Tracked Retailers

The app monitors emails from:
- `pokemoncenter.com`
- `target.com`
- `walmart.com`
- `bestbuy.com`

You can modify the `SITES` list in `scraper/app.py` to add or remove retailers.

### Product Images

Update the `PRODUCT_IMAGES` dictionary in `scraper/app.py` with your tracked items and their image URLs.

## Usage

1. **Set Date Range**: Use the sidebar slider to set how many days back to search for emails
2. **Refresh Data**: Click "Refresh Data 🔥" to fetch the latest emails
3. **View Stats**: Check the "Stats Arena" tab for order statistics
4. **Item Details**: View individual item stats in the "Item Dex" tab
5. **Order Log**: See all orders in the "Order Log" tab
6. **Profit Analysis**: Check projected profits in the "Profit Calc" tab

## Troubleshooting

### "Error fetching emails"

- Verify your Gmail credentials in `.env`
- Ensure 2-factor authentication is enabled
- Check that you're using an App Password, not your regular password
- Verify IMAP is enabled in your Gmail settings

### "No orders detected"

- Increase the "Days Back to Search" slider
- Check that order emails are in your inbox
- Verify the sender email addresses match the tracked sites
- The regex patterns may need adjustment for your specific email format

### eBay Price Fetching Issues

- eBay may rate-limit requests
- Check your internet connection
- The eBay scraping is based on HTML parsing and may break if eBay changes their structure

## Project Structure

```
zach/
├── scraper/
│   └── app.py          # Main Streamlit application
├── requirements.txt    # Python dependencies
├── run.sh             # Quick start script
├── .env               # Environment variables (not in git)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Notes

- Email parsing uses regex patterns that may need adjustment for different email formats
- eBay price fetching scrapes HTML and may need updates if eBay changes their site structure
- The app caches email data for 1 hour to reduce API calls
- All sensitive credentials should be stored in `.env` file

## License

This project is for personal use. Make sure to comply with Gmail's Terms of Service and eBay's Terms of Service when using this application.
