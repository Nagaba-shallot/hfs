class AIGenerationError(Exception):
    "Base class for every error this package raises."


class AINotConfiguredError(AIGenerationError):
    "No API key was provided."


class AITimeoutError(AIGenerationError):
    "The AI provider didn't respond in time."


class AIProviderError(AIGenerationError):
    "The AI provider itself returned an error."

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AIResponseFormatError(AIGenerationError):
    "The AI provider responded, but not in the shape we expected."