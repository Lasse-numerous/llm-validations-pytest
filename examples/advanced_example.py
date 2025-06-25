"""
Advanced Example for pytest-LLM-Validate

This example demonstrates advanced usage patterns including:
- Custom thresholds and models
- Multiple evaluation criteria  
- Error handling scenarios
- Complex content validation

To run this example:
1. Set your OpenAI API key: export OPENAI_API_KEY=your_key_here
2. Run: pytest examples/advanced_example.py -v -s
"""

import pytest


def test_content_quality_with_custom_threshold(llm_eval):
    """Test content quality with a higher threshold for stricter evaluation."""
    
    def generate_technical_documentation(feature):
        return f"""# {feature} Implementation Guide

## Overview
{feature} is a powerful feature that enhances user experience through advanced functionality. This guide provides comprehensive implementation details.

## Architecture
The {feature} system is built on a microservices architecture with the following components:
- API Gateway for request routing
- Processing Service for core functionality  
- Database Layer for data persistence
- Caching Layer for performance optimization

## Implementation Steps
1. **Setup**: Configure your development environment
2. **Dependencies**: Install required packages and libraries
3. **Configuration**: Set up configuration files and environment variables
4. **Development**: Implement core functionality following our coding standards
5. **Testing**: Write comprehensive unit and integration tests
6. **Deployment**: Deploy using our CI/CD pipeline

## Best Practices
- Follow established coding conventions
- Implement proper error handling and logging
- Use appropriate design patterns
- Ensure comprehensive test coverage
- Document all public APIs

## Troubleshooting
Common issues and their solutions:
- Performance: Check database queries and caching
- Errors: Review logs and error handling
- Configuration: Verify environment variables

## Conclusion
{feature} provides significant value when implemented correctly. Follow this guide for optimal results.
"""
    
    result = generate_technical_documentation("User Authentication")
    
    # Traditional assertions
    assert "User Authentication" in result
    assert "## Overview" in result  
    assert "Implementation Steps" in result
    
    # LLM evaluation with higher threshold
    tester = llm_eval(
        "The documentation should be comprehensive, well-structured, and technically accurate",
        threshold=0.85,  # Higher threshold for technical docs
        model="gpt-4o-mini"
    )
    tester.check(result, label="technical_documentation")


def test_error_message_quality(llm_eval):
    """Test error message quality across different scenarios."""
    
    def generate_error_message(error_type, context):
        messages = {
            "validation": {
                "form": "Please check the highlighted fields. Some required information is missing or invalid.",
                "api": "Request validation failed. Please verify your input parameters and try again.",
                "auth": "Authentication failed. Please check your credentials and ensure your account is active."
            },
            "system": {
                "network": "We're experiencing connectivity issues. Please check your internet connection and try again.",
                "server": "Our servers are temporarily unavailable. We're working to resolve this quickly.",
                "maintenance": "System maintenance in progress. Service will be restored shortly."
            },
            "user": {
                "permissions": "You don't have permission to access this resource. Contact your administrator if you need access.",
                "quota": "You've reached your usage limit. Upgrade your plan or wait until next month to continue.",
                "expired": "Your session has expired for security reasons. Please log in again to continue."
            }
        }
        return messages.get(error_type, {}).get(context, "An unexpected error occurred. Please try again.")
    
    # Create tester for error message quality
    error_tester = llm_eval("Error messages should be clear, helpful, and user-friendly")
    
    # Test different error scenarios
    validation_error = generate_error_message("validation", "form")
    assert len(validation_error) > 20  # Basic assertion
    error_tester.check(validation_error, label="validation_error")
    
    system_error = generate_error_message("system", "network")
    assert "connectivity" in system_error or "connection" in system_error
    error_tester.check(system_error, label="system_error")
    
    user_error = generate_error_message("user", "permissions")  
    assert "permission" in user_error.lower()
    error_tester.check(user_error, label="user_error")
    
    # Log summary of all error message evaluations
    error_tester.log_summary()


def test_multi_language_content(llm_eval):
    """Test content quality across different languages and styles."""
    
    def generate_welcome_message(language, style):
        messages = {
            "english": {
                "formal": "Welcome to our premium service. We are delighted to have you as our valued customer.",
                "casual": "Hey there! Welcome aboard - we're super excited to have you with us!",
                "professional": "Welcome to our platform. We look forward to supporting your business objectives."
            },
            "spanish": {
                "formal": "Bienvenido a nuestro servicio premium. Nos complace tenerle como nuestro valioso cliente.",
                "casual": "¡Hola! Bienvenido - estamos súper emocionados de tenerte con nosotros!",
                "professional": "Bienvenido a nuestra plataforma. Esperamos apoyar sus objetivos comerciales."
            }
        }
        return messages.get(language, {}).get(style, "Welcome!")
    
    # Test English content
    english_tester = llm_eval(
        "English content should be grammatically correct, appropriate for the intended style, and welcoming",
        threshold=0.8
    )
    
    formal_english = generate_welcome_message("english", "formal")
    assert "Welcome" in formal_english
    english_tester.check(formal_english, label="formal_english")
    
    casual_english = generate_welcome_message("english", "casual")
    assert "Welcome" in casual_english or "welcome" in casual_english
    english_tester.check(casual_english, label="casual_english")
    
    # Test Spanish content  
    spanish_tester = llm_eval(
        "Spanish content should be grammatically correct, culturally appropriate, and welcoming",
        threshold=0.75  # Slightly lower threshold for non-English
    )
    
    formal_spanish = generate_welcome_message("spanish", "formal")
    assert "Bienvenido" in formal_spanish
    spanish_tester.check(formal_spanish, label="formal_spanish")


def test_complex_data_analysis(llm_eval):
    """Test analysis and reporting of complex data scenarios."""
    
    def generate_sales_report(quarter, metrics):
        return f"""# Q{quarter} Sales Performance Report

## Executive Summary
This quarter showed strong performance across key metrics with notable improvements in customer acquisition and retention.

## Key Metrics
- Revenue: ${metrics['revenue']:,}
- New Customers: {metrics['new_customers']:,}
- Customer Retention: {metrics['retention']:.1%}
- Average Order Value: ${metrics['aov']:.2f}
- Conversion Rate: {metrics['conversion']:.2%}

## Performance Analysis
Revenue increased by {metrics.get('revenue_growth', 15):.1%} compared to the previous quarter, driven primarily by:
1. Improved product mix and pricing strategy
2. Enhanced customer experience initiatives  
3. Successful marketing campaigns targeting high-value segments

Customer acquisition exceeded targets with {metrics['new_customers']:,} new customers, representing a {metrics.get('customer_growth', 12):.1%} increase.

## Regional Breakdown
- North America: 45% of total revenue
- Europe: 30% of total revenue  
- Asia-Pacific: 20% of total revenue
- Other regions: 5% of total revenue

## Recommendations
1. Continue investment in high-performing marketing channels
2. Expand successful initiatives to underperforming regions
3. Focus on customer retention programs to maintain growth
4. Optimize pricing strategy based on market feedback

## Outlook
Based on current trends and pipeline analysis, we project continued growth in the next quarter with potential for 10-15% revenue increase.
"""
    
    # Sample metrics data
    sample_metrics = {
        'revenue': 2_500_000,
        'new_customers': 1_250,
        'retention': 0.92,
        'aov': 185.50,
        'conversion': 3.75,
        'revenue_growth': 18.5,
        'customer_growth': 15.2
    }
    
    report = generate_sales_report(3, sample_metrics)
    
    # Traditional assertions
    assert "Q3" in report
    assert "Revenue:" in report
    assert "2,500,000" in report
    
    # LLM evaluation for report quality
    report_tester = llm_eval(
        "The sales report should be professional, data-driven, well-structured, and provide actionable insights",
        threshold=0.8,
        model="gpt-4o-mini"
    )
    report_tester.check(report, label="sales_report_quality")


if __name__ == "__main__":
    print("Advanced pytest-LLM-Validate Examples")
    print("Run with: pytest examples/advanced_example.py -v -s")
    print("Make sure to set OPENAI_API_KEY environment variable") 