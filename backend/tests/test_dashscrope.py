import os
import dashscope


dashscope.api_key = os.getenv(
    "DASHSCOPE_API_KEY"
)

print("API key loaded")