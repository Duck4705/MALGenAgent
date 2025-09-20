# Hướng dẫn thiết lập .env

File .env mẫu: 
```.env
LANGCHAIN_API_KEY="replace this by langchain api key"
LANGCHAIN_TRACING_V2=true
OLLAMA=false # true if use Ollama
BASE_URL= # If you do not specify a URL, the default OpenAI URL will be used.
MODEL=
API_KEY= 
```
Các biến LANGCHAIN_API_KEY, LANGCHAIN_TRACING_V2 đã hướng dẫn thiết lập ở file [README.md](../README.md)  
Sẽ có 2 trường hợp sử dụng LLM:    
  
- Trường hợp sử dụng LLM từ nền tảng OLLAMA
- Trường hợp sử dụng LLM từ nền tảng thương mại hoặc self-host
  
TH1: Sử dụng Ollama  
Hãy thiết lập biến OLLAMA=true và chọn MODEL bạn muốn, các biến còn lại không thêm gì cả
```.env
LANGCHAIN_API_KEY="replace this by langchain api key"
LANGCHAIN_TRACING_V2=true
OLLAMA=true
BASE_URL= 
MODEL="qwen3b"
API_KEY= 
```  
TH2: Sử dụng nền tảng thương mại hoặc self-host
Nếu như bạn sử dụng model từ OpenAI thì chỉ cần thiết lập biến OLLAMA=false và điền API_KEY từ trang chủ OpenAI ví dụ như sau
```.env
LANGCHAIN_API_KEY="replace this by langchain api key"
LANGCHAIN_TRACING_V2=true
OLLAMA=false
BASE_URL= 
MODEL="gpt-4o"
API_KEY="your-key"
```  
Nếu bạn muốn sử dụng từ nền tảng thương mại khác hoặc self-host vui lòng thiết lập BASE_URL theo chuẩn của OpenAI ví dụ như BASE_URL=https://089b66ba64db.ngrok-free.app/v1 hoặc BASE_URL=https://api.deepseek.com/v1. Nếu như tự host thì không cần nhập API_KEY
```.env
LANGCHAIN_API_KEY="replace this by langchain api key"
LANGCHAIN_TRACING_V2=true
OLLAMA=false
BASE_URL=https://089b66ba64db.ngrok-free.app/v1 
MODEL="Qwen2.5-32B"
API_KEY=
``` 