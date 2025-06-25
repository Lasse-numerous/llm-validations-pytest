"""
Logging Example for pytest-LLM-Validate

This example demonstrates how to inspect LLM evaluation results using logging
with the fixture API.

To run this example with logging:
1. Ensure you have an OpenAI API key set in your environment: export OPENAI_API_KEY=your_key_here
2. Run with verbose logging: pytest examples/logging_example.py -v -s
3. Or run with debug logging: pytest examples/logging_example.py -vv -s
4. Or set log level via environment: PYTEST_LLM_VALIDATE_LOG_LEVEL=DEBUG pytest examples/logging_example.py -s

The -s flag is important to see the log output in real-time.
"""

import pytest


def test_greeting_with_logging(llm_eval):
    """Test with logging to see LLM evaluation results."""
    def create_greeting(name, time_of_day):
        return f"Good {time_of_day}, {name}! I hope you're having a wonderful day."
    
    result = create_greeting("Sarah", "morning")
    
    # Traditional assertion
    assert "Sarah" in result
    assert "morning" in result
    
    # LLM evaluation with logging
    tester = llm_eval("The greeting should be warm and personalized")
    tester.check(result, label="greeting_warmth")


def test_error_message_quality(llm_eval):
    """Test error message quality with higher threshold."""
    def generate_error_message(error_type):
        if error_type == "validation":
            return "Oops! It looks like some of the information you entered isn't quite right. Please check the highlighted fields and try again."
        elif error_type == "network":
            return "We're having trouble connecting to our servers right now. Please check your internet connection and try again in a moment."
        else:
            return "Something went wrong. Please try again."
    
    result = generate_error_message("validation")
    
    # Traditional assertions
    assert len(result) > 20
    assert "information" in result
    
    # LLM evaluation with higher threshold
    tester = llm_eval("The error message should be helpful and user-friendly", threshold=0.8)
    tester.check(result, label="error_message_quality")


def test_multiple_checks_with_logging(llm_eval):
    """Test multiple outputs with fixture API and logging."""
    
    # Create a tester for email responses
    email_tester = llm_eval(
        "Email responses should be professional, empathetic, and actionable",
        threshold=0.75
    )
    
    def generate_email_response(situation):
        responses = {
            "complaint": """Dear Valued Customer,

Thank you for bringing this matter to our attention. I sincerely apologize for the inconvenience you've experienced, and I want to make this right for you immediately.

I've escalated your case to our senior support team, and you can expect a resolution within 24 hours. In the meantime, I've applied a courtesy credit to your account.

Please don't hesitate to reach out if you have any other concerns.

Best regards,
Customer Support Team""",
            
            "inquiry": """Hello!

Thank you for your inquiry about our services. I'd be happy to help you find the right solution for your needs.

Based on what you've described, I recommend our Premium plan, which includes all the features you mentioned. I've attached a detailed comparison guide and would be glad to schedule a brief call to discuss how this can benefit your specific use case.

Feel free to reply with any questions or let me know a good time to connect.

Best regards,
Sales Team"""
        }
        return responses.get(situation, "Thank you for contacting us. We'll get back to you soon.")
    
    # Test complaint response
    complaint_response = generate_email_response("complaint")
    assert "Dear" in complaint_response  # Traditional assertion
    email_tester.check(complaint_response, label="complaint_handling")
    
    # Test inquiry response  
    inquiry_response = generate_email_response("inquiry")
    assert "inquiry" in inquiry_response.lower()  # Traditional assertion
    email_tester.check(inquiry_response, label="sales_inquiry")
    
    # Log summary of all checks
    email_tester.log_summary()


if __name__ == "__main__":
    print("To run this example with logging visibility:")
    print("1. Set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
    print("2. Run with verbose output: pytest examples/logging_example.py -v -s")
    print("3. Run with debug output: pytest examples/logging_example.py -vv -s")
    print("4. Or set custom log level: PYTEST_LLM_VALIDATE_LOG_LEVEL=DEBUG pytest examples/logging_example.py -s")
    print("\nThe -s flag is important to see log output in real-time!") 