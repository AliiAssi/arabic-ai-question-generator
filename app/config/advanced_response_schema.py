def get_response_schema(num_mcq_questions=None, num_comprehension_questions=None):
    """Generate JSON schema for the response"""
    schema = {
        "type": "object",
        "properties": {}
    }
    
    required_fields = []
    
    # Add questions schema if MCQ is needed
    if num_mcq_questions is not None or (num_mcq_questions is None and num_comprehension_questions is None):
        required_fields.append("questions")
        schema["properties"]["questions"] = {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["question", "options", "correct_answer"],
                "propertyOrdering": ["question", "options", "correct_answer"],
                "properties": {
                    "question": {"type": "string"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 3,
                        "maxItems": 3
                    },
                    "correct_answer": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 2
                    }
                }
            }
        }
    
    # Add comprehension questions schema if needed
    if num_comprehension_questions is not None or (num_mcq_questions is None and num_comprehension_questions is None):
        required_fields.append("comprehension_questions")
        schema["properties"]["comprehension_questions"] = {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["question", "answer"],
                "propertyOrdering": ["question", "answer"],
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"}
                }
            }
        }
    
    schema["required"] = required_fields
    return schema