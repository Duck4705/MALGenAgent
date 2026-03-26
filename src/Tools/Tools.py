import subprocess
import os
import hashlib
import shutil
from pathlib import Path


def ExecutableBuilder(type_file: str, language: str = "Python", code: list = None):
    """
    Build code to executable using PyInstaller (Windows and Linux Python), g++ (Linux C++), cl (Windows C++)
    Args:
        type_file: Type of output ("elf" for Linux, "exe" for Windows)
        language: Programming language ("Python", "C++")
        code: Source code as a list of strings (each string is one line of code)
    
    Returns:
        dict: Build result with status and output path
    """
    
    # Normalize inputs for consistency in comparisons
    language = language.lower()
    type_file = type_file.lower()
    
    # Resolve project root so build artifacts always stay at workspace root
    project_root = Path(__file__).resolve().parents[2]

    # Validate code input
    if not code or not isinstance(code, list) or len(code) == 0:
        return {"status": "error", "message": "Code must be a non-empty list of strings"}
    
    # Validate language
    supported_languages = ["python", "c++"]
    if language not in supported_languages:
        return {
            "status": "error", 
            "message": f"Language '{language}' not supported. Supported: {', '.join(supported_languages)}"
        }
    
    # Validate type_file based on language
    valid_types = {
        "python": ["elf", "exe"],
        "c++": ["elf", "exe"]
    }
    
    if type_file not in valid_types[language]:
        return {
            "status": "error",
            "message": f"Type '{type_file}' not supported for {language}. Supported: {', '.join(valid_types[language])}"
        }
    
    # File preparation section
    try:
        # Join the code lines with newlines
        formatted_code = '\n'.join(code)
        
        # Generate hash for unique filenames
        code_bytes = formatted_code.encode('utf-8')
        code_hash = hashlib.md5(code_bytes).hexdigest()[:8]  # Use first 8 chars of MD5
        
        # File extension and output configuration by language
        file_config = {
            "python": {
                "extension": ".py",
                "output_name": f"malwarePY_{code_hash}"
            },
            "c++": {
                "extension": ".cpp",
                "output_name": f"malwareCPP_{code_hash}" + (".exe" if type_file == "exe" else ".elf")
            }
        }
        
        # Get configuration for current language
        config = file_config[language]
        
        # Create directories
        tmp_dir = project_root / "tmp_file"
        tmp_dir.mkdir(exist_ok=True)
        
        # Setup temporary file path
        temp_filename = tmp_dir / f"temp_{code_hash}{config['extension']}"
        output_name = config['output_name']
        
        # Clean up existing file if needed
        if temp_filename.exists():
            temp_filename.unlink()
        
        # Write code to temporary file
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write(formatted_code)
        
        # Log file creation
        print(f"[ExecutableBuilder] Created {language} file ({temp_filename.stat().st_size} bytes): {temp_filename}")
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to create temporary file: {str(e)}"}
    
    # Build configuration and setup
    output_dirs = {
        "python": project_root / "dist_Python",
        "c++": project_root / "dist_C++"
    }
    
    # Create output directory if it doesn't exist
    output_dir = output_dirs[language]
    output_dir.mkdir(exist_ok=True)
    
    # Clean existing output files if they exist
    output_path = output_dir / output_name
    if output_path.exists():
        output_path.unlink()
        print(f"[ExecutableBuilder] Removed existing {language} output: {output_path}")
        
    # Configure build commands for each language
    if language == "python":
        # Clean any previous build artifacts
        build_dir = project_root / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir, ignore_errors=True)
        
        # PyInstaller command for Python
        cmd = [
            "pyinstaller", 
            "--onefile",           # Create single executable file
            "--name", output_name, # Output name
            "--clean",             # Clean cache
            "--noconfirm",         # Overwrite without asking
            "--workpath", str(build_dir / output_name),  # Unique work path
            str(temp_filename)     # Input file path
        ]
        use_shell = False
        operation_type = "Building"
        
    elif language == "c++":
        # C++ compilation commands
        if type_file == "exe":
            # Windows MSVC compiler
            vcvars = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
            cmd = f'"{vcvars}" && cl.exe "{temp_filename}" /Fe:"{output_name}" /EHsc /O2 /MT /nologo /W3 /sdl- /GS- /GL'
            use_shell = True
        else:
            # Linux g++ compiler
            cmd = [
                "g++", 
                str(temp_filename), 
                "-o", output_name,
                "-lcurl", "-lpthread", "-lssl", "-lcrypto", "-lz", 
                "-ldl", "-lrt", "-lm", "-lstdc++fs",
                "-static-libgcc", "-static-libstdc++"
            ]
            use_shell = False
        operation_type = "Building"
        
    
        
    try:
        # Execute the build/validation command
        print(f"[ExecutableBuilder] {operation_type} {language} code -> {output_name} ({type_file.upper()})")
        
        # Run the appropriate command
        result = subprocess.run(
            cmd,
            shell=use_shell,
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        # Clean up temporary file after processing
        try:
            os.remove(temp_filename)
            print(f"[ExecutableBuilder] Removed temporary file: {temp_filename}")
        except:
            pass
        
        # Process successful execution
        if result.returncode == 0:
            # Handle successful build/validation based on language
            if language == "python":
                # Check for Python executable in dist folder (PyInstaller output)
                py_output_path = output_dir / output_name
                exe_output_path = output_dir / f"{output_name}.exe"
                
                if py_output_path.exists():
                    final_path = py_output_path
                elif type_file == "exe" and exe_output_path.exists():
                    final_path = exe_output_path
                else:
                    return {"status": "error", "message": "Build completed but executable not found"}
                
                print(f"[ExecutableBuilder] Build successful! Executable saved to: {final_path}")
                return {"status": "success", "message": f"{language} executable built successfully: {final_path.name}"}
                
            elif language == "c++":
                # Handle C++ output - may need to move from current directory to dist_C++
                current_output = Path(output_name)
                if current_output.exists():
                    final_path = output_dir / output_name
                    shutil.move(str(current_output), str(final_path))
                    print(f"[ExecutableBuilder] Build successful! Executable moved to: {final_path}")
                    return {"status": "success", "message": f"{language} executable built successfully: {output_name}"}
                else:
                    return {"status": "error", "message": "Build completed but executable not found"}
                    
        else:
            # Handle build/validation failures
            error_msg = result.stderr if result.stderr else result.stdout
            error_responses = {
                "python": f"PyInstaller failed: {error_msg}",
                "c++": f"Compilation failed: {error_msg}"
            }
            return {"status": "error", "message": error_responses[language], "code": code}
    
    except FileNotFoundError as e:
        # Extract command that wasn't found
        cmd_name = str(e).split("'")[1] if "'" in str(e) else "Required command"
        
        # Installation instructions by command/language
        install_instructions = {
            "pyinstaller": "Install with: pip install pyinstaller",
            "g++": "Install with: sudo apt install g++",
            "x86_64-w64-mingw32-g++": "Install with: sudo apt install gcc-mingw-w64"
        }
        
        # For other languages, return appropriate error message
        for tool, instruction in install_instructions.items():
            if tool in str(e) or tool in cmd_name.lower():
                return {"status": "error", "message": f"{cmd_name} not found. {instruction}"}
        
        # Generic error if no specific tool identified
        return {"status": "error", "message": f"{cmd_name} not found. Please install the required tools for {language}"}
        
    except Exception as e:
        # General error handling - clean up and return error
        try:
            if 'temp_filename' in locals() and temp_filename.exists():
                os.remove(temp_filename)
        except:
            pass
            
        # Log and return error
        error_msg = str(e)
        print(f"[ExecutableBuilder] Error: {error_msg}")
        return {"status": "error", "message": f"Build process error: {error_msg}"}
