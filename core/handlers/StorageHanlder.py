from pathlib import Path


async def init_directories():
    program_dirs = [
        'accounts/input',
        'accounts/spam-block',
        'accounts/unauthorized',
        'assets'

    ]

    for program_dir in program_dirs:
        try:
            Path(program_dir).mkdir(parents=True, exist_ok=True)
        except Exception as CreationDirEx:
            pass
