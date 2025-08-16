#define UNICODE
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <Windows.h>
#include <dwmapi.h>
#include <string>
#include <vector>
#include <iostream>

#pragma comment(lib, "dwmapi.lib")

namespace py = pybind11;

// ---------------------- Utility Functions ----------------------

std::string hello_world() {
    return "Hello from C++ Desktop Capture Module!";
}

std::wstring to_wide(const std::string &input) {
    int size_needed = MultiByteToWideChar(CP_UTF8, 0, input.c_str(), -1, nullptr, 0);
    std::wstring wide(size_needed, 0);
    MultiByteToWideChar(CP_UTF8, 0, input.c_str(), -1, &wide[0], size_needed);
    return wide;
}

uintptr_t find_window(const std::string &title) {
    std::wstring wname = to_wide(title);
    HWND hwnd = FindWindowW(nullptr, wname.c_str());
    return reinterpret_cast<uintptr_t>(hwnd);
}

// ---------------------- DWM Logic ----------------------

HWND create_window(int width, int height) {
    const wchar_t CLASS_NAME[] = L"DWM_Thumbnail_Host";

    // register window class
    WNDCLASS wc = {};
    wc.lpfnWndProc = DefWindowProcW;
    wc.hInstance = GetModuleHandle(nullptr);
    wc.lpszClassName = CLASS_NAME;
    RegisterClass(&wc);

    // safe coordinates
    int screenWidth = GetSystemMetrics(SM_CXVIRTUALSCREEN);
    int screenHeight = GetSystemMetrics(SM_CYVIRTUALSCREEN);
    int screenLeft = GetSystemMetrics(SM_XVIRTUALSCREEN);
    int screenTop = GetSystemMetrics(SM_YVIRTUALSCREEN);

    // place window far beyond the virtual desktop bounds
    int safeX = screenLeft + screenWidth + 500;
    int safeY = screenTop + screenHeight + 500;

    // create hidden, non-activating, layered window
    HWND hwnd = CreateWindowExW(
        WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE, // Extended styles
        CLASS_NAME,
        L"DWM Thumbnail Host",
        WS_POPUP | WS_VISIBLE,  // no title bar, which is still visible for PrintWindow
        safeX, safeY,           // off-screen position
        width, height,
        nullptr, nullptr, wc.hInstance, nullptr
    );

    // make window fully transparent
    SetLayeredWindowAttributes(hwnd, 0, 0, LWA_ALPHA);

    // show it (required for PrintWindow)
    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);

    return hwnd;
}

bool is_thumbnail_available(HWND target, HWND destination, int width, int height) {
    HTHUMBNAIL thumb;
    HRESULT hr = DwmRegisterThumbnail(destination, target, &thumb);
    if (FAILED(hr)) {
        std::cerr << "DwmRegisterThumbnail failed: 0x" << std::hex << hr << std::endl;
        return false;
    }

    DWM_THUMBNAIL_PROPERTIES props{};
    props.dwFlags = DWM_TNP_VISIBLE | DWM_TNP_RECTDESTINATION;
    props.fVisible = TRUE;
    props.rcDestination = { 0, 0, width, height };

    DwmUpdateThumbnailProperties(thumb, &props);
    return true;
}

// ---------------------- Pybind11 Export ----------------------

PYBIND11_MODULE(screen_capture, m) {
    m.def("hello_world", &hello_world);
    m.def("find_window", &find_window);
    m.def("create_window", [](int width, int height) {
        return reinterpret_cast<uintptr_t>(create_window(width, height));
    });
    m.def("register_thumbnail", [](uintptr_t target, uintptr_t host, int width, int height) {
        return is_thumbnail_available(reinterpret_cast<HWND>(target), reinterpret_cast<HWND>(host), width, height);
    });
}