# Runu Studio

A professional Flask-based calculator application with a modern, responsive UI. Runu Studio provides server-side calculation processing with real-time result preview.

## Features

✨ **Modern Design**
- Clean, professional dark-themed interface
- Responsive design that works on desktop and mobile
- Smooth animations and transitions
- Gradient accents and modern typography

🧮 **Calculator Features**
- Support for basic arithmetic operations (addition, subtraction, multiplication, division)
- Server-side calculation processing
- Error handling for invalid inputs
- Real-time result display

👤 **User Profile Integration**
- Capture and display user information
- Professional operator badge display
- Timestamp tracking for calculations

## Project Structure

```
flask api/
├── main.py                 # Flask application and routes
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
└── templates/
    ├── index.html         # Main calculator interface
    └── login.html         # Login page (template)
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or extract the project**
   ```bash
   cd "flask api"
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv env
   env\Scripts\activate

   # macOS/Linux
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Main Interface
1. Enter your first and last name in the User Profile section
2. Input two numeric values (Value X and Value Y)
3. Select a mathematical operation from the dropdown
4. Click "Calculate & Process" to submit
5. View the result in the preview panel on the right

### Supported Operations
- **Addition (+)**: X + Y
- **Subtraction (−)**: X − Y
- **Multiplication (×)**: X × Y
- **Division (÷)**: X ÷ Y (with division by zero protection)

## API Endpoints

### GET `/`
Renders the main calculator interface with default values.

**Response**: HTML page with calculator interface

### POST `/data`
Processes calculator input and returns updated interface with results.

**Parameters**:
- `fname` (string): First name
- `lname` (string): Last name
- `num1` (number): First value (X)
- `num2` (number): Second value (Y)
- `operation` (string): Operation type (add, subtract, multiply, divide)

**Response**: HTML page with calculated results

## Configuration

### Environment Variables
Currently, the application runs with default configuration. To customize:

Edit `main.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

- `debug=True`: Enable debug mode for development
- `host='0.0.0.0'`: Make server accessible from any network interface
- `port=5000`: Server port

## Error Handling

The application includes comprehensive error handling:
- **Invalid numeric input**: Returns error message with form pre-filled
- **Division by zero**: Returns "Error: Division by zero" in result
- **Missing required fields**: Form validation with error alerts
- **Server errors**: Graceful error page display (500.html)
- **Page not found**: Custom 404 error page

## Styling

The application uses:
- **Font**: Plus Jakarta Sans (Google Fonts)
- **Color Scheme**: Modern dark theme with indigo/purple gradients
- **Design System**: 
  - Color variables for consistent theming
  - Responsive grid layouts
  - CSS custom properties for maintainability

### CSS Variables
Main CSS variables defined in `<head>`:
```css
--bg-main: #0f172a
--brand-primary: #6366f1
--brand-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%)
--text-primary: #f8fafc
```

## Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Considerations

- Server-side calculation reduces client-side computation
- Optimized CSS with GPU-accelerated animations
- Minimal JavaScript dependencies
- Responsive images and efficient asset loading

## Security

- Input validation on both client and server
- Error messages don't expose sensitive information
- Protection against division by zero
- Type checking for numeric inputs

## Development

### Logging
The application uses Python's logging module:
```python
logger.info("User action")
logger.error("Error message")
```

Check console output for detailed logs during development.

### Code Organization
- Modular route handlers
- Separated business logic in utility functions
- Clear comments and documentation
- Following Flask best practices

## Future Enhancements

- [ ] User authentication system
- [ ] Database integration for history tracking
- [ ] Advanced mathematical operations
- [ ] Export results to CSV/PDF
- [ ] User preferences and themes
- [ ] API-first architecture
- [ ] Unit tests and integration tests

## Troubleshooting

### Application won't start
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check port availability
# If port 5000 is in use, modify main.py to use different port
```

### Styling not loading
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh browser (Ctrl+Shift+R)
- Check browser console for errors

### Calculation errors
- Ensure numeric inputs are valid numbers
- Check JavaScript console for client-side errors
- Check terminal for Flask error logs

## License

This project is provided as-is for educational and professional use.

## Support

For issues or questions, please refer to:
- Flask Documentation: https://flask.palletsprojects.com/
- Python Documentation: https://docs.python.org/3/

---

Built with ❤️ | Runu Studio © 2024
