"""
Basic Usage Example for pytest-LLM-Validate

This example demonstrates the Fixture API for AI-driven qualitative testing 
using the pytest-llm-validate plugin.

To run this example:
1. Ensure you have an OpenAI API key set in your environment: export OPENAI_API_KEY=your_key_here
2. Run: pytest examples/basic_usage_example.py -v
3. To see LLM evaluation logs: pytest examples/basic_usage_example.py -v -s

Requirements:
- pytest-llm-validate installed
- OpenAI API key configured
"""

import pytest


# =============================================================================
# EXAMPLE 1: Simple function validation
# =============================================================================

def test_greeting_function(llm_eval):
    """Test that our greeting function produces polite output."""
    def greet(name):
        return f"Hello, {name}! It's wonderful to meet you!"
    
    result = greet("Alice")
    
    # Traditional assertions (fast, reliable)
    assert "Alice" in result
    assert "Hello" in result
    
    # LLM evaluation (qualitative assessment)
    tester = llm_eval("The function should return a polite, friendly greeting")
    tester.check(result, label="greeting_politeness")


def test_email_response(llm_eval):
    """Test that our email response generator produces professional content."""
    def generate_response(customer_issue):
        if "refund" in customer_issue.lower():
            return """Dear Valued Customer,

Thank you for contacting us regarding your refund request. We sincerely apologize for any inconvenience you may have experienced.

I have reviewed your account and initiated the refund process. You should expect to see the credit reflected in your account within 3-5 business days.

If you have any other questions or concerns, please don't hesitate to reach out.

Best regards,
Customer Service Team"""
        return "Thank you for your inquiry. We'll get back to you soon."
    
    result = generate_response("I need a refund for my order")
    
    # Basic assertions to ensure function works
    assert "Dear" in result
    assert "refund" in result.lower()
    
    # LLM evaluation for professional quality
    tester = llm_eval("The response should be professional and helpful for customer service")
    tester.check(result, label="email_professionalism")


def test_code_quality(llm_eval):
    """Test that generated code meets quality standards."""
    def fibonacci(n):
        """
        Generate the nth Fibonacci number using iterative approach.
        
        Args:
            n (int): Position in Fibonacci sequence (0-indexed)
            
        Returns:
            int: The nth Fibonacci number
            
        Raises:
            ValueError: If n is negative
        """
        if n < 0:
            raise ValueError("Fibonacci sequence is not defined for negative numbers")
        
        if n <= 1:
            return n
            
        # Use iterative approach for better performance
        prev, curr = 0, 1
        for _ in range(2, n + 1):
            prev, curr = curr, prev + curr
            
        return curr
    
    import inspect
    
    # Verify it works (traditional testing)
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(10) == 55
    
    # Get source code for LLM evaluation
    source_code = inspect.getsource(fibonacci)
    assert "def fibonacci" in source_code  # Basic assertion
    
    # LLM evaluation for code quality
    tester = llm_eval(
        "The code should be clean, well-commented, and follow Python best practices",
        threshold=0.8,  # Higher threshold for code quality
        model="gpt-4o-mini"
    )
    tester.check(source_code, label="code_quality")


# =============================================================================
# EXAMPLE 2: Multiple checks in one test
# =============================================================================

def test_chat_bot_responses(llm_eval):
    """Test multiple chatbot responses using the fixture API."""
    
    # Create a tester for evaluating chatbot responses
    tester = llm_eval(
        "All responses should be helpful, empathetic, and appropriate for the context",
        threshold=0.75
    )
    
    def get_bot_response(user_input):
        """Simulate a chatbot responding to user input."""
        if "sad" in user_input.lower():
            return "I'm sorry to hear you're feeling this way. While I'm just a chatbot, I want you to know that your feelings are valid. Have you considered talking to a mental health professional?"
        elif "help" in user_input.lower():
            return "I'm here to help! Could you tell me more about what you need assistance with? I'll do my best to provide useful information."
        else:
            return "Thank you for sharing that with me. I'm here to listen and help however I can."
    
    # Test different scenarios
    sad_response = get_bot_response("I'm feeling really sad today")
    assert len(sad_response) > 10  # Basic assertion
    tester.check(sad_response, label="emotional_support")
    
    help_response = get_bot_response("I need help with something")
    assert "help" in help_response.lower()  # Basic assertion  
    tester.check(help_response, label="general_help")


def test_content_generation_quality(llm_eval):
    """Test content generation with different criteria."""
    
    def generate_blog_post(topic, audience):
        """Generate a blog post for a given topic and audience."""
        if audience == "technical":
            return f"""# Understanding {topic}: A Technical Deep Dive

## Introduction

In today's rapidly evolving technological landscape, {topic} has emerged as a critical component for modern applications. This article provides a comprehensive technical analysis of {topic}, exploring its architecture, implementation details, and best practices.

## Technical Architecture

The core architecture of {topic} is built on several fundamental principles:

1. **Scalability**: Designed to handle increasing loads efficiently
2. **Reliability**: Fault-tolerant systems that maintain operation
3. **Performance**: Optimized for speed and resource utilization

## Implementation Considerations

When implementing {topic}, developers should consider:

- Proper error handling and logging
- Security best practices and data protection
- Performance monitoring and optimization
- Maintainable and testable code structure

## Conclusion

{topic} represents a significant advancement in our technological capabilities. By understanding its technical foundations and following established best practices, developers can leverage its full potential to build robust, scalable applications.
"""
        else:
            return f"""# {topic}: What You Need to Know

## Why {topic} Matters

{topic} is becoming increasingly important in our daily lives. Whether you're a business owner, student, or just curious about technology, understanding {topic} can help you make better decisions and stay informed about the future.

## The Basics

Think of {topic} as a powerful tool that helps solve complex problems. Just like how a calculator makes math easier, {topic} makes certain tasks more efficient and effective.

## Real-World Benefits

Here are some ways {topic} can make a difference:

- Saves time on routine tasks
- Provides better insights and decision-making
- Creates new opportunities and possibilities
- Improves overall efficiency and productivity

## Getting Started

You don't need to be a technical expert to benefit from {topic}. Start by:

1. Learning the basic concepts
2. Finding practical applications in your field
3. Experimenting with simple tools and examples
4. Connecting with others who share your interest

{topic} is an exciting field with lots of potential. Take your time, stay curious, and don't be afraid to explore!
"""
    
    # Create different testers for different content types
    technical_tester = llm_eval(
        "Content should be technically accurate, well-structured, and appropriate for a technical audience",
        threshold=0.8
    )
    
    general_tester = llm_eval(
        "Content should be accessible, engaging, and easy to understand for a general audience",
        threshold=0.7
    )
    
    # Test technical content
    tech_post = generate_blog_post("Machine Learning", "technical")
    assert "Machine Learning" in tech_post  # Basic assertion
    technical_tester.check(tech_post, label="technical_blog_post")
    
    # Test general audience content
    general_post = generate_blog_post("Artificial Intelligence", "general")
    assert "Artificial Intelligence" in general_post  # Basic assertion
    general_tester.check(general_post, label="general_audience_blog_post")


# =============================================================================
# EXAMPLE 3: Error handling and edge cases
# =============================================================================

def test_error_handling(llm_eval):
    """Test that our function handles errors appropriately."""
    def safe_divide(a, b):
        try:
            if b == 0:
                return "Error: Cannot divide by zero. Please provide a non-zero divisor."
            return f"Result: {a / b}"
        except (TypeError, ValueError) as e:
            return f"Error: Invalid input provided. {str(e)}"
        except Exception as e:
            return f"Unexpected error occurred: {str(e)}"
    
    # Test various error conditions
    results = {
        "zero_division": safe_divide(10, 0),
        "valid_calculation": safe_divide(10, 2),
        "invalid_input": safe_divide("10", "abc"),
    }
    
    # Basic assertions for traditional testing
    assert "Error" in results["zero_division"]
    assert "Result: 5.0" == results["valid_calculation"]
    assert "Error" in results["invalid_input"]
    
    # LLM evaluation for error message quality
    tester = llm_eval("The function should handle errors gracefully and provide helpful error messages")
    tester.check(results, label="error_handling_quality")


# =============================================================================
# EXAMPLE 4: Custom metadata and configuration
# =============================================================================

def test_api_response_format(llm_eval):
    """Test API response formatting with custom metadata."""
    import json
    
    def create_api_response(status_code, data, message=None):
        response = {
            "status_code": status_code,
            "data": data,
            "timestamp": "2024-01-15T10:30:00Z",
            "version": "1.0"
        }
        
        if message:
            response["message"] = message
            
        if status_code >= 400:
            response["error"] = True
            
        return response
    
    # Create a sample API response
    result = create_api_response(
        200,
        {"user_id": 123, "name": "John Doe", "email": "john@example.com"},
        "User retrieved successfully"
    )
    
    # Basic assertions for traditional testing
    assert result["status_code"] == 200
    assert "data" in result
    assert result["data"]["user_id"] == 123
    
    # Convert to properly formatted JSON for LLM evaluation
    json_result = json.dumps(result, indent=2)
    
    # LLM evaluation with custom configuration
    tester = llm_eval(
        "The API response should be properly formatted JSON with appropriate HTTP status codes",
        threshold=0.85,
        rule="output_format",  # Using a specific rule
        project="web_api",
        version="1.0"
    )
    tester.check(json_result, label="api_response_format")


# =============================================================================
# RUN INSTRUCTIONS
# =============================================================================

if __name__ == "__main__":
    print("To run this example:")
    print("1. Set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
    print("2. Run: pytest examples/basic_usage_example.py -v")
    print("3. To see LLM evaluation logs: pytest examples/basic_usage_example.py -v -s")
    print("\nThis will execute all the example tests and show LLM evaluation results.") 