from argparse import ArgumentParser, SUPPRESS
from bs4 import BeautifulSoup
import requests
from rich import print, box
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from paramiko import SSHClient, AutoAddPolicy

# Creates commandline arguments
parser = ArgumentParser(
    prog='otw',
    usage='%(prog)s [options]',
    description='OTW Bandit Tool. This can pull level information from the OTW site, and open an interactive SSH shell to the desired level',
    epilog='For optimal experience, please remember to put newly aquired password into the "password_dict" in the script file.'
    
)
parser.add_argument('-l', '--level', type=int, required=False, help = "bandit level. Required for -i")
parser.add_argument('-i', '--info',  required = False, action='store_true', help = "prints info for the level")
parser.add_argument('-p', '--passwords', required = False, action='store_true', help = "Prints a table of the current password repository")
args = parser.parse_args()

# Opens rich.console module to be used
console = Console()

# Dictionary of OTW Bandit passwords.
# Update this when you complete a level of automated access
password_dict = {
    '0' : "bandit0",
    '1' : "NH2SXQwcBdpmTEzi3bvBHMM9H66vVXjL",
    '2' : "rRGizSaX8Mk1RTb1CNQoXTcYZWU6lgzi"
}

def print_level_data(level):
    """
    Pulls level information from OverTheWire Bandit website and displays it in the console.

    @param level: The Bandit level to be queried
    @return: N/A. Output is printed to console.
    """

    # Pulls the webpage for the designated Bandit level
    url = f"https://overthewire.org/wargames/bandit/bandit{level}.html"
    webpage = requests.get(url).text

    # Parses the HTML into python-readable objects and selects the paragraph tags
    soup = BeautifulSoup(webpage, 'html.parser')
    p_tags = soup.find_all("p")

    # Cleans up the "Level Goal" and "Useful Command" sections into readable sections
    goal = [text.replace('\n', ' ') for text in p_tags[0].stripped_strings]

    cmds = []
    for text in p_tags[1].stripped_strings:
        text.replace('\n',' ')
        if text != ',':
            cmds.append(text)

    goal_string = " ".join(goal)
    cmd_string = ", ".join(cmds)


    # prints the output using rich to make it pretty
    print(Panel(f"""[green]
      ,----..            ,----,          .---.
     /   /   \         ,/   .`|         /. ./|
    /   .     :      ,`   .'  :     .--'.  ' ;
   .   /   ;.  \   ;    ;     /    /__./ \ : |
  .   ;   /  ` ; .'___,/    ,' .--'.  '   \' .
  ;   |  ; \ ; | |    :     | /___/ \ |    ' '
  |   :  | ; | ' ;    |.';  ; ;   \  \;      :
  .   |  ' ' ' : `----'  |  |  \   ;  `      |
  '   ;  \; /  |     '   :  ;   .   \    .\  ;
   \   \  ',  /      |   |  '    \   \   ' \ |
    ;   :    /       '   :  |     :   '  |--"
     \   \ .'        ;   |.'       \   \ ;
  www. `---` ver     '---' he       '---" ire.org[/green]

[green bold]===================== [red]Level {level}[/red] =====================[/green bold]

[yellow bold underline]Level Goal[/yellow bold underline]
[white]{goal_string}[/white]

[yellow bold underline]Useful Commands[/yellow bold underline]
[grey]{cmd_string}[/grey]
"""))


def connect_to_server(level, password):
    """
    Creates a SSH session with the Bandit server specified

    @param level: The Bandit level to be connected to
    @param password: String pulls from password dictionary
    @returns: N/A Output is printed to console. 
    """

    # Initiating variables
    hostname = "bandit.labs.overthewire.org"
    port = 2220
    user = f"bandit{level}"
    
    try:
        # Connected to SSH Server
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(hostname, port=port, username=user, password=password)

        # Print info for the level just logged into
        print_level_data(level)

        while True:
            try:
                # Receives user input to send to SSH Server
                cmd = console.input(f"[blue]{user} -> ")

                # command "exit" will disconnect from server
                if cmd == "exit": break

                # Save response from SSH Server
                stdin, stdout, stderr = client.exec_command(cmd)

                # Print out response from SSH Server
                print(stdout.read().decode())
            
            # If CTRL+C, disconnect from SSH Server
            except KeyboardInterrupt:
                break
    except Exception as err:
        print(str(err))


def list_passwords(passwords):
    """
    Prints a rich table with current passwords

    @param passwords: A dictionary of level:password pairs
    @return: N/A Output is printed to console. 
    """

    # Creates a table and it's columns
    table = Table(title="Bandit Password List", show_lines=True, box=box.ASCII_DOUBLE_HEAD)
    table.add_column("Level", justify="center", style="blue")
    table.add_column("Password", justify="center", style="blue")

    # Iterates over the password dictionary to create table rows
    for item in passwords:
        table.add_row(item, passwords[item])
    
    # Prints the table to the console
    console.print(table)


# If -i argument, just print out the level information
if args.info:
    print_level_data(args.level)
elif args.passwords:
    list_passwords(password_dict)
else:
    # If the level in console command exists in password_dict
    if str(args.level) in password_dict:
        # Connect using proper credentials
        connect_to_server(args.level, password_dict[str(args.level)])
    else:
        # Let the user know it doesn't exist.
        raise Exception("This password does not exist in the Dictionary...yet.")
