# Examples & Tutorials

Real-world examples demonstrating how to use pytest-LLM-Validate for different types of testing scenarios.

## Basic Examples

### 1. Testing Text Generation

```python
from numerous.pytest_llm_validate import llm_eval

class TestContentGeneration:
    """Examples of testing generated text content."""

    @llm_eval("Blog post should be engaging and informative")
    def test_blog_post_quality(self):
        """Test AI-generated blog content."""
        topic = "The Future of Web Development"
        post = generate_blog_post(topic)
        return post

    @llm_eval("Headlines should be attention-grabbing and clickable")
    def test_headline_generation(self):
        """Test headline generation for articles."""
        article_content = "AI is transforming the workplace..."
        headline = generate_headline(article_content)
        return headline

    @llm_eval("Product descriptions should highlight key benefits and features")
    def test_product_descriptions(self):
        """Test e-commerce product descriptions."""
        product = {
            "name": "Wireless Bluetooth Headphones",
            "features": ["noise-canceling", "30-hour battery", "quick charge"]
        }
        description = generate_product_description(product)
        return description
```

### 2. Testing API Response Quality

```python
def test_api_responses(llm_eval):
    """Test API responses for quality and helpfulness."""
    tester = llm_eval("API responses should be clear, actionable, and user-friendly")

    # Test different error scenarios
    error_404 = api_error_handler(404, "User not found")
    tester.check(error_404, label="not_found_error")

    error_400 = api_error_handler(400, "Invalid email format")
    tester.check(error_400, label="validation_error")

    error_500 = api_error_handler(500, "Database connection failed")
    tester.check(error_500, label="server_error")

    # Verify all error messages are helpful
    summary = tester.get_summary()
    assert summary["passed"] >= 2, "Most error messages should be user-friendly"
```

### 3. Testing Code Generation

```python
class TestCodeGeneration:
    """Examples of testing AI-generated code."""

    @llm_eval("Generated code should follow Python best practices and PEP 8")
    def test_function_generation(self):
        """Test AI-generated Python functions."""
        prompt = "Create a function to validate email addresses"
        code = generate_python_function(prompt)
        return code

    @llm_eval("SQL queries should be optimized and use proper syntax")
    def test_sql_generation(self):
        """Test AI-generated SQL queries."""
        requirement = "Find top 10 customers by total purchase amount"
        sql = generate_sql_query(requirement)
        return sql

    @llm_eval("API documentation should be comprehensive and include examples")
    def test_api_doc_generation(self):
        """Test AI-generated API documentation."""
        endpoint_info = {
            "method": "POST",
            "path": "/users",
            "params": ["name", "email", "age"]
        }
        docs = generate_api_documentation(endpoint_info)
        return docs
```

## Advanced Examples

### 4. Multi-Stage Testing with Context

```python
def test_customer_journey(llm_eval):
    """Test entire customer interaction flow."""
    # Create tester with context about customer service
    tester = llm_eval(
        "All customer interactions should be empathetic, professional, and solution-focused",
        context="customer_service",
        interaction_type="support_ticket"
    )

    # Simulate customer journey stages
    stages = [
        ("greeting", "Customer opens support ticket"),
        ("acknowledgment", "Agent acknowledges the issue"),
        ("investigation", "Agent investigates and asks clarifying questions"),
        ("solution", "Agent provides solution or workaround"),
        ("followup", "Agent follows up to ensure satisfaction")
    ]

    for stage, scenario in stages:
        response = customer_service_agent.respond(scenario)
        tester.check(response, label=stage, scenario=scenario)

    # Ensure the entire journey meets quality standards
    summary = tester.get_summary()
    assert summary["average_score"] >= 0.8, "Customer journey should be consistently high quality"
```

### 5. A/B Testing with LLM Evaluation

```python
def test_email_variants(llm_eval):
    """Compare different email variants using LLM evaluation."""
    tester_formal = llm_eval("Email should be professional and respectful")
    tester_casual = llm_eval("Email should be friendly and approachable")
    tester_urgent = llm_eval("Email should convey urgency while remaining polite")

    scenarios = [
        "payment_reminder",
        "welcome_new_user",
        "feature_announcement",
        "support_response"
    ]

    results = {}

    for scenario in scenarios:
        # Test different email styles
        formal_email = generate_email(scenario, style="formal")
        casual_email = generate_email(scenario, style="casual")
        urgent_email = generate_email(scenario, style="urgent")

        # Evaluate each variant
        tester_formal.check(formal_email, label=f"{scenario}_formal")
        tester_casual.check(casual_email, label=f"{scenario}_casual")
        tester_urgent.check(urgent_email, label=f"{scenario}_urgent")

        results[scenario] = {
            "formal": tester_formal.get_results()[-1].score,
            "casual": tester_casual.get_results()[-1].score,
            "urgent": tester_urgent.get_results()[-1].score
        }

    # Analyze which style works best for each scenario
    for scenario, scores in results.items():
        best_style = max(scores, key=scores.get)
        print(f"{scenario}: {best_style} style scored highest ({scores[best_style]:.2f})")
```

### 6. Testing with Domain-Specific Rules

```python
# Custom rule for medical content
@llm_eval(
    "Medical advice should be accurate, cautious, and recommend consulting professionals",
    rule="medical_content",  # Custom rule for medical domain
    threshold=0.9  # Higher threshold for medical content
)
def test_medical_content():
    """Test AI-generated medical information."""
    symptoms = ["headache", "fever", "fatigue"]
    advice = generate_medical_advice(symptoms)
    return advice

# Custom rule for financial advice
@llm_eval(
    "Financial advice should be balanced, include risk warnings, and avoid guarantees",
    rule="financial_advice",
    compliance_check=True
)
def test_financial_advice():
    """Test AI-generated financial recommendations."""
    user_profile = {"age": 35, "risk_tolerance": "moderate", "goal": "retirement"}
    advice = generate_investment_advice(user_profile)
    return advice
```

### 7. Testing Multilingual Content

```python
def test_multilingual_support(llm_eval):
    """Test content generation in multiple languages."""
    languages = ["en", "es", "fr", "de", "ja"]

    for lang in languages:
        tester = llm_eval(
            f"Content should be culturally appropriate and grammatically correct in {lang}",
            language=lang,
            cultural_context=True
        )

        # Test different content types in each language
        greeting = generate_greeting(lang)
        tester.check(greeting, label="greeting")

        apology = generate_apology(lang)
        tester.check(apology, label="apology")

        invitation = generate_invitation(lang)
        tester.check(invitation, label="invitation")

        # Verify quality standards for each language
        summary = tester.get_summary()
        assert summary["passed"] == 3, f"All {lang} content should meet quality standards"
```

### 8. Performance and Load Testing

```python
def test_content_generation_performance(llm_eval):
    """Test content generation under load."""
    import time
    import concurrent.futures

    tester = llm_eval("Generated content should maintain quality under load")

    def generate_and_check(batch_id):
        content = generate_content_batch(size=10)
        return [(item, f"batch_{batch_id}_item_{i}") for i, item in enumerate(content)]

    # Generate content in parallel batches
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(generate_and_check, i) for i in range(10)]

        for future in concurrent.futures.as_completed(futures):
            batch_results = future.result()
            for content, label in batch_results:
                tester.check(content, label=label)

    # Verify quality didn't degrade under load
    summary = tester.get_summary()
    assert summary["average_score"] >= 0.7, "Quality should be maintained under load"
    print(f"Processed {summary['total_checks']} items with {summary['average_score']:.2f} avg score")
```

## Integration Examples

### 9. Django/Flask Web Application Testing

```python
import pytest
from django.test import TestCase
from numerous.pytest_llm_validate import llm_eval

class TestWebAppResponses(TestCase):
    """Test web application responses with LLM evaluation."""

    @llm_eval("Error pages should be user-friendly and helpful")
    def test_404_page(self):
        """Test custom 404 error page."""
        response = self.client.get('/nonexistent-page/')
        return response.content.decode()

    @llm_eval("Contact form validation messages should be clear and actionable")
    def test_form_validation(self):
        """Test form validation messages."""
        response = self.client.post('/contact/', {
            'email': 'invalid-email',
            'message': ''
        })
        return response.context['form'].errors

    def test_user_notifications(self, llm_eval):
        """Test various user notification messages."""
        tester = llm_eval("Notifications should be clear, timely, and actionable")

        # Test different notification types
        notifications = [
            create_success_notification("Profile updated successfully"),
            create_warning_notification("Password will expire in 3 days"),
            create_error_notification("Payment failed - please update your card")
        ]

        for i, notification in enumerate(notifications):
            tester.check(notification, label=f"notification_{i}")
```

### 10. Data Processing Pipeline Testing

```python
def test_data_transformation_pipeline(llm_eval):
    """Test data processing outputs for quality and consistency."""
    tester = llm_eval(
        "Processed data should be clean, consistent, and properly formatted",
        domain="data_processing"
    )

    # Test different data transformation stages
    raw_data = load_sample_data()

    # Stage 1: Data cleaning
    cleaned_data = data_cleaning_pipeline(raw_data)
    tester.check(cleaned_data, label="cleaning_stage")

    # Stage 2: Data normalization
    normalized_data = data_normalization_pipeline(cleaned_data)
    tester.check(normalized_data, label="normalization_stage")

    # Stage 3: Data enrichment
    enriched_data = data_enrichment_pipeline(normalized_data)
    tester.check(enriched_data, label="enrichment_stage")

    # Verify overall pipeline quality
    summary = tester.get_summary()
    assert summary["passed"] == 3, "All pipeline stages should produce quality data"
```

### 11. Machine Learning Model Testing

```python
def test_ml_model_explanations(llm_eval):
    """Test ML model explanations and interpretability."""
    tester = llm_eval(
        "Model explanations should be understandable to non-technical users",
        audience="business_users",
        technical_level="beginner"
    )

    # Test explanations for different predictions
    test_cases = [
        {"prediction": "approve_loan", "confidence": 0.85},
        {"prediction": "reject_loan", "confidence": 0.92},
        {"prediction": "manual_review", "confidence": 0.65}
    ]

    for case in test_cases:
        explanation = model.explain_prediction(case)
        tester.check(
            explanation,
            label=f"explanation_{case['prediction']}",
            confidence=case["confidence"]
        )

    # Test feature importance explanations
    feature_importance = model.get_feature_importance()
    importance_explanation = explain_feature_importance(feature_importance)
    tester.check(importance_explanation, label="feature_importance")
```

### 12. Documentation Generation Testing

```python
class TestDocumentationGeneration:
    """Test AI-generated documentation quality."""

    @llm_eval("API documentation should be comprehensive and include practical examples")
    def test_api_docs(self):
        """Test generated API documentation."""
        api_spec = load_openapi_spec()
        docs = generate_api_documentation(api_spec)
        return docs

    @llm_eval("Code comments should explain the 'why' not just the 'what'")
    def test_code_comments(self):
        """Test AI-generated code comments."""
        code_snippet = """
        def complex_algorithm(data, threshold=0.5):
            filtered = [x for x in data if x.score > threshold]
            return sorted(filtered, key=lambda x: x.priority, reverse=True)
        """
        commented_code = add_intelligent_comments(code_snippet)
        return commented_code

    def test_tutorial_generation(self, llm_eval):
        """Test generated tutorial content."""
        tester = llm_eval(
            "Tutorials should be beginner-friendly with step-by-step instructions",
            target_audience="beginners",
            include_examples=True
        )

        topics = ["getting_started", "advanced_features", "troubleshooting"]

        for topic in topics:
            tutorial = generate_tutorial(topic)
            tester.check(tutorial, label=f"tutorial_{topic}")

        # Ensure all tutorials meet quality standards
        summary = tester.get_summary()
        assert summary["average_score"] >= 0.8, "Tutorials should be consistently high quality"
```

## Testing Patterns & Best Practices

### 13. Fixture-Based Test Organization

```python
import pytest

@pytest.fixture
def content_tester(llm_eval):
    """Reusable fixture for content quality testing."""
    return llm_eval(
        "Content should be engaging, accurate, and appropriate for the target audience",
        threshold=0.75
    )

@pytest.fixture
def technical_tester(llm_eval):
    """Reusable fixture for technical content testing."""
    return llm_eval(
        "Technical content should be accurate, complete, and well-explained",
        threshold=0.85,
        domain="technical"
    )

def test_blog_posts(content_tester):
    """Test blog post generation using shared fixture."""
    posts = generate_blog_posts(["AI", "Tech", "Business"])

    for i, post in enumerate(posts):
        content_tester.check(post, label=f"blog_post_{i}")

def test_technical_guides(technical_tester):
    """Test technical guide generation using shared fixture."""
    guides = generate_technical_guides(["API Setup", "Deployment", "Troubleshooting"])

    for i, guide in enumerate(guides):
        technical_tester.check(guide, label=f"guide_{i}")
```

### 14. Parameterized Testing

```python
@pytest.mark.parametrize("tone,threshold", [
    ("professional", 0.8),
    ("friendly", 0.7),
    ("urgent", 0.75),
    ("apologetic", 0.85)
])
def test_email_tones(llm_eval, tone, threshold):
    """Test email generation with different tones."""
    tester = llm_eval(
        f"Email should have a {tone} tone throughout",
        threshold=threshold,
        tone=tone
    )

    scenarios = ["complaint_response", "welcome_message", "follow_up"]

    for scenario in scenarios:
        email = generate_email(scenario, tone=tone)
        tester.check(email, label=f"{scenario}_{tone}")

@pytest.mark.parametrize("language,cultural_context", [
    ("en-US", "American business culture"),
    ("en-GB", "British business culture"),
    ("es-ES", "Spanish business culture"),
    ("ja-JP", "Japanese business culture")
])
def test_localized_content(llm_eval, language, cultural_context):
    """Test content localization for different cultures."""
    tester = llm_eval(
        f"Content should be appropriate for {cultural_context}",
        language=language,
        cultural_context=cultural_context
    )

    content = generate_localized_content(language)
    tester.check(content, label=f"localized_{language}")
```

### 15. Error and Edge Case Testing

```python
def test_error_handling_quality(llm_eval):
    """Test quality of error messages and edge case handling."""
    tester = llm_eval(
        "Error messages should be helpful, specific, and suggest solutions",
        scenario_type="error_handling"
    )

    # Test various error conditions
    error_scenarios = [
        ("invalid_input", lambda: process_data("invalid_format_data")),
        ("network_timeout", lambda: api_call_with_timeout(0.1)),
        ("permission_denied", lambda: access_restricted_resource()),
        ("resource_not_found", lambda: fetch_nonexistent_resource())
    ]

    for scenario_name, scenario_func in error_scenarios:
        try:
            scenario_func()
        except Exception as e:
            error_message = format_user_error(e)
            tester.check(error_message, label=scenario_name)

def test_edge_case_responses(llm_eval):
    """Test system behavior with edge cases."""
    tester = llm_eval(
        "System should handle edge cases gracefully with appropriate responses",
        edge_case_testing=True
    )

    edge_cases = [
        ("empty_input", ""),
        ("very_long_input", "x" * 10000),
        ("unicode_input", "Hello 🌍 世界 🚀"),
        ("malformed_json", '{"incomplete": json'),
        ("sql_injection_attempt", "'; DROP TABLE users; --")
    ]

    for case_name, test_input in edge_cases:
        response = handle_user_input(test_input)
        tester.check(response, label=case_name)
```

## Performance and Optimization Examples

### 16. Batch Processing with Deduplication

```python
def test_batch_processing_efficiency(llm_eval):
    """Demonstrate efficient batch testing with deduplication."""
    # Create multiple testers for different aspects
    quality_tester = llm_eval("Content should be high quality")
    format_tester = llm_eval("Content should be properly formatted")
    tone_tester = llm_eval("Content should have professional tone")

    # Generate test data (some duplicates to demonstrate deduplication)
    test_data = [
        "Hello, welcome to our service!",  # Duplicate
        "Thank you for your inquiry.",
        "Hello, welcome to our service!",  # Duplicate - will use cached result
        "We appreciate your business.",
        "Please let us know if you need help."
    ]

    # Test all aspects - duplicates will use cached results
    for i, content in enumerate(test_data):
        quality_tester.check(content, label=f"quality_{i}")
        format_tester.check(content, label=f"format_{i}")
        tone_tester.check(content, label=f"tone_{i}")

    # Print efficiency stats
    for name, tester in [("Quality", quality_tester), ("Format", format_tester), ("Tone", tone_tester)]:
        summary = tester.get_summary()
        print(f"{name}: {summary['total_checks']} checks, avg score: {summary['average_score']:.2f}")
```

This comprehensive examples document demonstrates real-world usage patterns, from basic text generation testing to complex multi-stage workflows, performance testing, and advanced integration scenarios. Each example includes practical code that can be adapted for specific use cases.
