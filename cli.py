from rich.console import Console
from rich.align import Align
from rich.rule import Rule
from rich.text import Text
from pyfiglet import Figlet
import argparse
import os
from commands.report import run_report

from commands.analyze import run_analyze
from commands.init import run_init
from commands.version import run_version

console = Console()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def professional_banner():
    clear_screen()

    f = Figlet(font="slant")
    ascii_art = f.renderText("Cloud Guardian")

    # Blue-Cyan gradient effect
    styled = Text()
    colors = ["bright_cyan", "cyan", "bright_blue"]

    for i, line in enumerate(ascii_art.split("\n")):
        styled.append(line + "\n", style=colors[i % len(colors)])

    console.print(styled)

    console.print(
        Align.center(
            "[bold bright_green]AI-Assisted Cloud Audit & Optimization Engine[/bold bright_green]"
        )
    )

    console.print(
        Align.center(
            "[cyan]Secure • Analyze • Optimize • Protect[/cyan]\n"
        )
    )

    console.print(Rule(style="bright_blue"))


def show_commands():
    console.print("\n[bold bright_cyan]Available Commands:[/bold bright_cyan]\n")

    console.print("  [cyan]init[/cyan]       Initialize configuration")
    console.print("  [cyan]analyze[/cyan]    Run full cloud audit")
    console.print("  [cyan]analyze --hardware-auth[/cyan]    Use ESP32 hardware vault for audit")
    console.print("  [cyan]fix[/cyan]        Remediate detected issues")
    console.print("  [cyan]report[/cyan]     Generate audit report")
    console.print("  [cyan]version[/cyan]    Show version info")
    console.print("  [cyan]help[/cyan]       Display help menu\n")

    console.print("[dim]Use 'cg <command>' to execute.[/dim]\n")


def main():
    parser = argparse.ArgumentParser(prog="cg", add_help=False)
    subparsers = parser.add_subparsers(dest="command")
    
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--format", choices=["json", "html"], default="json")

    subparsers.add_parser("init")
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument(
        "--hardware-auth",
        action="store_true",
        help="Use ESP32 hardware vault for AWS credentials"
    )
    subparsers.add_parser("version")
    subparsers.add_parser("help")
    subparsers.add_parser("change-password")

    args = parser.parse_args()

    if args.command == "init":
        run_init()
    elif args.command == "analyze":
        run_analyze(hardware_auth=args.hardware_auth)
    elif args.command == "change-password":
        from core.hardware.vault_client import VaultClient
        vault = VaultClient()
        vault.change_password()
    elif args.command == "version":
        run_version()
    elif args.command == "report":
        run_report(args.format)
    elif args.command == "help":
        professional_banner()
        show_commands()
    else:
        professional_banner()
        show_commands()


if __name__ == "__main__":
    main()