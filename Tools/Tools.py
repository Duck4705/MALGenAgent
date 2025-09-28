import subprocess
import os
import hashlib
import shutil
from pathlib import Path

def ExecutableBuilder(type_file: str, language: str = "Python", code: list = None):
    """
    Build code to executable using PyInstaller (Python), g++ (C++) or validate bash scripts
    
    Args:
        type_file: Type of output ("elf" for Linux, "exe" for Windows, "bash" for Bash Script)
        language: Programming language ("Python", "C++", or "Bash Script")
        code: Source code as a list of strings (each string is one line of code)
    
    Returns:
        dict: Build result with status and output path
    """
    
    # Normalize inputs for consistency in comparisons
    language = language.lower()
    type_file = type_file.lower()
    
    # Validate code input
    if not code or not isinstance(code, list) or len(code) == 0:
        return {"status": "error", "message": "Code must be a non-empty list of strings"}
    
    # Validate language
    supported_languages = ["python", "c++", "bash script", "golang"]
    if language not in supported_languages:
        return {
            "status": "error", 
            "message": f"Language '{language}' not supported. Supported: {', '.join(supported_languages)}"
        }
    
    # Validate type_file based on language
    valid_types = {
        "python": ["elf", "exe"],
        "c++": ["elf", "exe"],
        "bash script": ["bash"],
        "golang": ["elf", "exe"]
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
                "output_name": f"malware_{code_hash}"
            },
            "c++": {
                "extension": ".cpp",
                "output_name": f"malware_{code_hash}" + (".exe" if type_file == "exe" else ".elf")
            },
            "bash script": {
                "extension": ".sh",
                "output_name": f"malware_{code_hash}.sh"
            },
            "golang": {
                "extension": ".go",
                "output_name": f"malware_{code_hash}" + (".exe" if type_file == "exe" else "")
            }
        }
        
        # Get configuration for current language
        config = file_config[language]
        
        # Create directories
        tmp_dir = Path("tmp_file")
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
        "python": Path("dist"),
        "c++": Path("dist_C++"),
        "bash script": Path("bash_script"),
        "golang": Path("dist_Go")
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
        build_dir = Path("build")
        if build_dir.exists():
            shutil.rmtree(build_dir, ignore_errors=True)
        
        # PyInstaller command for Python
        cmd = [
            "pyinstaller", 
            "--onefile",           # Create single executable file
            "--name", output_name, # Output name
            "--clean",             # Clean cache
            "--noconfirm",         # Overwrite without asking
            "--workpath", f"./build/{output_name}",  # Unique work path
            str(temp_filename)     # Input file path
        ]
        use_shell = False
        operation_type = "Building"
        
    elif language == "c++":
        # C++ compilation commands
        if type_file == "exe":
            # Windows MSVC compiler
            vcvars = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
            cmd = f'"{vcvars}" && cl.exe "{temp_filename}" /Fe:"{output_name}" /EHsc /O2 /MT /nologo /W3 user32.lib advapi32.lib kernel32.lib gdi32.lib shell32.lib ole32.lib oleaut32.lib comdlg32.lib rpcrt4.lib ws2_32.lib wininet.lib psapi.lib shlwapi.lib taskschd.lib wbemuuid.lib'
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
        
    elif language == "golang":
        # Golang build configuration
        # Create a unique directory for each build to avoid module conflicts
        build_dir = tmp_dir / f"go_build_{code_hash}"
        build_dir.mkdir(exist_ok=True)
        
        # Prepare output filename (with appropriate extension for Windows)
        out_flag = "-o"
        output_file = output_name
        
        # Go build command
        cmd = [
            "go", "build",
            "-v",               # Verbose: in package đang build
            "-x",               # In chi tiết các lệnh compile/link
            "-gcflags", "all=-N -l",   # Tắt tối ưu hoá/inlining để debug dễ hơn
            out_flag, output_file,
            str(temp_filename)
        ]

        
        use_shell = False
        operation_type = "Building"
        
    elif language == "bash script":
        # Check if shellcheck is available for validation
        try:
            check_result = subprocess.run(
                ["shellcheck", "--version"],
                capture_output=True, text=True, timeout=5
            )
            
            if check_result.returncode == 0:
                cmd = ["shellcheck", "--format=gcc", str(temp_filename)]
                print(f"[ExecutableBuilder] Found shellcheck {check_result.stdout.splitlines()[1] if check_result.stdout else ''}")
            else:
                cmd = ["true"]  # Skip validation
                print(f"[ExecutableBuilder] Shellcheck check failed, skipping validation")
        except FileNotFoundError:
            cmd = ["true"]  # Skip validation
            print(f"[ExecutableBuilder] Shellcheck not found, skipping validation")
            
        use_shell = False
        operation_type = "Validating"
        
    try:
        # Execute the build/validation command
        print(f"[ExecutableBuilder] {operation_type} {language} code -> {output_name}" + 
              (f" ({type_file.upper()})" if language != "bash script" else ""))
        
        # Run the appropriate command
        result = subprocess.run(cmd, shell=use_shell, capture_output=True, text=True)
        
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
                
            elif language == "bash script":
                # Process bash script - make executable and copy to output directory
                if not temp_filename.exists():
                    # Recreate if needed
                    with open(temp_filename, 'w', encoding='utf-8') as f:
                        f.write(formatted_code)
                
                # Set permissions and copy to final location
                final_path = output_dir / output_name
                os.chmod(str(temp_filename), 0o755)
                shutil.copy(str(temp_filename), str(final_path))
                os.chmod(str(final_path), 0o755)
                
                # Determine validation status for message
                validation_status = "validated and saved" if "shellcheck" in str(cmd) else "saved"
                print(f"[ExecutableBuilder] Bash script {validation_status} to: {final_path}")
                return {"status": "success", "message": f"{language} {validation_status} successfully: {output_name}"}
                
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
                    
            elif language == "golang":
                # Handle Go output - may need to move from current directory to dist_Go
                current_output = Path(output_name)
                if current_output.exists():
                    final_path = output_dir / output_name
                    shutil.move(str(current_output), str(final_path))
                    print(f"[ExecutableBuilder] Build successful! Executable moved to: {final_path}")
                    return {"status": "success", "message": f"{language} executable built successfully: {output_name}"}
                else:
                    return {"status": "error", "message": "Build completed but Go executable not found"}
        else:
            # Handle build/validation failures
            error_msg = result.stderr if result.stderr else result.stdout
            error_responses = {
                "python": f"PyInstaller failed: {error_msg}",
                "c++": f"Compilation failed: {error_msg}",
                "golang": f"Go build failed: {error_msg}",
                "bash script": f"{'Shellcheck validation' if 'shellcheck' in str(cmd) else 'Processing'} failed: {error_msg}"
            }
            return {"status": "error", "message": error_responses[language], "code": code}
    
    except FileNotFoundError as e:
        # Extract command that wasn't found
        cmd_name = str(e).split("'")[1] if "'" in str(e) else "Required command"
        
        # Installation instructions by command/language
        install_instructions = {
            "pyinstaller": "Install with: pip install pyinstaller",
            "g++": "Install with: sudo apt install g++",
            "x86_64-w64-mingw32-g++": "Install with: sudo apt install gcc-mingw-w64",
            "shellcheck": "Install with: sudo apt install shellcheck",
            "go": "Install with: sudo apt install golang"
        }
        
        # Handle bash script special case - save file even if tool is missing
        if language == "bash script":
            try:
                # Create output directory and setup file path
                output_dir.mkdir(exist_ok=True)
                final_path = output_dir / output_name
                
                # Recreate temp file if needed and copy to output location
                if not temp_filename.exists():
                    with open(temp_filename, 'w', encoding='utf-8') as f:
                        f.write(formatted_code)
                
                # Make executable and copy
                os.chmod(str(temp_filename), 0o755)
                shutil.copy(str(temp_filename), str(final_path))
                os.chmod(str(final_path), 0o755)
                
                # Log success
                print(f"[ExecutableBuilder] Script copied without validation to: {final_path}")
                return {"status": "success", "message": f"{language} saved without validation: {output_name}"}
            except Exception as inner_e:
                return {"status": "error", "message": f"Failed to save bash script: {str(inner_e)}"}
        
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
