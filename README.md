# Target Webapp - PDF Library

This is a standalone FastAPI web application for managing and serving PDF files. It's designed to be protected by the Project WARP DDoS protection system.

## Features

- 📄 Upload PDF files
- 🔍 Search PDF content
- 📥 Download PDFs
- 🗑️ Delete PDFs
- 📊 List all PDFs
- 🎨 Clean web interface

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/sanil0/target-webapp.git
cd target-webapp

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
# Run on localhost:8001
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload

# Run on all interfaces (for EC2)
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

Access the application at: `http://localhost:8001`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage - web interface |
| `/upload` | POST | Upload a PDF file |
| `/list` | GET | List all PDFs |
| `/download/{filename}` | GET | Download a PDF |
| `/search` | GET | Search PDF content |
| `/delete/{filename}` | DELETE | Delete a PDF |

## Usage Examples

```bash
# List all PDFs
curl http://localhost:8001/list

# Search for content
curl "http://localhost:8001/search?query=DDoS"

# Upload a PDF
curl -X POST -F "file=@document.pdf" http://localhost:8001/upload

# Download a PDF
curl http://localhost:8001/download/document.pdf -o document.pdf

# Delete a PDF
curl -X DELETE http://localhost:8001/delete/document.pdf
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t target-webapp:latest .
```

### Run with Docker

```bash
docker run -d \
  --name target-webapp \
  -p 8001:8001 \
  -v webapp_pdfs:/app/pdfs \
  target-webapp:latest
```

## AWS EC2 Deployment

### 1. Launch EC2 Instance
- AMI: Ubuntu 22.04 LTS
- Type: t3.small
- Security Group: Allow port 8001

### 2. Connect and Setup
```bash
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3 python3-pip git

# Clone and run
git clone https://github.com/sanil0/target-webapp.git
cd target-webapp
pip install -r requirements.txt

# Run as background service (optional)
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 > app.log 2>&1 &
```

### 3. For Production (with Supervisor/Systemd)
Create `/etc/systemd/system/webapp.service`:

```ini
[Unit]
Description=Target Webapp Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/target-webapp
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable webapp.service
sudo systemctl start webapp.service
```

## Configuration

### Environment Variables

```bash
# Optional: Set upload directory
export PDF_UPLOAD_DIR=/path/to/pdfs

# Optional: Set file size limit (in MB)
export MAX_FILE_SIZE=50

# Optional: Set log level
export LOG_LEVEL=INFO
```

## Project Structure

```
target-webapp/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── templates/             # HTML templates
│   └── index.html        # Web interface
├── static/               # Static files (CSS, JS)
├── pdfs/                 # PDF storage directory
└── README.md             # This file
```

## Dependencies

- fastapi==0.104.1
- uvicorn==0.24.0
- python-multipart==0.0.6
- aiofiles==23.2.1
- jinja2==3.1.2
- PyPDF2==3.0.1

See `requirements.txt` for complete list and versions.

## Testing

### Health Check
```bash
curl http://localhost:8001/health 2>/dev/null || echo "Service not running"
```

### Performance Test
```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8001/list

# Using curl loop
for i in {1..100}; do curl http://localhost:8001/list > /dev/null; done
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>
```

### Permission Denied
```bash
# Ensure pdfs directory is writable
chmod 755 pdfs/
```

### Module Not Found
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Security Considerations

- ⚠️ This webapp should ALWAYS be deployed behind Project WARP DDoS protection
- Use HTTPS in production (with reverse proxy like nginx)
- Validate all file uploads
- Set appropriate file size limits
- Consider implementing authentication for sensitive deployments

## Integration with Project WARP

This application is designed to work with **Project WARP** DDoS protection:

1. Deploy this webapp on a private/protected instance
2. Configure Project WARP to forward clean traffic to this app
3. Project WARP will handle DDoS detection and mitigation
4. Your webapp receives only legitimate traffic

```
Internet → Project WARP Proxy (8080) → Target Webapp (8001)
```

## License

This project is part of Project WARP. See LICENSE in main project repository.

## Support

For issues or questions:
- Check Project WARP documentation: https://github.com/sanil0/Project_final
- Report issues on GitHub

## Contributing

Contributions welcome! Please ensure:
- Code follows PEP 8
- All tests pass
- Documentation is updated

---

**Made with ❤️ for Project WARP**
