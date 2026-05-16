from dotenv import load_dotenv
import os
from anthropic import Anthropic

load_dotenv()  # reads .env file from current directory

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("❌ API key not found — check your .env file")
else:
    print(f"✅ Key loaded: {api_key[:12]}...{api_key[-4:]}")  # shows partial key only

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=50,
    messages=[{"role": "user", "content": "Say 'setup works' and nothing else."}]
)

print(f"✅ API response: {response.content[0].text}")
print(f"✅ Tokens used: {response.usage.input_tokens} in, {response.usage.output_tokens} out")
