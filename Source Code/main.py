from os import system
from time import sleep
system("python -m pip install -r requirements.txt")
print("If you seen an error under this message, restart the application.")
sleep(.75)
from website import Website

def main() -> None:
    website = Website()
    website.run()


if __name__ == "__main__":
    main()

# use the admin sidebar on all the pages, it looks better.
