from base64 import decode
import tiktoken

enc= tiktoken.encoding_for_model("gpt-4o")
text=  [13225, 1366, 357, 939, 641, 14603, 1229]
tokens= enc.decode(text)
print("Tokens: ", tokens)