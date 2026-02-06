# import openai

# openai.api_key = "YOUR_API_KEY"   # keep in env variable later

# def generate_advisory(issue_type, details):
#     prompt = f"""
# You are a cloud optimization assistant.

# Issue Type: {issue_type}
# Details: {details}

# Explain:
# 1. What the issue is
# 2. Why it is a problem
# 3. What action is recommended

# Use simple language suitable for beginners.
# """

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.3
#     )

#     return response.choices[0].message["content"]
