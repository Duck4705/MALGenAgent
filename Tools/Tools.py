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
        
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write(formatted_code)  # Use formatted code with proper newlines
        
        print(f"[ExecutableBuilder] Created temporary file: {temp_filename}")
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to create temporary file: {str(e)}"}
    
    # Build command based on language
    if language.lower() == "python":
        # Build PyInstaller command for Python
        cmd = [
            "pyinstaller", 
            "--onefile",           # Create single executable file
            "--name", output_name, # Output name
            "--clean",             # Clean cache
            "--noconfirm",         # Overwrite without asking
            str(temp_filename)     # Use temporary file (convert Path to string)
        ]
    else:  # C++
        # Build g++ command for C++
        if type_file.lower() == "exe":
            # Build for Windows using mingw cross-compiler
            cmd = ["x86_64-w64-mingw32-g++", str(temp_filename), "-o", output_name]
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
            # Check if output file exists
            if language.lower() == "python":
                # Python output goes to dist folder
                output_path = Path("dist") / output_name
            else:
                # C++ output goes to dist_C++ folder
                output_path = Path("dist_C++") / output_name

            if output_path.exists():
                print(f"[ExecutableBuilder] ✅ Build successful! Executable saved to: {output_path}")
                
                # Only return simple status message for terminal
                return {"status": "success", "message": f"{language} executable built successfully: {output_name}"}
            else:
                return {"status": "error", "message": "Build completed but output file not found"}
        else:
            # Get full error output for detailed analysis
            error_output = ""
            if result.stderr:
                error_output += result.stderr
            if result.stdout:
                error_output += f"\n{result.stdout}" if error_output else result.stdout
            
            if language.lower() == "python":
                return {"status": "error", "message": f"PyInstaller failed:\n{error_output}"}
            else:
                return {"status": "error", "message": f"g++ compilation failed:\n{error_output}"}
    
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
        print(f"[execute_command] 🔧 Executing: {command}")
        
        # Execute the command with safety measures
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=120,  # 2 minute timeout
            encoding='utf-8',
            errors='replace'  # Handle encoding errors gracefully
        )
        
        # Format result - combine stdout and stderr if needed
        if result.returncode == 0:
            output = result.stdout.strip()
            if result.stderr.strip():
                output += f"\n{result.stderr.strip()}"
                
            print(f"[execute_command] ✅ Command completed successfully")
            return {
                "status": "success",
                "message": output if output else "Command executed successfully (no output)"
            }
        else:
            error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
            if not error_msg:
                error_msg = f"Command failed with return code {result.returncode}"
                
            print(f"[execute_command] ❌ Command failed: {error_msg}")
            return {
                "status": "error",
                "message": error_msg
            }
        
    except subprocess.TimeoutExpired:
        print(f"[execute_command] ⏰ Command timed out")
        return {
            "status": "error",
            "message": f"Command timed out after 2 minutes: {command}"
        }
    except Exception as e:
        print(f"[execute_command] 💥 Exception: {str(e)}")
        return {
            "status": "error", 
            "message": f"Command execution failed: {str(e)}"
        }
