#pragma once

#include "imgui.h"      // IMGUI_IMPL_API

IMGUI_IMPL_API bool     ImGui_ImplQt_Init();
IMGUI_IMPL_API void     ImGui_ImplQt_Shutdown();
IMGUI_IMPL_API void     ImGui_ImplQt_NewFrame();
IMGUI_IMPL_API void     ImGui_ImplQt_RenderDrawData(ImDrawData* draw_data);

// Called by Init/NewFrame/Shutdown
IMGUI_IMPL_API bool     ImGui_ImplQt_CreateFontsTexture();
IMGUI_IMPL_API void     ImGui_ImplQt_DestroyFontsTexture();
IMGUI_IMPL_API bool     ImGui_ImplQt_CreateDeviceObjects();
IMGUI_IMPL_API void     ImGui_ImplQt_DestroyDeviceObjects();
