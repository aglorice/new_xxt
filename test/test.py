from rich.console import Console

console = Console(record=True)  # 设置 record=True

console.print("Hello, World!")

captured_output_value = console.export_text()
print("Captured Output:", captured_output_value)
