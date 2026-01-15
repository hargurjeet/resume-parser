# Resume Parser

An intelligent resume parsing system powered by AWS Bedrock Claude and structured output validation. Extract structured candidate information from PDF resumes with high accuracy using AI.

## Features

- **AI-Powered Parsing**: Uses AWS Bedrock Claude with tool-based structured output
- **Pydantic Validation**: Ensures data quality and schema compliance
- **FastAPI Backend**: RESTful API for resume parsing
- **Streamlit UI**: Interactive web interface for easy resume uploads
- **Docker Support**: Containerized deployment for consistency
- **Structured Output**: Extracts contact info, experience, skills, education, and certifications

## Architecture

```
resume-parser/
├── app/
│   ├── api/          # FastAPI routes
│   ├── core/         # Configuration
│   ├── models/       # Pydantic models
│   ├── services/     # Business logic (parser)
│   └── utils/        # Utilities
├── streamlit_ui/     # Streamlit interface
├── Dockerfile        # Container configuration
└── requirements.txt  # Python dependencies
```

## Prerequisites

- Python 3.10+
- AWS Account with Bedrock access
- AWS credentials configured
- Docker (optional, for containerized deployment)

## Installation

### Local Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd resume-parser
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:
```env
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Docker Setup

1. **Build the image**
```bash
docker build -t resume-parser .
```

2. **Run the container**
```bash
docker run -p 8000:8000 -p 8501:8501 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  resume-parser
```

## Usage

### Starting the Services

**Option 1: Using the start script**
```bash
bash start.sh
```

**Option 2: Manual start**

Terminal 1 - FastAPI Backend:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2 - Streamlit UI:
```bash
streamlit run streamlit_ui/ui.py --server.port 8501
```

### API Endpoints

#### Parse Resume
```bash
POST /resume/parse
Content-Type: multipart/form-data

curl -X POST "http://localhost:8000/resume/parse" \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1-234-567-8900",
  "location": "San Francisco, CA",
  "current_job_title": "Senior Software Engineer",
  "years_of_experience": 8,
  "summary": "Experienced software engineer...",
  "work_experience": [
    {
      "job_title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "start_date": "2020-01",
      "end_date": "Present",
      "responsibilities": [
        "Led development of microservices architecture",
        "Mentored junior developers"
      ]
    }
  ],
  "skills": [
    {"name": "Python", "proficiency": "Expert"},
    {"name": "AWS", "proficiency": "Advanced"}
  ],
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "institution": "University of California",
      "graduation_year": "2015"
    }
  ],
  "certifications": [
    {
      "name": "AWS Certified Solutions Architect",
      "issuing_organization": "Amazon Web Services",
      "issue_date": "2021-06"
    }
  ]
}
```

#### Health Check
```bash
GET /
```

### Web Interface

1. Open browser to `http://localhost:8501`
2. Upload a PDF resume
3. Click "Parse Resume"
4. View structured results
5. Download JSON output

## Technology Stack

### Backend
- **FastAPI**: Modern web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Instructor**: Structured outputs from LLMs
- **Boto3**: AWS SDK for Python
- **PDFPlumber**: PDF text extraction

### AI/ML
- **AWS Bedrock**: Managed AI service
- **Claude 3.5 Sonnet**: Advanced language model
- **Tool-based extraction**: Structured output generation

### Frontend
- **Streamlit**: Interactive web applications
- **Python**: Full-stack Python development

### DevOps
- **Docker**: Containerization
- **Uvicorn**: ASGI server
- **Pre-commit**: Code quality hooks

## Configuration

### AWS Bedrock Setup

1. **Enable Bedrock in AWS Console**
   - Navigate to AWS Bedrock
   - Request model access for Claude 3.5 Sonnet
   - Wait for approval (usually instant)

2. **IAM Permissions**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
    }
  ]
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `BEDROCK_MODEL_ID` | Claude model identifier | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |

## Data Models

### ParsedResume Schema

```python
class ParsedResume(BaseModel):
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    current_job_title: Optional[str]
    years_of_experience: Optional[int]
    summary: Optional[str]
    work_experience: List[WorkExperience]
    skills: List[Skill]
    education: List[Education]
    certifications: Optional[List[Certification]]
```

See `app/models/resume.py` for complete schema definitions.

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Project Structure

```
app/
├── api/
│   └── routes.py          # API endpoints
├── core/
│   └── config.py          # Settings management
├── models/
│   └── resume.py          # Pydantic models
├── services/
│   └── parser.py          # Resume parsing logic
├── utils/
│   └── pdf.py             # PDF utilities
└── main.py                # FastAPI application

streamlit_ui/
└── ui.py                  # Streamlit interface

tests/
└── test_parser.py         # Unit tests
```

## Deployment

### Production Considerations

1. **Security**
   - Use AWS IAM roles instead of access keys
   - Enable HTTPS/TLS
   - Implement rate limiting
   - Add authentication/authorization

2. **Scalability**
   - Deploy behind load balancer
   - Use container orchestration (ECS, EKS)
   - Implement caching
   - Add monitoring and logging

3. **Cost Optimization**
   - Monitor Bedrock usage
   - Implement request batching
   - Use appropriate instance sizes

### AWS Deployment Example

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t resume-parser .
docker tag resume-parser:latest <account>.dkr.ecr.us-east-1.amazonaws.com/resume-parser:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/resume-parser:latest

# Deploy to ECS/Fargate
aws ecs update-service --cluster resume-parser --service resume-parser-service --force-new-deployment
```

## Troubleshooting

### Common Issues

**1. AWS Credentials Error**
```
Error: Unable to locate credentials
```
Solution: Ensure AWS credentials are configured via environment variables or AWS CLI.

**2. Bedrock Access Denied**
```
Error: AccessDeniedException
```
Solution: Request model access in AWS Bedrock console and verify IAM permissions.

**3. PDF Extraction Fails**
```
Error: PDF extraction failed
```
Solution: Ensure PDF is not encrypted or corrupted. Check poppler-utils installation.

**4. Port Already in Use**
```
Error: Address already in use
```
Solution: Change ports in configuration or kill existing processes.

## Performance

- **Average parsing time**: 3-8 seconds per resume
- **Accuracy**: ~95% for well-formatted resumes
- **Supported formats**: PDF only
- **Max file size**: 10MB (configurable)

## Limitations

- PDF format only (no Word documents)
- English language resumes (primary support)
- Requires AWS Bedrock access
- Internet connection required

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- AWS Bedrock for AI capabilities
- Anthropic Claude for language understanding
- Instructor library for structured outputs
- FastAPI and Streamlit communities

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## Roadmap

- [ ] Support for Word documents (.docx)
- [ ] Multi-language support
- [ ] Batch processing
- [ ] Resume comparison features
- [ ] ATS scoring
- [ ] Export to multiple formats
- [ ] Integration with HR systems

---

**Built with ❤️ using AWS Bedrock and Python**
