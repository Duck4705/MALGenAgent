#include <winsock2.h>
#include <windows.h>
#include <shlwapi.h>
#include <wbemidl.h>
#include <winhttp.h>
#include <iostream>

#pragma comment(lib, "wbemuuid.lib")
#pragma comment(lib, "winhttp.lib")

int main() {
    // 1. In Hello World
    std::cout << "Hello from cross-compiled Windows program!" << std::endl;

    // 2. Dùng MessageBox từ user32.lib
    MessageBoxA(NULL, "Hello via MessageBox", "Test", MB_OK);

    // 3. Test Winsock2 (khởi tạo thôi, không kết nối)
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2,2), &wsaData) == 0) {
        std::cout << "Winsock initialized." << std::endl;
        WSACleanup();
    }

    // 4. Dùng hàm Shlwapi (PathFileExistsA)
    if (PathFileExistsA("C:\\Windows\\System32\\notepad.exe")) {
        std::cout << "Notepad exists!" << std::endl;
    }

    // 5. WinHTTP: chỉ khởi tạo session (không tải gì)
    HINTERNET hSession = WinHttpOpen(L"TestAgent/1.0",
                                     WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                                     WINHTTP_NO_PROXY_NAME,
                                     WINHTTP_NO_PROXY_BYPASS, 0);
    if (hSession) {
        std::cout << "WinHTTP session created." << std::endl;
        WinHttpCloseHandle(hSession);
    }

    // 6. COM khởi tạo/giải phóng (liên quan ole32, oleaut32, wbemuuid)
    HRESULT hr = CoInitializeEx(0, COINIT_MULTITHREADED);
    if (SUCCEEDED(hr)) {
        std::cout << "COM initialized successfully." << std::endl;
        CoUninitialize();
    }

    return 0;
}
