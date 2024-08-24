import subprocess
import shlex 

def main():
    prompt = "ccssh> "

    while True: 
        # display prompt and get user input 
        user_input = input(prompt).strip()

        # parse the input into command and arguments 
        command_parts = shlex.split(user_input)

        if not command_parts: 
            continue
        
        if command_parts[0].lower() == "exit":
            break 
        
        try: 
            # run the command and wait for it to complete 
            subprocess.run(command_parts, check = True)
        except subprocess.CalledProcessError as e: 
            print(f"Command failed with exit code {e.returncode}")
        except FileNotFoundError: 
            print(f"Command not found: {command_parts[0]}")
    
if __name__ == "__main__":
    main()


