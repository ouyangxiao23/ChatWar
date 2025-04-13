"""
AI Military Instruction Parser
Modules aligned with your folder structure capabilities
"""
import json
import re
import concurrent.futures
import requests
import os
from typing import List, Dict, Optional


# Configuration aligned with multiple technical domains
class Config:
    API_KEY = "sk-a2pYayG2h8awHnD15lcawU6VbbpGZAxR1ZPIMRR8NqrF3YhN"
    API_ENDPOINT = "https://api.hunyuan.cloud.tencent.com/v1/chat/completions"
    MAX_WORKERS = 10  # Multi-threading for parallel processing
    RATE_LIMIT = 0.3  # Seconds between requests
    RETRY_ATTEMPTS = 3
    DEFAULT_LANGUAGE = "swahili"
    CONFIG_DIR = "config"


# Language-specific prompt templates
class LanguageConfig:
    @staticmethod
    def load_prompt_template(language: str) -> Optional[str]:
        """Load prompt template from config file for the specified language"""
        config_path = os.path.join(Config.CONFIG_DIR, f"{language.lower()}_prompt.txt")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    @staticmethod
    def get_default_prompt_templates():
        """Return default prompt templates for all supported languages"""
        return {
            "swahili": """Combine capabilities from your folders to analyze:
{text}

Output JSON with structure:
{{
  "text": "{text}",
  "orders": [
    {{
      "unit": "extracted_unit",
      "action": "move|attack|NONE",
      "parameters": {{
        "x": "x_coord",
        "y": "y_coord"
      }} | null
    }}
  ]
}}

example1:
    {{
        "text": "Kikosi Alpha zi-nende 2,2 wakati wa mvua",
        "orders": [
        {{
            "unit": "Alpha",
            "action": "move",
            "parameters": ["2","2"]
        }}
        ]
    }}
example2:
    {{
        "text": "lakini Kikosi Alpha na Beta zili-shambulia 5,2",
        "orders": [
          {{
            "unit": "Alpha",
            "action": "attack",
            "parameters": {{
              "x": "5",
              "y": "2"
            }}
          }},
          {{
            "unit": "Beta",
            "action": "attack",
            "parameters": {{
              "x": "5",
              "y": "2"
            }}
          }}
        ]
    }}

Apply techniques from:
- text-classification (military vs civilian)
- token-classification (entity recognition)
- translation (Swahili to structured data)
- question-answering (command extraction)
Only output JSON, no commentary.
""",
            "english": """Combine capabilities from your folders to analyze:
{text}

Output JSON with structure:
{{
  "text": "{text}",
  "orders": [
    {{
      "unit": "extracted_unit",
      "action": "move|attack|NONE",
      "parameters": {{
        "x": "x_coord",
        "y": "y_coord"
      }} | null
    }}
  ]
}}

example1:
    {{
        "text": "Unit Alpha move to 2,2 during the rain",
        "orders": [
        {{
            "unit": "Alpha",
            "action": "move",
            "parameters": ["2","2"]
        }}
        ]
    }}
example2:
    {{
        "text": "but Unit Alpha and Beta attacked 5,2",
        "orders": [
          {{
            "unit": "Alpha",
            "action": "attack",
            "parameters": {{
              "x": "5",
              "y": "2"
            }}
          }},
          {{
            "unit": "Beta",
            "action": "attack",
            "parameters": {{
              "x": "5",
              "y": "2"
            }}
          }}
        ]
    }}

Apply techniques from:
- text-classification (military vs civilian)
- token-classification (entity recognition)
- translation (English to structured data)
- question-answering (command extraction)
Only output JSON, no commentary.
""",
            "hindi": """Combine capabilities from your folders to analyze:
{text}

Output JSON with structure:
{{
  "text": "{text}",
  "orders": [
    {{
      "unit": "extracted_unit",
      "action": "move|attack|NONE",
      "parameters": {{
        "x": "x_coord",
        "y": "y_coord"
      }} | null
    }}
  ]
}}

example1:
    {{
        "text": "Unit Alpha 2,2 par barish ke samay jaaye",
        "orders": [
        {{
            "unit": "Alpha",
            "action": "move",
            "parameters": ["2","2"]
        }}
        ]
    }}
example2:
    {{
        "text": "lekin Unit Alpha aur Beta ne 5,2 par hamla kiya",
        "orders": [
          {{
            "unit": "Alpha",
            "action": "attack",
            "parameters": {{
              "x": "5",
              "y": "2"
            }}
          }},
          {{
            "unit": "Beta",
            "action": "attack",
            "parameters": {{
              "x": "5",
              "y": "2"
            }}
          }}
        ]
    }}

Apply techniques from:
- text-classification (military vs civilian)
- token-classification (entity recognition)
- translation (Hindi in Latin script to structured data)
- question-answering (command extraction)
Only output JSON, no commentary.
"""
        }

    @staticmethod
    def initialize_config_files():
        """Initialize config files for all supported languages if they don't exist"""
        if not os.path.exists(Config.CONFIG_DIR):
            os.makedirs(Config.CONFIG_DIR)
        
        templates = LanguageConfig.get_default_prompt_templates()
        for language, template in templates.items():
            config_path = os.path.join(Config.CONFIG_DIR, f"{language.lower()}_prompt.txt")
            if not os.path.exists(config_path):
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(template)


# Core processing class combining multiple capabilities
class MilitaryInstructionParser:
    def __init__(self, language: str = Config.DEFAULT_LANGUAGE):
        # Initialize config files if they don't exist
        LanguageConfig.initialize_config_files()
        
        # Load the prompt template for the specified language
        self.language = language.lower()
        self.prompt_template = LanguageConfig.load_prompt_template(self.language)
        
        # If language not found, fall back to default language
        if not self.prompt_template:
            print(f"Warning: Prompt template for {language} not found. Falling back to {Config.DEFAULT_LANGUAGE}.")
            self.language = Config.DEFAULT_LANGUAGE
            self.prompt_template = LanguageConfig.load_prompt_template(self.language)
            
            # If still not found, use default templates
            if not self.prompt_template:
                default_templates = LanguageConfig.get_default_prompt_templates()
                self.prompt_template = default_templates.get(self.language, default_templates["swahili"])

    def _clean_response(self, response: str) -> Dict:
        """Robust parsing combining regex and JSON validation"""
        try:
            # First attempt: Direct JSON parse
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: Extract JSON substring
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except Exception:
                    pass
        return {"text": "", "orders": []}

    def process_single(self, text: str) -> Dict:
        """Single text processing with error recovery"""
        headers = {
            "Authorization": f"Bearer {Config.API_KEY}",
            "Content-Type": "application/json"
        }

        for attempt in range(Config.RETRY_ATTEMPTS):
            try:
                response = requests.post(
                    Config.API_ENDPOINT,
                    headers=headers,
                    json={
                        "model": "hunyuan-turbos-latest",
                        "messages": [
                            {"role": "system", "content": f"Military NLP Pipeline for {self.language.capitalize()}"},
                            {"role": "user", "content": self.prompt_template.format(text=text)}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 300
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    return self._clean_response(response.json()['choices'][0]['message']['content'])

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")

        return {"text": text, "orders": []}

    def batch_process(self, texts: List[str]) -> List[Dict]:
        """Multi-threaded batch processing"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
            return list(executor.map(self.process_single, texts))


# Simple test function for process_single
def test_process_single():
    print("Running tests for process_single function...")
    test_cases = {
        "swahili": [
            "Kikosi Alpha ziende 2,2 kwa msaada wa Timu Bravo",
            "Timu Charlie ishambulie 5,7 kabla ya alfajiri"
        ],
        "english": [
            "Unit Alpha move to 2,2 with support from Team Bravo",
            "Team Charlie attack 5,7 before dawn"
        ],
        "hindi": [
            "Unit Alpha 2,2 par jaaye Team Bravo ke saath",
            "Team Charlie 5,7 par hamla kare subah se pehle"
        ]
    }
    
    for language, tests in test_cases.items():
        print(f"\nTesting {language.capitalize()} language:")
        parser = MilitaryInstructionParser(language)
        for i, text in enumerate(tests):
            print(f"  Test {i+1}: {text}")
            result = parser.process_single(text)
            print(f"  Result: {json.dumps(result, ensure_ascii=False)}")
            
            # Basic validation
            if "text" in result and "orders" in result:
                print("  Status: ✓ Valid response format")
            else:
                print("  Status: ✗ Invalid response format")


# Example usage pattern
if __name__ == "__main__":
    # Check if running tests
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--test":
        test_process_single()
        exit(0)
    
    # Sample inputs covering different cases
    inputs = [
        "Kikosi Alpha ziende 2,2 kwa msaada wa Timu Bravo",
        "Hakuna maagizo ya kijeshi kwa sasa",
        "Timu Charlie ishambulie 5,7 kabla ya alfajiri",
        "lakini Kikosi Alpha na Beta zili-shambulia 5,2",
        "Timu Bravo i-eneo 6,7 kwa mazoeziTimu Alpha i-shambulie 2,9 kwa dharura",
        "Vifaa vya jeshi vimepungua, na Timu Beta inahitaji msaada wa haraka kabla ya kufanya hatua.",
        "Mradi Charlie na Delta walihamisha vifaa kwenda 3,4 kwa ajili ya uendeshaji wa kisasa"
    ]

    # Initialize parser with multi-domain capabilities
    language = Config.DEFAULT_LANGUAGE  # Change this to process a different language
    parser = MilitaryInstructionParser(language)

    # Process with parallel execution
    results = parser.batch_process(inputs)

    # Save comprehensive output
    output_file = f"{language}_military_commands.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Processing completed. Results saved to {output_file}")