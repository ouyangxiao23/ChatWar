#!/usr/bin/env python
"""
Simple test script for the Multi-Language Military Instruction Parser.
This script demonstrates how to use the parser with different languages.
"""
from interpreter import MilitaryInstructionParser
import json

def main():
    print("Multi-Language Military Instruction Parser Test")
    print("==============================================")
    
    # Test instructions for each language
    test_data = {
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
    
    # Test each language
    for language, instructions in test_data.items():
        print(f"\n\nTesting {language.capitalize()} Parser")
        print("-" * (len(language) + 15))
        
        # Initialize parser for this language
        parser = MilitaryInstructionParser(language)
        
        # Process each instruction
        for i, instruction in enumerate(instructions):
            print(f"\nInstruction {i+1}: {instruction}")
            result = parser.process_single(instruction)
            print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Validate result structure
            if not result.get("orders"):
                print("Warning: No orders extracted from instruction")
            
    print("\n\nBatch Processing Test")
    print("--------------------")
    
    # Test batch processing with English
    english_parser = MilitaryInstructionParser("english")
    batch_results = english_parser.batch_process(test_data["english"])
    print(f"Batch processed {len(batch_results)} instructions")
    
    # Save results to file for inspection
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(batch_results, f, indent=2, ensure_ascii=False)
    print("Batch results saved to test_results.json")

if __name__ == "__main__":
    main() 