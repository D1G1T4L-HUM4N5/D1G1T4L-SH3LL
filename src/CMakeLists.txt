add_library(lkcef SHARED
    lkcef.cpp
    browser_window.cpp
    # Add all other .cpp files you found in the src directory
    # For example:
    # some_other_file.cpp
    # another_file.cpp
)

# Add include directories if needed
target_include_directories(lkcef PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Link against necessary libraries
target_link_libraries(lkcef PRIVATE libcef_dll_wrapper ${CEF_STANDARD_LIBS})

# Add any other necessary configuration for lkcef