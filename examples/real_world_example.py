"""
Real-World Example for pytest-LLM-Validate

This example demonstrates practical usage scenarios:
- Content moderation system testing
- Customer service response evaluation
- Code review automation
- Documentation quality assessment

To run:
1. Set OpenAI API key: export OPENAI_API_KEY=your_key_here
2. Run: pytest examples/real_world_example.py -v -s
"""

import pytest


# =============================================================================
# CONTENT MODERATION SYSTEM
# =============================================================================

def test_content_moderation_system(llm_eval):
    """Test content moderation for user-generated content."""
    
    moderation_tester = llm_eval(
        "Content moderation should correctly identify harmful content while preserving legitimate content",
        threshold=0.9  # High threshold for safety-critical systems
    )
    
    def moderate_content(text):
        """Simple content moderation system."""
        harmful_patterns = [
            "spam", "scam", "hate speech", "harassment", 
            "violence", "illegal", "inappropriate"
        ]
        
        text_lower = text.lower()
        issues = [pattern for pattern in harmful_patterns if pattern in text_lower]
        
        if issues:
            return {
                "approved": False,
                "confidence": 0.95,
                "issues_found": issues,
                "recommendation": "Content flagged for manual review",
                "original_text": text[:50] + "..." if len(text) > 50 else text
            }
        
        return {
            "approved": True,
            "confidence": 0.85,
            "issues_found": [],
            "recommendation": "Content approved for publication",
            "original_text": text[:50] + "..." if len(text) > 50 else text
        }
    
    # Test various content scenarios
    legitimate_content = moderate_content(
        "This is a great product! I've been using it for months and highly recommend it to anyone looking for quality."
    )
    assert legitimate_content["approved"] == True
    moderation_tester.check(legitimate_content, label="legitimate_content")
    
    suspicious_content = moderate_content(
        "This is a total scam! Don't waste your money on this garbage product!"
    )
    assert suspicious_content["approved"] == False
    moderation_tester.check(suspicious_content, label="suspicious_content")
    
    neutral_content = moderate_content(
        "The weather today is partly cloudy with a chance of rain in the evening."
    )
    assert neutral_content["approved"] == True
    moderation_tester.check(neutral_content, label="neutral_content")


# =============================================================================
# CUSTOMER SERVICE AUTOMATION
# =============================================================================

def test_customer_service_responses(llm_eval):
    """Test automated customer service response generation."""
    
    def generate_customer_response(issue_type, customer_message, priority="normal"):
        """Generate customer service response based on issue type."""
        
        responses = {
            "billing": {
                "high": """Dear Valued Customer,

I sincerely apologize for the billing concern you've raised. I understand how frustrating billing issues can be, and I want to resolve this for you immediately.

I have escalated your case to our billing specialists who will:
1. Review your account within the next 2 hours
2. Contact you directly with a detailed explanation
3. Process any necessary adjustments or refunds

You can reach me directly at [email] or call our priority line at [phone].

Thank you for your patience and continued trust in our service.

Best regards,
Senior Customer Success Manager""",
                
                "normal": """Dear Customer,

Thank you for contacting us about your billing inquiry. I understand your concern and want to help resolve this matter promptly.

I will personally review your account and billing history. You can expect:
- A detailed response within 24 hours
- Clear explanation of any charges
- Resolution of any billing errors found

Please don't hesitate to reach out if you have additional questions.

Best regards,
Customer Support Team"""
            },
            
            "technical": {
                "high": """Dear Customer,

I apologize for the technical difficulties you're experiencing. I understand how disruptive this can be to your work.

I've immediately escalated your case to our senior technical team. Here's what we're doing:
1. Assigning a dedicated engineer to your case
2. Prioritizing a fix within the next 4 hours
3. Providing you with a temporary workaround if needed

I'll personally monitor this case and update you every 2 hours until resolved.

Technical Support Manager""",
                
                "normal": """Dear Customer,

Thank you for reporting this technical issue. I want to ensure we get this resolved for you quickly.

Our technical team will:
1. Investigate the issue within 24 hours
2. Provide a solution or workaround
3. Follow up to ensure everything is working properly

I've created ticket #12345 for your reference.

Best regards,
Technical Support Team"""
            }
        }
        
        response_template = responses.get(issue_type, {}).get(priority)
        if not response_template:
            return f"Thank you for contacting us. We've received your {issue_type} inquiry and will respond within 24 hours."
        
        return response_template
    
    # Test different scenarios
    high_priority_billing = generate_customer_response("billing", "My card was charged twice!", "high")
    
    # Traditional assertions
    assert "apologize" in high_priority_billing.lower()
    assert "escalated" in high_priority_billing.lower()
    
    # LLM evaluation
    service_tester = llm_eval(
        "Customer service responses should be empathetic, professional, and provide clear next steps",
        threshold=0.85
    )
    
    result_context = {
        "high_priority_billing": high_priority_billing,
        "scenario": "Customer charged twice - urgent billing issue",
        "expected_elements": ["apology", "immediate action", "escalation", "timeline", "direct contact"]
    }
    
    service_tester.check(result_context, label="billing_crisis_response")


# =============================================================================
# CODE REVIEW AUTOMATION
# =============================================================================

def test_automated_code_review(llm_eval):
    """Test automated code review functionality."""
    
    def review_code_snippet(code, language="python"):
        """Perform automated code review."""
        
        # Simulate code analysis
        issues = []
        suggestions = []
        
        if "password" in code.lower() and "print" in code.lower():
            issues.append({
                "type": "security",
                "severity": "high", 
                "message": "Potential password exposure in print statement",
                "line": "detected in code"
            })
        
        if "for i in range(len(" in code:
            issues.append({
                "type": "performance",
                "severity": "medium",
                "message": "Consider using enumerate() instead of range(len())",
                "suggestion": "for i, item in enumerate(items):"
            })
        
        if len([line for line in code.split('\n') if line.strip()]) > 50:
            issues.append({
                "type": "maintainability",
                "severity": "medium",
                "message": "Function is too long, consider breaking into smaller functions",
                "suggestion": "Split into multiple focused functions"
            })
        
        if '"""' not in code and 'def ' in code:
            suggestions.append({
                "type": "documentation",
                "message": "Consider adding docstring for better documentation"
            })
        
        return {
            "total_issues": len(issues),
            "security_issues": len([i for i in issues if i["type"] == "security"]),
            "performance_issues": len([i for i in issues if i["type"] == "performance"]),
            "maintainability_issues": len([i for i in issues if i["type"] == "maintainability"]),
            "issues": issues,
            "suggestions": suggestions,
            "overall_score": max(0, 100 - (len(issues) * 10)),
            "code_analyzed": code[:100] + "..." if len(code) > 100 else code
        }
    
    # Sample code with various issues
    problematic_code = '''
def process_user_data(users):
    password = "admin123"
    print(f"Using password: {password}")
    
    results = []
    for i in range(len(users)):
        user = users[i]
        # Process user data without proper validation
        processed = {
            "id": user.get("id"),
            "name": user.get("name"),
            "email": user.get("email")
        }
        results.append(processed)
    
    return results
'''
    
    review_result = review_code_snippet(problematic_code)
    
    # Traditional assertions
    assert review_result["total_issues"] > 0
    assert review_result["security_issues"] > 0
    
    # LLM evaluation
    code_review_tester = llm_eval(
        "Code review should identify issues with security, performance, maintainability, and best practices",
        threshold=0.8
    )
    
    code_review_tester.check(review_result, label="security_and_performance_review")


# =============================================================================
# API DOCUMENTATION TESTING
# =============================================================================

def test_api_documentation_quality(llm_eval):
    """Test API documentation for completeness and clarity."""
    
    def assess_api_documentation(endpoint_docs):
        """Assess API documentation quality."""
        return {
            "endpoint": endpoint_docs.get("endpoint"),
            "method": endpoint_docs.get("method"),
            "description": endpoint_docs.get("description"),
            "parameters": endpoint_docs.get("parameters", []),
            "example_request": endpoint_docs.get("example_request"),
            "example_response": endpoint_docs.get("example_response"),
            "error_codes": endpoint_docs.get("error_codes", [])
        }
    
    # Sample API documentation
    api_docs = {
        "endpoint": "/api/v1/users",
        "method": "POST",
        "description": "Create a new user account with the provided information. This endpoint validates input data and creates a user profile in the system.",
        "parameters": [
            {
                "name": "username",
                "type": "string",
                "required": True,
                "description": "Unique username for the account (3-50 characters, alphanumeric and underscores only)"
            },
            {
                "name": "email",
                "type": "string", 
                "required": True,
                "description": "Valid email address for account verification and communication"
            },
            {
                "name": "password",
                "type": "string",
                "required": True,
                "description": "Strong password (minimum 8 characters, must include uppercase, lowercase, number, and special character)"
            },
            {
                "name": "profile",
                "type": "object",
                "required": False,
                "description": "Optional profile information including first_name, last_name, and bio"
            }
        ],
        "example_request": {
            "username": "john_doe",
            "email": "john.doe@example.com", 
            "password": "SecurePass123!",
            "profile": {
                "first_name": "John",
                "last_name": "Doe",
                "bio": "Software developer passionate about clean code"
            }
        },
        "example_response": {
            "status": "success",
            "data": {
                "user_id": "usr_123456",
                "username": "john_doe",
                "email": "john.doe@example.com",
                "profile": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "bio": "Software developer passionate about clean code"
                },
                "created_at": "2024-01-15T10:30:00Z",
                "verification_status": "pending"
            }
        },
        "error_codes": [
            {"code": 400, "description": "Invalid input data or missing required fields"},
            {"code": 409, "description": "Username or email already exists"},
            {"code": 422, "description": "Password does not meet security requirements"},
            {"code": 500, "description": "Internal server error during user creation"}
        ]
    }
    
    documentation = assess_api_documentation(api_docs)
    
    # Traditional assertions
    assert documentation["endpoint"] == "/api/v1/users"
    assert documentation["method"] == "POST"
    assert len(documentation["parameters"]) > 0
    assert documentation["example_request"] is not None
    
    # LLM evaluation
    docs_tester = llm_eval(
        "API documentation should be comprehensive, clear, accurate, and include proper examples and error handling information",
        threshold=0.85
    )
    
    docs_tester.check(documentation, label="user_creation_api_docs")


# =============================================================================
# INTEGRATION TESTING
# =============================================================================

def test_complete_user_journey(llm_eval):
    """Test a complete user journey scenario."""
    
    def simulate_user_journey():
        """Simulate a complete user registration and onboarding flow."""
        journey = {
            "steps": [
                {
                    "step": "landing_page_visit",
                    "user_action": "User visits landing page",
                    "system_response": "Welcome! Discover our platform that helps businesses streamline their workflow and increase productivity.",
                    "user_experience": "Clear value proposition and compelling call-to-action"
                },
                {
                    "step": "registration_form",
                    "user_action": "User fills registration form",
                    "system_response": "Registration successful! Please check your email to verify your account.",
                    "user_experience": "Simple, intuitive form with helpful validation messages"
                },
                {
                    "step": "email_verification",
                    "user_action": "User clicks verification link",
                    "system_response": "Email verified successfully! Welcome to our platform. Let's get you started with a quick tour.",
                    "user_experience": "Smooth verification process with immediate next steps"
                },
                {
                    "step": "onboarding_tutorial",
                    "user_action": "User completes onboarding",
                    "system_response": "Great job! You're all set up. Here are some recommended actions to get the most out of our platform.",
                    "user_experience": "Interactive tutorial that teaches key features without overwhelming"
                },
                {
                    "step": "first_action",
                    "user_action": "User creates their first project",
                    "system_response": "Congratulations on creating your first project! You can now invite team members and start collaborating.",
                    "user_experience": "Achievement celebration with clear guidance for next steps"
                }
            ],
            "overall_satisfaction": "High - user successfully completed core actions with positive experience",
            "conversion_points": ["clear value prop", "easy registration", "helpful onboarding", "quick success"],
            "potential_improvements": ["add progress indicators", "provide more examples", "offer live chat support"]
        }
        
        return journey
    
    user_journey = simulate_user_journey()
    
    # Traditional assertions
    assert len(user_journey["steps"]) == 5
    assert "registration_form" in [step["step"] for step in user_journey["steps"]]
    assert user_journey["overall_satisfaction"].startswith("High")
    
    # LLM evaluation
    journey_tester = llm_eval(
        "The user journey should be smooth, intuitive, and provide clear value at each step with helpful guidance and positive user experience",
        threshold=0.8
    )
    
    journey_tester.check(user_journey, label="complete_user_onboarding")


if __name__ == "__main__":
    print("Real-World pytest-LLM-Validate Examples")
    print("=======================================")
    print("Scenarios covered:")
    print("- Content moderation system")
    print("- Customer service automation") 
    print("- Automated code review")
    print("- API documentation quality")
    print("- User journey testing")
    print()
    print("To run: pytest examples/real_world_example.py -v -s") 