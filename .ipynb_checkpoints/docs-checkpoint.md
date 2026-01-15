# Pydantic Documentation for LLM Output Validation

This documentation provides everything needed to build LLM output validators using Pydantic. All information is extracted from the Pydantic short course materials.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Core Concepts](#core-concepts)
3. [API Reference](#api-reference)
4. [Common Patterns](#common-patterns)
5. [Error Handling](#error-handling)
6. [LLM Integration](#llm-integration)
7. [Examples by Use Case](#examples-by-use-case)

---

## Installation and Setup

### Required Packages

```python
# Install Pydantic and OpenAI
pip install pydantic openai python-dotenv
```

### Basic Imports

```python
from pydantic import BaseModel, ValidationError, Field, EmailStr
from typing import List, Optional, Literal
from datetime import date, datetime
from openai import OpenAI
import json
```

### Initialize OpenAI Client

```python
from openai import OpenAI

client = OpenAI()
# API key loaded from environment variable OPENAI_API_KEY
```

---

## Core Concepts

### What is a Pydantic Model?

A Pydantic model is a Python class that inherits from `BaseModel` and defines:
1. **Field names**: Python variable names (e.g., `title`, `email`)
2. **Field types**: Python types (e.g., `str`, `int`, `float`, `bool`)
3. **Constraints**: Validation rules using `Field()` (e.g., `ge=0`, `min_length=1`)
4. **Optional fields**: Fields that can be `None` using `Optional[type]`

### Basic Model Structure

```python
from pydantic import BaseModel, Field
from typing import Optional

class UserInput(BaseModel):
    name: str                    # Required field
    email: str                   # Required field
    age: int = Field(ge=0)       # Required with constraint
    phone: Optional[str] = None  # Optional field with default
```

### Key Features

1. **Automatic validation**: Data is validated when creating model instances
2. **Type coercion**: Pydantic automatically converts compatible types (e.g., "123" → 123)
3. **Clear error messages**: ValidationError provides detailed field-level errors
4. **JSON support**: Native methods for JSON serialization/deserialization

---

## API Reference

### BaseModel

The base class for all Pydantic models.

```python
from pydantic import BaseModel

class MyModel(BaseModel):
    field1: str
    field2: int
```

**Key Methods:**

1. **`model_validate_json(json_str)`** - Parse and validate JSON string
   ```python
   json_data = '{"field1": "value", "field2": 42}'
   instance = MyModel.model_validate_json(json_data)
   ```

2. **`model_dump_json(indent=None)`** - Serialize model to JSON string
   ```python
   json_output = instance.model_dump_json(indent=2)
   ```

3. **`model_json_schema()`** - Get JSON schema for the model
   ```python
   schema = MyModel.model_json_schema()
   ```

4. **`__init__(**data)`** - Create instance from dictionary
   ```python
   instance = MyModel(field1="value", field2=42)
   # Or with **kwargs unpacking
   data_dict = {"field1": "value", "field2": 42}
   instance = MyModel(**data_dict)
   ```

### Field()

Define field constraints and metadata.

```python
from pydantic import Field

class MyModel(BaseModel):
    # Numeric constraints
    age: int = Field(ge=0, le=120)           # 0 <= age <= 120
    score: float = Field(gt=0.0, lt=100.0)   # 0.0 < score < 100.0

    # String constraints
    name: str = Field(min_length=1, max_length=100)

    # Description for documentation
    email: str = Field(description="User email address")

    # Required field with constraints
    order_id: int = Field(..., ge=10000, le=99999)  # ... means required
```

**Field Parameters:**

- `ge` - Greater than or equal to (numbers)
- `le` - Less than or equal to (numbers)
- `gt` - Greater than (numbers)
- `lt` - Less than (numbers)
- `min_length` - Minimum string/list length
- `max_length` - Maximum string/list length
- `description` - Field documentation
- `...` - Ellipsis indicates required field (when default not provided)

### Special Field Types

#### EmailStr

Validates email address format.

```python
from pydantic import EmailStr

class UserInput(BaseModel):
    email: EmailStr  # Validates email format
```

#### Literal

Restricts field to specific allowed values.

```python
from typing import Literal

class CustomerQuery(BaseModel):
    priority: Literal["low", "medium", "high"]
    category: Literal["refund_request", "information_request", "other"]
```

#### Optional Fields

Fields that can be `None` with a default value.

```python
from typing import Optional
from datetime import date

class UserInput(BaseModel):
    name: str                          # Required
    order_id: Optional[int] = None     # Optional, defaults to None
    purchase_date: Optional[date] = None
```

#### Lists

```python
from typing import List

class CustomerQuery(BaseModel):
    tags: List[str]  # Required list of strings
    # Example: ["support", "refund", "urgent"]
```

### ValidationError

Exception raised when validation fails.

```python
from pydantic import ValidationError

try:
    user = UserInput(name="Joe", email="invalid-email")
except ValidationError as e:
    print(e.errors())  # List of error dictionaries
    # [{'loc': ('email',), 'msg': 'value is not a valid email address', 'type': 'value_error.email'}]
```

**Error Structure:**

Each error is a dictionary with:
- `loc` - Field location (tuple of field names)
- `msg` - Error message
- `type` - Error type identifier

---

## Common Patterns

### Pattern 1: Basic Model Creation and Validation

```python
from pydantic import BaseModel, EmailStr

class UserInput(BaseModel):
    name: str
    email: EmailStr
    query: str

# Create instance from dictionary
user_input = UserInput(
    name="Joe User",
    email="joe.user@example.com",
    query="I forgot my password."
)

print(user_input)
# UserInput(name='Joe User', email='joe.user@example.com', query='I forgot my password.')
```

### Pattern 2: Validation with Error Handling

```python
from pydantic import ValidationError

def validate_user_input(input_data):
    try:
        user_input = UserInput(**input_data)
        print(f"✅ Valid user input created:")
        print(f"{user_input.model_dump_json(indent=2)}")
        return user_input
    except ValidationError as e:
        print(f"❌ Validation error occurred:")
        for error in e.errors():
            print(f"  - {error['loc'][0]}: {error['msg']}")
        return None

# Test with valid data
input_data = {
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I forgot my password."
}
user_input = validate_user_input(input_data)

# Test with invalid data
input_data = {
    "name": "Joe User",
    "email": "not-an-email"  # Missing query field, invalid email
}
user_input = validate_user_input(input_data)
# ❌ Validation error occurred:
#   - email: value is not a valid email address
#   - query: Field required
```

### Pattern 3: Optional Fields with Constraints

```python
from pydantic import Field
from typing import Optional
from datetime import date

class UserInput(BaseModel):
    name: str
    email: EmailStr
    query: str
    order_id: Optional[int] = Field(
        None,
        description="5-digit order number (cannot start with 0)",
        ge=10000,
        le=99999
    )
    purchase_date: Optional[date] = None

# Valid with required fields only
input_data = {
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I forgot my password."
}
user = UserInput(**input_data)
print(user.order_id)  # None

# Valid with all fields
input_data = {
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I need to return my laptop case.",
    "order_id": 12345,
    "purchase_date": "2025-12-31"  # String converted to date
}
user = UserInput(**input_data)
print(user.order_id)  # 12345
```

### Pattern 4: JSON Validation

```python
# JSON string input
json_data = '''
{
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I bought a keyboard and mouse and was overcharged.",
    "order_id": 12345,
    "purchase_date": "2025-12-31"
}
'''

# Parse and validate JSON in one step
user_input = UserInput.model_validate_json(json_data)
print(user_input.model_dump_json(indent=2))
```

### Pattern 5: Model Inheritance

```python
from typing import List, Literal

class UserInput(BaseModel):
    name: str
    email: EmailStr
    query: str
    order_id: Optional[int] = Field(None, ge=10000, le=99999)
    purchase_date: Optional[date] = None

# CustomerQuery inherits all fields from UserInput
class CustomerQuery(UserInput):
    priority: Literal["low", "medium", "high"] = Field(
        ..., description="Priority level"
    )
    category: Literal["refund_request", "information_request", "other"]
    is_complaint: bool
    tags: List[str] = Field(..., description="Relevant keyword tags")

# CustomerQuery has all UserInput fields PLUS the additional fields
query = CustomerQuery(
    name="Joe User",
    email="joe.user@example.com",
    query="I need a refund for my broken monitor.",
    order_id=12345,
    purchase_date="2025-12-31",
    priority="high",
    category="refund_request",
    is_complaint=True,
    tags=["monitor", "refund", "complaint"]
)
```

### Pattern 6: Type Coercion

Pydantic automatically converts compatible types:

```python
# String to integer
input_data = {
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I need help.",
    "order_id": "12345"  # String, not int
}
user = UserInput(**input_data)
print(type(user.order_id))  # <class 'int'>
print(user.order_id)  # 12345

# Integer to string
class TestModel(BaseModel):
    name: str

test = TestModel(name=99999)  # Integer, not string
print(type(test.name))  # <class 'str'>
print(test.name)  # "99999"

# String to date
input_data = {
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I need help.",
    "purchase_date": "2025-12-31"  # String, not date
}
user = UserInput(**input_data)
print(type(user.purchase_date))  # <class 'datetime.date'>
```

### Pattern 7: Extra Fields Handling

By default, Pydantic **ignores** extra fields not defined in the model:

```python
input_data = {
    "name": "Joe User",
    "email": "joe.user@example.com",
    "query": "I need help.",
    "system_message": "logging status...",  # Extra field
    "iteration": 1  # Extra field
}

user = UserInput(**input_data)
print(user.model_dump_json(indent=2))
# {
#   "name": "Joe User",
#   "email": "joe.user@example.com",
#   "query": "I need help.",
#   "order_id": null,
#   "purchase_date": null
# }
# Extra fields are silently ignored
```

---

## Error Handling

### Basic Try/Except Pattern

```python
from pydantic import ValidationError

try:
    user_input = UserInput(**input_data)
    print("✅ Valid input")
except ValidationError as e:
    print("❌ Validation failed")
    print(e)
```

### Detailed Error Inspection

```python
try:
    user_input = UserInput(**input_data)
except ValidationError as e:
    for error in e.errors():
        field = error['loc'][0]      # Field name
        message = error['msg']        # Error message
        error_type = error['type']    # Error type
        print(f"Field '{field}': {message} (type: {error_type})")
```

### Validation Function Pattern

```python
def validate_with_model(data_model, input_data):
    """
    Validate input data against a Pydantic model.

    Returns:
        (validated_data, error_message) tuple
        - If valid: (instance, None)
        - If invalid: (None, error_message)
    """
    try:
        if isinstance(input_data, str):
            # JSON string input
            validated_data = data_model.model_validate_json(input_data)
        else:
            # Dictionary input
            validated_data = data_model(**input_data)

        print("✅ Validation successful!")
        print(validated_data.model_dump_json(indent=2))
        return validated_data, None

    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        error_message = f"Validation failed: {e}"
        return None, error_message
```

---

## LLM Integration

### OpenAI Structured Output API

OpenAI's `beta.chat.completions.parse()` method accepts Pydantic models for structured output:

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class MovieRecommendation(BaseModel):
    title: str
    genre: str
    year: int
    rating: float

# Call OpenAI with structured output
response = client.beta.chat.completions.parse(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "You are a movie recommendation expert."},
        {"role": "user", "content": "Recommend a sci-fi movie."}
    ],
    response_format=MovieRecommendation
)

# Get parsed response (already validated)
recommendation = response.choices[0].message.parsed
print(type(recommendation))  # <class 'MovieRecommendation'>
print(recommendation.model_dump_json(indent=2))
```

### Manual LLM Validation Pattern

If NOT using structured output API, validate LLM responses manually:

```python
def call_llm(prompt, model="gpt-4.1-mini"):
    """Call OpenAI without structured output."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Get LLM response as JSON string
prompt = "Return movie recommendation as JSON with title, genre, year, rating"
llm_response = call_llm(prompt)

# Validate the response
try:
    recommendation = MovieRecommendation.model_validate_json(llm_response)
    print("✅ Valid recommendation:", recommendation.model_dump_json(indent=2))
except ValidationError as e:
    print("❌ Validation error:", e)
```

### Using JSON Schema in Prompts

```python
import json

# Get JSON schema from Pydantic model
schema = json.dumps(MovieRecommendation.model_json_schema(), indent=2)

# Include schema in prompt
prompt = f"""
Recommend a sci-fi movie.

Return your response as JSON matching this schema:
{schema}

Respond ONLY with valid JSON.
"""

response = call_llm(prompt)
recommendation = MovieRecommendation.model_validate_json(response)
```

---

## Examples by Use Case

### Example 1: Movie Recommendation Generator

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from openai import OpenAI

class MovieRecommendation(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    genre: Literal["action", "comedy", "drama", "sci-fi", "thriller", "horror", "romance"]
    year: int = Field(ge=1900, le=2025)
    rating: float = Field(ge=0.0, le=10.0)
    synopsis: str = Field(min_length=10, max_length=500)
    director: Optional[str] = None
    lead_actor: Optional[str] = None
    recommended_for: Optional[Literal["family", "adults", "teens"]] = None

# Use with OpenAI
client = OpenAI()

def get_recommendation(query: str):
    response = client.beta.chat.completions.parse(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a movie recommendation expert."},
            {"role": "user", "content": query}
        ],
        response_format=MovieRecommendation
    )
    return response.choices[0].message.parsed

# Test queries
queries = [
    "Recommend a sci-fi movie for a relaxing weekend",
    "I want an action thriller with a strong female lead",
    "Suggest a comedy suitable for family viewing"
]

for query in queries:
    rec = get_recommendation(query)
    print(f"\nQuery: {query}")
    print(f"✅ {rec.title} ({rec.year}) - {rec.genre}")
    print(f"   Rating: {rec.rating}/10")
    print(f"   {rec.synopsis}")
```

### Example 2: Email Classifier

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class EmailClassification(BaseModel):
    category: Literal["work", "urgent", "personal", "spam", "social"]
    priority: Literal["low", "medium", "high", "critical"]
    summary: str = Field(min_length=10, max_length=200)
    requires_action: bool
    sentiment: Literal["positive", "neutral", "negative"]
    action_items: List[str] = []
    deadline: Optional[str] = None
    sender_type: Optional[Literal["colleague", "client", "friend", "automated"]] = None

def classify_email(email_text: str):
    response = client.beta.chat.completions.parse(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are an email classification assistant."},
            {"role": "user", "content": email_text}
        ],
        response_format=EmailClassification
    )
    return response.choices[0].message.parsed

# Test emails
emails = [
    "Dear team, the quarterly budget meeting is rescheduled to Friday at 3 PM. Please confirm attendance.",
    "URGENT: Server downtime detected. System critical. Immediate action required.",
    "Hi! Just wanted to check in and see how your weekend was. Let's grab coffee soon!"
]

for email in emails:
    classification = classify_email(email)
    print(f"\nEmail: {email[:50]}...")
    print(f"✅ Category: {classification.category}, Priority: {classification.priority}")
    print(f"   Summary: {classification.summary}")
    print(f"   Requires action: {classification.requires_action}")
```

### Example 3: Validation with Retry Logic

```python
def validate_and_print(llm_response, model_class):
    """Validate LLM response and print result."""
    try:
        validated = model_class.model_validate_json(llm_response)
        print("✅ Valid response:")
        print(validated.model_dump_json(indent=2))
        return validated, None
    except ValidationError as e:
        print("❌ Validation error:")
        for error in e.errors():
            print(f"  - {error['loc'][0]}: {error['msg']}")
        return None, str(e)

# Usage
llm_response = call_llm(prompt)
validated_data, error = validate_and_print(llm_response, MovieRecommendation)

if error:
    print("Retrying with error feedback...")
    # Implement retry logic here
```

---

## Summary

### Key Takeaways

1. **Pydantic models** define structure and validation rules for data
2. **BaseModel** is the base class for all Pydantic models
3. **Field()** adds constraints (numeric ranges, string lengths, etc.)
4. **Optional fields** use `Optional[type] = default_value`
5. **Literal** restricts values to specific choices
6. **Type coercion** automatically converts compatible types
7. **ValidationError** provides detailed field-level error information
8. **JSON methods** (`model_validate_json`, `model_dump_json`) handle JSON data
9. **OpenAI integration** uses `response_format` parameter for structured output
10. **Error handling** is essential for robust validation workflows

### Common Field Types Reference

```python
str                                    # String
int                                    # Integer
float                                  # Float
bool                                   # Boolean
date                                   # Date (from datetime)
EmailStr                               # Email (requires email-validator package)
Optional[type]                         # Optional field (can be None)
List[type]                            # List of items
Literal["opt1", "opt2"]               # Specific allowed values
```

### Common Field Constraints

```python
Field(ge=N)              # Greater than or equal to N
Field(le=N)              # Less than or equal to N
Field(gt=N)              # Greater than N
Field(lt=N)              # Less than N
Field(min_length=N)      # Minimum string/list length
Field(max_length=N)      # Maximum string/list length
Field(description="...")  # Documentation string
Field(...)               # Required field (when no default)
```

---

## Additional Resources

- **Pydantic Documentation**: https://docs.pydantic.dev/
- **OpenAI Structured Outputs**: https://platform.openai.com/docs/guides/structured-outputs
- **Python Type Hints**: https://docs.python.org/3/library/typing.html

---

**Generated from Pydantic Short Course Materials**
- Lessons 2-5 notebooks
- VTT transcripts L0-L6
- Course version: Pydantic C1
