import subprocess
import os
import hashlib
import shutil
from pathlib import Path

def ExecutableBuilder(type_file: str, language: str = "Python", code: str = ""):
    """
    Build Python code to executable using PyInstaller
    
    Args:
        type_file: Type of executable ("elf" for Linux)
        language: Programming language (currently only supports "Python")
        code: Python code to build into executable
    
    Returns:
        dict: Build result with status and output path
    """
    
    # Validate inputs
    if not code or not code.strip():
        return {"status": "error", "message": "code is required"}
    
    if language.lower() != "python":
        return {"status": "error", "message": f"Language '{language}' not supported. Only Python is supported."}
    
    if type_file.lower() != "elf":
        return {"status": "error", "message": f"Type '{type_file}' not supported. Only 'elf' is supported."}
    
    # Convert JSON dump format (\n) to actual newlines
    try:
        # Replace \n with actual newlines to format code properly
        formatted_code = code.replace('\\n', '\n')
        print(f"[ExecutableBuilder] Formatted code from JSON dump")
        
        code_bytes = formatted_code.encode('utf-8')
        code_hash = hashlib.md5(code_bytes).hexdigest()[:8]  # Use first 8 chars of MD5
        output_name = f"malware_{code_hash}"
        
        # Create tmp_file directory if it doesn't exist
        tmp_dir = Path("tmp_file")
        tmp_dir.mkdir(exist_ok=True)
        
        # Create temporary Python file in tmp_file directory
        temp_filename = tmp_dir / f"temp_{code_hash}.py"
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write(formatted_code)  # Use formatted code with proper newlines
        
        print(f"[ExecutableBuilder] Created temporary file: {temp_filename}")
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to create temporary file: {str(e)}"}
    
    # Build PyInstaller command for ELF
    cmd = [
        "pyinstaller", 
        "--onefile",           # Create single executable file
        "--name", output_name, # Output name
        "--clean",             # Clean cache
        "--noconfirm",         # Overwrite without asking
        str(temp_filename)     # Use temporary file (convert Path to string)
    ]
    
    try:
        print(f"[ExecutableBuilder] Building code -> {output_name} (ELF)")
        
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temporary file
        try:
            os.remove(temp_filename)
            print(f"[ExecutableBuilder] Removed temporary file: {temp_filename}")
        except:
            pass  # Don't fail if temp file cleanup fails
        
        if result.returncode == 0:
            # Check if output file exists in dist folder
            output_path = Path("dist") / output_name
            
            if output_path.exists():
                print(f"[ExecutableBuilder] ✅ Build successful! Executable saved to: {output_path}")
                
                # Only return simple status message for terminal
                return {"status": "success", "message": f"Executable built successfully: {output_name}"}
            else:
                return {"status": "error", "message": "Build completed but output file not found"}
        else:
            return {"status": "error", "message": f"PyInstaller failed: {result.stderr}"}
    
    except FileNotFoundError:
        return {"status": "error", "message": "PyInstaller not found. Install with: pip install pyinstaller"}
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
