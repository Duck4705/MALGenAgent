import subprocess
import os
import hashlib
import shutil
from pathlib import Path

def ExecutableBuilder(type_file: str, language: str = "Python", code: str = ""):
    """
    Build code to executable using PyInstaller (Python) or g++ (C++)
    
    Args:
        type_file: Type of executable ("elf" for Linux, "exe" for Windows)
        language: Programming language ("Python" or "C++")
        code: Source code to build into executable
    
    Returns:
        dict: Build result with status and output path
    """
    
    # Validate inputs
    if not code or not code.strip():
        return {"status": "error", "message": "code is required"}
    
    if language.lower() not in ["python", "c++"]:
        return {"status": "error", "message": f"Language '{language}' not supported. Supported: Python, C++"}
    
    if type_file.lower() not in ["elf", "exe"]:
        return {"status": "error", "message": f"Type '{type_file}' not supported. Supported: elf, exe"}
    
    # Convert JSON dump format (\n) to actual newlines
    try:
        # Replace \n with actual newlines to format code properly
        formatted_code = code.replace('\\n', '\n')
        print(f"[ExecutableBuilder] Formatted {language} code from JSON dump")
        
        code_bytes = formatted_code.encode('utf-8')
        code_hash = hashlib.md5(code_bytes).hexdigest()[:8]  # Use first 8 chars of MD5
        
        # Debug: Print code hash and preview
        print(f"[ExecutableBuilder] Code hash: {code_hash}")
        print(f"[ExecutableBuilder] Code preview: {formatted_code[:100]}...")
        
        # Create tmp_file directory if it doesn't exist
        tmp_dir = Path("tmp_file")
        tmp_dir.mkdir(exist_ok=True)
        
        # Create temporary file based on language
        if language.lower() == "python":
            temp_filename = tmp_dir / f"temp_{code_hash}.py"
            output_name = f"malware_{code_hash}"
        else:  # C++
            temp_filename = tmp_dir / f"temp_{code_hash}.cpp"
            if type_file.lower() == "exe":
                output_name = f"malware_{code_hash}.exe"
            else:
                output_name = f"malware_{code_hash}.elf"
        
        # Check if temp file already exists and remove it
        if temp_filename.exists():
            print(f"[ExecutableBuilder] Warning: Temp file {temp_filename} already exists, removing...")
            temp_filename.unlink()
        
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write(formatted_code)  # Use formatted code with proper newlines
        
        print(f"[ExecutableBuilder] Created temporary file: {temp_filename}")
        print(f"[ExecutableBuilder] File size: {temp_filename.stat().st_size} bytes")
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to create temporary file: {str(e)}"}
    
    # Build command based on language
    if language.lower() == "python":
        # Clean any previous build artifacts more aggressively
        build_dir = Path("build")
        if build_dir.exists():
            shutil.rmtree(build_dir, ignore_errors=True)
            print(f"[ExecutableBuilder] Cleaned build directory")
        
        # Build PyInstaller command for Python
        cmd = [
            "pyinstaller", 
            "--onefile",           # Create single executable file
            "--name", output_name, # Output name
            "--clean",             # Clean cache
            "--noconfirm",         # Overwrite without asking
            "--workpath", f"./build/{output_name}",  # Unique work path per build
            str(temp_filename)     # Use temporary file (convert Path to string)
        ]
    else:  # C++
        # Clean any existing C++ output files first
        current_output = Path(output_name)
        if current_output.exists():
            current_output.unlink()
            print(f"[ExecutableBuilder] Removed existing C++ output: {output_name}")
        
        # Also check and clean dist_C++ directory
        dist_cpp_dir = Path("dist_C++") 
        final_output_path = dist_cpp_dir / output_name
        if final_output_path.exists():
            final_output_path.unlink()
            print(f"[ExecutableBuilder] Removed existing C++ output from dist_C++: {output_name}")
        
        # Build g++ command for C++
        if type_file.lower() == "exe":
            # Build for Windows using mingw cross-compiler with Windows libraries
            cmd = [
                "x86_64-w64-mingw32-g++", 
                str(temp_filename), 
                "-o", output_name,
                "-lws2_32",      # Winsock2 library
                "-lwininet",     # WinINet library  
                "-ladvapi32",    # Advanced API library
                "-luser32",      # User32 library
                "-lkernel32",    # Kernel32 library
                "-static-libgcc", # Static linking for better compatibility
                "-static-libstdc++",
                "-lwininet",
                "-lpsapi",
                "-lshlwapi",
                "-lgdi32",
                "-lshell32",
                "-lole32",
                "-loleaut32",
                "-lcomdlg32",
                "-lrpcrt4",
                "-ltaskschd",
                "-lcomsupp",
                "-lole32",
                "-loleaut32"
            ]
        else:  # elf
            # Build for Linux using g++
            cmd = ["g++", str(temp_filename), "-o", output_name]
    
    try:
        print(f"[ExecutableBuilder] Building {language} code -> {output_name} ({type_file.upper()})")
        
        # Run the build command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temporary file
        try:
            os.remove(temp_filename)
            print(f"[ExecutableBuilder] Removed temporary file: {temp_filename}")
        except:
            pass  # Don't fail if temp file cleanup fails
        
        if result.returncode == 0:
            # Check if output file exists and move to appropriate folder
            if language.lower() == "python":
                # Python output goes to dist folder (handled by PyInstaller)
                output_path = Path("dist") / output_name
                if output_path.exists():
                    print(f"[ExecutableBuilder] Build successful! Executable saved to: {output_path}")
                    return {"status": "success", "message": f"{language} executable built successfully: {output_name}"}
                else:
                    return {"status": "error", "message": "Build completed but Python executable not found in dist folder"}
            else:
                # C++ output - check if file exists in current directory first
                current_output = Path(output_name)
                dist_cpp_dir = Path("dist_C++")
                
                # Create dist_C++ directory if it doesn't exist
                dist_cpp_dir.mkdir(exist_ok=True)
                
                if current_output.exists():
                    # Move to dist_C++ folder
                    final_path = dist_cpp_dir / output_name
                    try:
                        shutil.move(str(current_output), str(final_path))
                        print(f"[ExecutableBuilder] Build successful! Executable moved to: {final_path}")
                        return {"status": "success", "message": f"{language} executable built successfully: {output_name}"}
                    except Exception as e:
                        print(f"[ExecutableBuilder] Warning: Could not move file to dist_C++: {e}")
                        return {"status": "success", "message": f"{language} executable built successfully: {output_name}"}
                else:
                    return {"status": "error", "message": "Build completed but C++ executable not found"}
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            if language.lower() == "python":
                return {"status": "error", "message": f"PyInstaller failed: {error_msg}"}
            else:
                return {"status": "error", "message": f"g++ compilation failed: {error_msg}"}
    
    except FileNotFoundError as e:
        if language.lower() == "python":
            return {"status": "error", "message": "PyInstaller not found. Install with: pip install pyinstaller"}
        elif "x86_64-w64-mingw32-g++" in str(e):
            return {"status": "error", "message": "MinGW cross-compiler not found. Install with: sudo apt install gcc-mingw-w64"}
        else:
            return {"status": "error", "message": "g++ compiler not found. Install with: sudo apt install g++"}
    except Exception as e:
        # Clean up temporary file on error
        try:
            os.remove(temp_filename)
        except:
            pass
        return {"status": "error", "message": f"Build error: {str(e)}"}
 
def execute_command(command: str):
    """
    Execute any shell/terminal command and get the result.
    
    This tool allows you to run system commands like file operations,
    system info, network commands, and package management.
    
    Args:
        command: The shell command to execute as a string

    Returns:
        dict: Contains status (success/error) and message with output
    """
    
    if not command or not command.strip():
        return {
            "status": "error",
            "message": "Command cannot be empty"
        }

    try:
        print(f"[execute_command] Executing: {command}")
        
        # Handle sudo commands - automatically provide password
        if command.strip().startswith("sudo"):
            print("[execute_command] Detected sudo command - providing password automatically")
            # Use echo to pipe password to sudo -S
            modified_command = f"echo 'kali' | sudo -S {command[4:].strip()}"
            command = modified_command
        
        # Execute the command with safety measures
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=600,  # 10 minute timeout for package installation
            encoding='utf-8',
            errors='replace'  # Handle encoding errors gracefully
        )        # Format result - combine stdout and stderr if needed
        if result.returncode == 0:
            output = result.stdout.strip()
            if result.stderr.strip():
                output += f"\n{result.stderr.strip()}"
                
            print(f"[execute_command] Command completed successfully")
            return {
                "status": "success",
                "message": output if output else "Command executed successfully (no output)"
            }
        else:
            error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
            if not error_msg:
                error_msg = f"Command failed with return code {result.returncode}"
                
            print(f"[execute_command]  Command failed: {error_msg}")
            return {
                "status": "error",
                "message": error_msg
            }
        
    except subprocess.TimeoutExpired:
        print(f"[execute_command] Command timed out")
        return {
            "status": "error",
            "message": f"Command timed out after 10 minutes: {command}"
        }
    except Exception as e:
        print(f"[execute_command] Exception: {str(e)}")
        return {
            "status": "error", 
            "message": f"Command execution failed: {str(e)}"
        }
