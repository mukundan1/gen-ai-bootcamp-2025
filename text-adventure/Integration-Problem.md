# Integration Problem

The problem faced while integrating the DeepSeek-R1 model with Ollama in the Text Adventure companion AI system.

## The Problem

When using DeepSeek-R1 with Ollama, we discovered two specific issues:

1. **Response Format Mismatch**: Even when requesting a non-streaming response (`stream: false`), the Ollama API returns streaming NDJSON (newline-delimited JSON) responses.

2. **Thinking Process Included**: The model includes its internal thinking process in `<think>...</think>` tags, which should not be shown to the end user.

## The Solution

Made some fixes to the `OllamaClient` class to properly handle DeepSeek-R1 responses:

1. **NDJSON Parsing**: Added support for parsing NDJSON responses by concatenating all response fragments.

2. **Thinking Tags Removal**: Added a function to remove the `<think>...</think>` tags and their contents from the response.

## Implementation Details

### Response Format Handling

```python
# Handle both regular JSON and streaming ndjson responses
content_type = response.headers.get('content-type', '')
response_text = await response.text()

if 'application/x-ndjson' in content_type:
    # Handle streaming response format
    json_lines = [line for line in response_text.strip().split('\n') if line.strip()]
    
    # Combine all response fragments
    complete_response = ""
    for line in json_lines:
        try:
            obj = json.loads(line)
            partial_response = obj.get("response", "")
            complete_response += partial_response
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON line: {e}")
    
    # Clean the response
    clean_response = self._remove_thinking_tags(complete_response)
    return clean_response
else:
    # Handle regular JSON response
    data = json.loads(response_text)
    response = data.get("response", "")
    clean_response = self._remove_thinking_tags(response)
    return clean_response
```

### Removing Thinking Tags

```python
def _remove_thinking_tags(self, text):
    """
    Remove <think>...</think> tags and their content from the response.
    
    This is specifically for models like DeepSeek-R1 that include their reasoning process
    in thinking tags that should not be shown to the user.
    """
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
```

## Testing the Integration

Created standalone integration tests in the `backend/tests/integration/tier2/` directory:

1. `test_ollama_simple.py`: A simple standalone test that validates basic connectivity and response processing.

2. `test_ollama_integration.py`: A more comprehensive test that integrates with the application code.

To run the tests:

```bash
cd backend/tests/integration/tier2
python3 test_ollama_simple.py
```

## DeepSeek-R1 Characteristics

- DeepSeek-R1 is a first-generation reasoning model with performance comparable to OpenAI-o1 with available sizes: 1.5B, 7B, 8B, 14B, 32B, 70B, and 671B
- The model is open-source and MIT licensed
- It shows its reasoning process in thinking tags, which can be helpful for debugging but should be removed for user-facing responses

## Troubleshooting

If you encounter issues with the DeepSeek-R1 model:

1. Ensure Ollama is running: `ollama serve`
2. Check if the model is installed: `ollama list`
3. Pull the model if needed: `ollama pull deepseek-r1:latest`
4. Run the integration tests to validate connectivity and response processing
5. Check the logs for any specific errors

## Additional Resources

- [DeepSeek-R1 on Ollama](https://ollama.com/library/deepseek-r1)
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [DeepSeek Platform Documentation](https://api-docs.deepseek.com/) 