# 🔗 CSV Merger Tool

A powerful web application for merging CSV files with automatic key detection and advanced join operations. Built with Streamlit, inspired by NimbleSET functionality.

## 🚀 Live Demo

[**Try the app here →**](https://csv-merger-tool.streamlit.app/)

## ✨ Features

- 🔍 **Automatic Key Detection** - Smart matching of column names between files
- 🔗 **Multiple Join Types** - Inner, Left, Right, Outer, and Union joins
- 📊 **Real-time Statistics** - See record counts and data insights instantly
- 📁 **Multiple Export Formats** - Download as CSV, Excel, or JSON
- 🎨 **Modern Interface** - Clean, responsive design that works on all devices
- ⚡ **Fast Processing** - Optimized for large CSV files with caching
- 📋 **Flexible Column Selection** - Choose exactly which columns to include
- 📈 **Data Preview** - See your data before and after merging

## 🎯 Use Cases

Perfect for:
- **Data Analysis** - Compare and merge datasets from different sources
- **Database Operations** - Perform SQL-like joins without a database
- **Excel Replacement** - Better than VLOOKUP for complex data merging
- **Data Cleaning** - Combine and deduplicate information
- **Report Generation** - Merge data from multiple CSV exports

## 🛠️ Join Types Explained

| Join Type | Description | Use Case |
|-----------|-------------|----------|
| **Inner Join** | Only records that match in both files | Find common data between sets |
| **Left Join** | All records from left + matching from right | Keep all left data, add right info |
| **Right Join** | All records from right + matching from left | Keep all right data, add left info |
| **Full Outer** | All records from both files | Complete picture with all data |
| **Union** | Simple combination of all records | Stack datasets together |

## 🚀 Quick Start

### Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/csv-merger-streamlit.git
cd csv-merger-streamlit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub account
4. Select your forked repository
5. Set main file path to `app.py`
6. Deploy!

## 📖 How to Use

1. **Upload Files** - Use the sidebar to upload your LEFT and RIGHT CSV files
2. **Auto-detect Keys** - Click "Auto-detect Keys" to find matching columns
3. **Choose Join Type** - Select the type of merge you want to perform
4. **Select Columns** - Pick which columns to include in the final result
5. **Download Results** - Export in your preferred format (CSV, Excel, JSON)

## 🔧 Advanced Features

### Automatic Key Detection
The app intelligently finds matching columns by:
- Exact name matching (case-sensitive)
- Fuzzy matching for similar names
- Prioritizing common key fields (id, key, code, name, email)

### Memory Optimization
- Uses Streamlit's caching for better performance
- Handles large files efficiently
- Shows only preview data to maintain speed

### Error Handling
- Supports different CSV encodings (UTF-8, Latin1)
- Graceful error messages for common issues
- File validation and column name cleaning

## 📊 Sample Data

The app works with any CSV files that have at least one matching column. Common examples:

- **Customer data** from different systems (merge on email or customer_id)
- **Sales data** with product information (merge on product_code)
- **Survey responses** with participant details (merge on participant_id)
- **Financial data** from different sources (merge on account_number)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports & Feature Requests

Found a bug or have a feature request? Please open an issue on GitHub with:
- Clear description of the problem/feature
- Steps to reproduce (for bugs)
- Sample data if applicable
- Screenshots if helpful

## 💡 Technical Details

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **File Handling**: openpyxl for Excel export
- **Deployment**: Streamlit Community Cloud
- **Python**: 3.7+ compatible

## 🔒 Privacy & Security

- All processing happens client-side in your browser
- No data is stored on servers
- Files are processed in memory only
- Perfect for sensitive data that cannot leave your environment

## 📞 Support

- 📧 **Email**: [your-email@domain.com]
- 💬 **Discussions**: Use GitHub Discussions for questions
- 🐛 **Issues**: Report bugs via GitHub Issues
- 📖 **Documentation**: Check the wiki for detailed guides

## 🌟 Acknowledgments

- Inspired by [NimbleSET](http://nimbleset.com/) for set operations
- Built with [Streamlit](https://streamlit.io/) framework
- Data processing powered by [Pandas](https://pandas.pydata.org/)

---

**Made with ❤️ for the data community**

⭐ **Star this repo** if it helped you merge your CSV files!