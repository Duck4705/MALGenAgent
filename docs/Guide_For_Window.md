# Hướng dẫn cài đặt cho Window
Nếu bạn muốn sử dụng chương trình này để chạy trên window vui lòng tải phiên bản window 10 hoặc 11 để chạy. Ram tối thiểu là 8 GB và 8 core CPU nếu như chạy local LLM, dung lượng đĩa từ 80 GB trở lên.   

Cài đặt MalGenAgent  
```bash
# Git clone repo
git clone https://github.com/your-org/MALGenAgent.git
cd MALGenAgent
# Create venv
python -m venv .venv
.venv/Scripts/activate  
# Install lib
pip install -r requirements.txt
```
Tạo file .env
```bash
echo -e "LANGCHAIN_API_KEY=\nLANGCHAIN_TRACING_V2=true" > .env
```
Tạo tài khoản langchain và lấy LANGCHAIN_API_KEY ở https://www.langchain.com/
```.env
LANGCHAIN_API_KEY="replace this by langchain api key"
LANGCHAIN_TRACING_V2=true
OLLAMA=false # true if use Ollama
BASE_URL= # If you do not specify a URL, the default OpenAI URL will be used.
MODEL=
API_KEY= 
```
Lưu ý rằng hiện tại dự MalGenAgent đang sử dụng ollama để sử dụng các llm open source. Bạn có thể thay đổi sang api openAI hoặc nền tảng khác qua link [docs](./docs/Guide_Change_Model_LLM.md)  này  
Tải Ollama và download model([các model ở nền tảng ollama để tham khảo](https://ollama.com/search))
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:7b
```
Khởi động chương trình 
```
langgraph dev
```
Bạn hãy nhập đầu vào của bạn tại dòng INPUT  
**Lưu ý:** Khi dùng trên nền tảng Window vui lòng tải [visual studio](https://visualstudio.microsoft.com/downloads/). Sau đó tick vào mục **Desktop development for C++**. Ở **Installation details** tick vào các mục sau:  
- MSVC v143
- C++ ATL for latest v143 build tools
- C++ profiling tools
- C++ Cmake tools for Windows
- Windows 11 SDK
- vcpkg package manager