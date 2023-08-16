import loguru

loguru.logger.add(
    "logs.log",
    format="{time} {message}"
)

def main():
    print(1/0)

try:
    main()
except Exception as e:
    print(e)
    loguru.logger.exception(e)


