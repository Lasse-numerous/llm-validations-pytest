"""
Simple Example for pytest-LLM-Validate

This example shows the Fixture API in action.

To run:
1. Set OpenAI API key: export OPENAI_API_KEY=your_key_here
2. Run: pytest examples/simple_example.py -v
"""

import pytest


def test_greeting(llm_eval):
    """Test that generates a simple greeting."""
    def create_greeting(name):
        return f"Hello {name}, nice to meet you!"
    
    result = create_greeting("World")
    
    # Traditional assertion
    assert "World" in result
    assert "Hello" in result
    
    # LLM evaluation
    tester = llm_eval("The greeting should be polite and friendly")
    tester.check(result, label="greeting_politeness")


def test_email_generation(llm_eval):
    """Test email generation quality."""
    def generate_email(topic):
        return f"""Subject: Re: {topic}

Dear Customer,

Thank you for your email regarding {topic}. We appreciate you taking the time to contact us.

We have reviewed your request and will get back to you within 2 business days with a detailed response.

If you have any urgent concerns, please don't hesitate to call our support line.

Best regards,
Customer Service Team"""
    
    result = generate_email("Product Support")
    
    # Traditional assertions
    assert "Product Support" in result
    assert "Dear Customer" in result
    
    # LLM evaluation
    tester = llm_eval("The email should be professional and helpful")
    tester.check(result, label="email_quality")


def test_content_examples(llm_eval):
    """Test various content generation scenarios."""
    
    # Create different testers for different content types
    news_tester = llm_eval("News summaries should be informative and neutral")
    recipe_tester = llm_eval("Recipes should be clear and easy to follow")
    
    # Test news summary
    news_summary = "Technology stocks rose today following positive earnings reports from major companies. The tech sector gained 2.3% with particular strength in cloud computing and AI-related companies."
    
    assert "technology" in news_summary.lower()
    news_tester.check(news_summary, label="news_summary")
    
    # Test recipe content
    recipe = """Chocolate Chip Cookies

Ingredients:
- 2 cups all-purpose flour
- 1 cup butter, softened
- 3/4 cup brown sugar
- 1/2 cup white sugar
- 2 eggs
- 1 cup chocolate chips

Instructions:
1. Preheat oven to 375°F
2. Mix butter and sugars until creamy
3. Add eggs and mix well
4. Gradually add flour
5. Stir in chocolate chips
6. Drop spoonfuls on baking sheet
7. Bake 9-11 minutes until golden

Makes about 48 cookies."""
    
    assert "flour" in recipe
    assert "Instructions:" in recipe
    recipe_tester.check(recipe, label="recipe_clarity")


if __name__ == "__main__":
    print("Run with: pytest examples/simple_example.py -v -s") 