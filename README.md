# Multi-Language Military Instruction Parser

This program parses military instructions in multiple languages (Swahili, English, and Hindi) and extracts structured commands.

## Features

- Support for multiple languages via configuration files
- Language-specific templates for improved instruction parsing
- Multi-threaded batch processing
- Simple testing functionality

## Setup

1. Ensure you have the required Python packages:
   ```
   pip install requests
   ```

2. Configuration files will be automatically created in the `config` directory during the first run.

## Usage

### Basic Usage

```python
from language.interpreter import MilitaryInstructionParser

# Initialize parser with the desired language (default is Swahili)
parser = MilitaryInstructionParser("english")  # Options: "swahili", "english", "hindi"

# Process a single military instruction
result = parser.process_single("Unit Alpha move to 2,2 with support from Team Bravo")
print(result)

# Process multiple instructions in batch
inputs = [
    "Unit Alpha move to 2,2 with support from Team Bravo",
    "Team Charlie attack 5,7 before dawn"
]
results = parser.batch_process(inputs)
```

### Command Line Usage

```
# Run with default language (Swahili)
python language/interpreter.py

# Run tests for all supported languages
python language/interpreter.py --test
```

## Customizing Language Templates

You can customize the language templates by editing the files in the `config` directory:
- `swahili_prompt.txt`
- `english_prompt.txt`
- `hindi_prompt.txt`

When adding examples to a language template, ensure that all text is represented in Latin script.

## Output Format

The parser returns JSON objects with the following structure:

```json
{
  "text": "original instruction text",
  "orders": [
    {
      "unit": "extracted unit name",
      "action": "move|attack|NONE",
      "parameters": {
        "x": "x_coordinate",
        "y": "y_coordinate"
      }
    }
  ]
}
```

## Adding New Languages

To add support for a new language:

1. Create a new prompt template file in the `config` directory (e.g., `french_prompt.txt`)
2. Follow the same format as the existing templates
3. Include examples in the target language (using Latin script)
4. Update the test_process_single function in interpreter.py to include test cases for the new language 