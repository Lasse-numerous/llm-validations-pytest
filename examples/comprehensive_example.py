"""
Comprehensive Example for pytest-LLM-Validate

This example demonstrates the fixture API and various use cases:
- Fixture API (llm_eval fixture) for multiple checks
- Custom thresholds and models
- Error handling evaluation
- Code quality assessment

To run this example:
1. Set your OpenAI API key: export OPENAI_API_KEY=your_key_here
2. Run: pytest examples/comprehensive_example.py -v -s

Requirements:
- pytest-llm-validate installed  
- OpenAI API key configured
"""

import pytest


# =============================================================================
# FIXTURE API EXAMPLES
# =============================================================================

def test_greeting_message(llm_eval):
    """Test a simple greeting function."""
    def create_greeting(name, time_of_day):
        greetings = {
            "morning": "Good morning",
            "afternoon": "Good afternoon", 
            "evening": "Good evening"
        }
        return f"{greetings.get(time_of_day, 'Hello')}, {name}! I hope you're having a wonderful day."
    
    result = create_greeting("Sarah", "morning")
    
    # Traditional assertions
    assert "Sarah" in result
    assert "morning" in result
    
    # LLM evaluation
    tester = llm_eval("The greeting should be warm, friendly, and professional")
    tester.check(result, label="greeting_message")


def test_customer_service_email(llm_eval):
    """Test customer service email generation."""
    def generate_support_email(issue_type, customer_name):
        if issue_type == "billing":
            return f"""Dear {customer_name},

Thank you for contacting us about your billing inquiry. I understand how important it is to have clarity on your account charges.

I have reviewed your account and will be investigating this matter personally. You can expect a detailed response within 24 hours with either a resolution or a clear explanation of next steps.

In the meantime, please don't hesitate to reach out if you have any other questions or concerns.

Best regards,
Customer Success Team
Email: support@company.com
Phone: 1-800-SUPPORT"""

        return f"Dear {customer_name}, Thank you for your inquiry. We will respond shortly."
    
    result = generate_support_email("billing", "John Smith")
    
    # Traditional assertions
    assert "John Smith" in result
    assert "billing" in result
    
    # LLM evaluation with higher threshold
    tester = llm_eval(
        "The email should be professional, empathetic, and provide clear next steps",
        threshold=0.8  # Higher threshold for important communications
    )
    tester.check(result, label="customer_service_email")


def test_code_quality_assessment(llm_eval):
    """Test code quality using LLM evaluation."""
    def calculate_compound_interest(principal, rate, time, compound_frequency=12):
        """
        Calculate compound interest using the standard formula.
        
        Args:
            principal (float): Initial amount of money
            rate (float): Annual interest rate (as decimal, e.g., 0.05 for 5%)
            time (float): Time period in years
            compound_frequency (int): Number of times interest compounds per year
            
        Returns:
            dict: Contains final amount, interest earned, and calculation details
            
        Raises:
            ValueError: If any input values are invalid
        """
        # Input validation
        if principal <= 0:
            raise ValueError("Principal must be positive")
        if rate < 0:
            raise ValueError("Interest rate cannot be negative") 
        if time < 0:
            raise ValueError("Time period cannot be negative")
        if compound_frequency <= 0:
            raise ValueError("Compound frequency must be positive")
        
        # Calculate compound interest: A = P(1 + r/n)^(nt)
        amount = principal * (1 + rate / compound_frequency) ** (compound_frequency * time)
        interest_earned = amount - principal
        
        return {
            "final_amount": round(amount, 2),
            "interest_earned": round(interest_earned, 2),
            "principal": principal,
            "rate_percent": rate * 100,
            "years": time,
            "compound_frequency": compound_frequency
        }
    
    # Test the function and get source code for evaluation
    import inspect
    
    # Verify it works correctly
    result = calculate_compound_interest(1000, 0.05, 2, 12)
    assert result["final_amount"] > 1000  # Should earn interest
    
    # Get source code for LLM evaluation
    source_code = inspect.getsource(calculate_compound_interest)
    
    # LLM evaluation
    tester = llm_eval("The code should be clean, well-documented, and follow Python best practices")
    tester.check(source_code, label="code_quality")


def test_content_moderation_system(llm_eval):
    """Test a content moderation system with multiple scenarios."""
    
    # Create a tester for content moderation
    tester = llm_eval(
        "Content should be appropriately flagged: safe content allowed, harmful content blocked",
        threshold=0.85
    )
    
    def moderate_content(text):
        """Simple content moderation system."""
        harmful_keywords = ["spam", "scam", "hate", "violence", "abuse"]
        
        text_lower = text.lower()
        flagged_words = [word for word in harmful_keywords if word in text_lower]
        
        if flagged_words:
            return {
                "approved": False,
                "reason": f"Content flagged for: {', '.join(flagged_words)}",
                "flagged_terms": flagged_words,
                "original_text": text
            }
        
        return {
            "approved": True,
            "reason": "Content passed moderation",
            "flagged_terms": [],
            "original_text": text
        }
    
    # Test various content types
    safe_content = moderate_content("This is a great product! I highly recommend it.")
    assert safe_content["approved"] == True
    tester.check(safe_content, label="safe_content")
    
    questionable_content = moderate_content("This is a scam product, don't buy it!")
    assert questionable_content["approved"] == False
    tester.check(questionable_content, label="harmful_content")
    
    neutral_content = moderate_content("The weather is nice today.")
    assert neutral_content["approved"] == True
    tester.check(neutral_content, label="neutral_content")


def test_api_response_validation(llm_eval):
    """Test API response structure and content."""
    
    # Create testers for different aspects
    structure_tester = llm_eval(
        "API responses should have consistent structure with proper HTTP codes and clear data format",
        threshold=0.8
    )
    
    content_tester = llm_eval(
        "API response messages should be clear, helpful, and appropriate for the status",
        threshold=0.75
    )
    
    def create_api_response(status_code, data=None, message=None, error_details=None):
        """Create standardized API response."""
        response = {
            "status": status_code,
            "timestamp": "2024-01-15T10:30:00Z",
            "success": status_code < 400
        }
        
        if data is not None:
            response["data"] = data
            
        if message:
            response["message"] = message
            
        if error_details and status_code >= 400:
            response["error"] = error_details
            
        return response
    
    # Test successful response
    success_response = create_api_response(
        200,
        {"user_id": 123, "username": "john_doe"},
        "User retrieved successfully"
    )
    
    assert success_response["status"] == 200
    assert success_response["success"] == True
    structure_tester.check(success_response, label="success_response_structure")
    content_tester.check(success_response, label="success_response_content")
    
    # Test error response
    error_response = create_api_response(
        404,
        None,
        "User not found",
        {"code": "USER_NOT_FOUND", "details": "No user exists with the provided ID"}
    )
    
    assert error_response["status"] == 404
    assert error_response["success"] == False
    structure_tester.check(error_response, label="error_response_structure")
    content_tester.check(error_response, label="error_response_content")


def test_chatbot_personality(llm_eval):
    """Test chatbot responses for consistent personality and helpfulness."""
    
    # Create a tester for personality consistency
    personality_tester = llm_eval(
        "Chatbot responses should be consistently helpful, friendly, and professional across different contexts",
        threshold=0.8
    )
    
    def chatbot_response(user_message, context="general"):
        """Simulate chatbot with consistent personality."""
        responses = {
            "greeting": "Hello! I'm here to help you today. What can I assist you with?",
            "help": "I'd be happy to help! Could you please provide more details about what you need assistance with?",
            "technical": "I understand you're having a technical issue. Let me help you troubleshoot this step by step.",
            "complaint": "I'm sorry to hear about your experience. I want to make sure we resolve this for you. Can you tell me more about what happened?",
            "general": "Thank you for reaching out! I'm here to assist you with any questions or concerns you might have."
        }
        
        # Simple intent detection
        user_lower = user_message.lower()
        if "hello" in user_lower or "hi" in user_lower:
            return responses["greeting"]
        elif "help" in user_lower:
            return responses["help"]
        elif "error" in user_lower or "bug" in user_lower:
            return responses["technical"]
        elif "complaint" in user_lower or "problem" in user_lower:
            return responses["complaint"]
        else:
            return responses["general"]
    
    # Test different conversation contexts
    greeting_response = chatbot_response("Hello there!")
    assert "Hello" in greeting_response
    personality_tester.check(greeting_response, label="greeting_response")
    
    help_response = chatbot_response("I need help with something")
    assert "help" in help_response.lower()
    personality_tester.check(help_response, label="help_response")
    
    technical_response = chatbot_response("I'm getting an error message")
    assert "technical" in technical_response or "troubleshoot" in technical_response
    personality_tester.check(technical_response, label="technical_response")
    
    # Log summary
    personality_tester.log_summary()


def test_error_handling_quality(llm_eval):
    """Test error handling and message quality."""
    def safe_calculator(operation, a, b):
        """Calculator with comprehensive error handling."""
        try:
            # Type validation
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                return {
                    "success": False,
                    "error": "Invalid input type",
                    "message": "Please provide numeric values only. Both inputs must be numbers."
                }
            
            # Operation validation
            valid_operations = ["+", "-", "*", "/", "**"]
            if operation not in valid_operations:
                return {
                    "success": False,
                    "error": "Invalid operation",
                    "message": f"Operation '{operation}' is not supported. Valid operations: {', '.join(valid_operations)}"
                }
            
            # Special case: division by zero
            if operation == "/" and b == 0:
                return {
                    "success": False,
                    "error": "Division by zero",
                    "message": "Cannot divide by zero. Please use a non-zero divisor."
                }
            
            # Perform calculation
            if operation == "+":
                result = a + b
            elif operation == "-":
                result = a - b
            elif operation == "*":
                result = a * b
            elif operation == "/":
                result = a / b
            elif operation == "**":
                result = a ** b
            
            return {
                "success": True,
                "result": result,
                "message": f"Calculation completed: {a} {operation} {b} = {result}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "Unexpected error",
                "message": f"An unexpected error occurred: {str(e)}. Please try again or contact support if the issue persists."
            }
    
    # Test various error scenarios
    error_tester = llm_eval("Error handling should be graceful with clear, helpful error messages")
    
    # Test valid operation
    valid_result = safe_calculator("+", 10, 5)
    assert valid_result["success"] == True
    error_tester.check(valid_result, label="valid_operation")
    
    # Test division by zero
    zero_div_result = safe_calculator("/", 10, 0)
    assert zero_div_result["success"] == False
    error_tester.check(zero_div_result, label="division_by_zero")
    
    # Test invalid operation
    invalid_op_result = safe_calculator("invalid", 10, 5)
    assert invalid_op_result["success"] == False
    error_tester.check(invalid_op_result, label="invalid_operation")
    
    # Test invalid input type
    invalid_type_result = safe_calculator("+", "10", 5)
    assert invalid_type_result["success"] == False
    error_tester.check(invalid_type_result, label="invalid_input_type")
    
    # Log summary
    error_tester.log_summary()


if __name__ == "__main__":
    print("Comprehensive pytest-LLM-Validate Examples")
    print("==========================================")
    print("Features demonstrated:")
    print("- Fixture API for multiple checks")
    print("- Custom thresholds and models")
    print("- Code quality evaluation")
    print("- Content moderation testing")
    print("- API response validation")
    print("- Chatbot personality testing")
    print("- Error handling assessment")
    print()
    print("To run: pytest examples/comprehensive_example.py -v -s") 